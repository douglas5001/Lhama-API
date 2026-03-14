# Documentação: Integração com Redis (Cache e Persistência Volátil)

Nossa aplicação FastAPI conta com a integração nativa e 100% assíncrona ao **Redis**, um banco de dados in-memory focado em velocidade extrema. Ele é a principal ferramenta para escalarmos endpoints que não mudam de valor constantemente e são alvos de alto tráfego.

---

## 🏗️ 1. Onde ele vive na nossa Arquitetura?

O Redis está configurado para subir automaticamente junto com a aplicação via Docker, conforme definido no nosso `docker-compose.yml`. Não é necessária nenhuma instalação complexa no computador local caso esteja rodando pelo Docker.

**A conexão assíncrona foi encapsulada em um Singleton/Pool** para garantir performance. Você encontrará o gerenciador de conexões em:
📁 `app/database/connections/redis_connection.py`

### Como a Conexão Funciona:
Ao invés de conectar e desconectar do Redis em cada rota, nós instanciamos um `ConnectionPool` assíncrono durante a subida (na carga do módulo). Toda vez que você chama a função `get_redis()`, o python seleciona uma porta viva do Pool e se comunica sem gargalos através do Event Loop do FastAPI.

---

## ⚙️ 2. Variáveis de Ambiente

Para o Redis funcionar, ele se orienta pelo nosso arquivo `app/core/config.py`. As variáveis essenciais que devem existir no arquivo `.env` da raiz da API (e já estão mapeadas no Docker) são:

```ini
REDIS_HOST=localhost       # Local / Na nuvem ou "middleware_redis" dentro da rede Docker.
REDIS_PORT=6379            # Porta padrão mundial.
```

---

## 👩‍💻 3. Como usar o Cache nas suas Rotas (Exemplo Prático)

Desenvolvemos um componente amigável e puramente Async. Aqui está o padrão ouro para fazer cache de respostas pesadas (como extrações do Postgres ou consultas à rede externa) para não sobrecarregar sua API:

```python
import asyncio
from app.database.connections.redis_connection import get_redis

# ... dentro da sua rota async def:

async def buscar_relatorio_pesado():
    # 1. Pede uma conexão do Pool de Redis (instantâneo)
    redis_client = get_redis()
    
    # 2. Verifica se a chave do relatório já existe no cache do Redis
    dados_no_cache = await redis_client.get('chave_do_relatorio_financeiro')
    
    if dados_no_cache:
        # 3. SE EXISTIR: Retorne IMEDIATAMENTE.
        # Zero uso do PostgreSQL e Resposta em ~5 milissegundos
        return {"data": dados_no_cache, "status": "cache_hit"}
    
    # --- A PARTIR DAQUI: O CACHE ESTAVA VAZIO OU EXPIROU ---
    
    # 4. Geração do dado pesado/lento
    await asyncio.sleep(5)  # Simulando uma busca gigantesca no PostgreSQL
    novo_relatorio_gerado = "Planilha XYZ 2026..."
    
    # 5. Salva o resultado no Redis para as futuras requisições!
    # O comando 'setex' salva a chave ("chave_do_relatorio_financeiro")
    # passando quanto tempo ela VAI DURAR lá (Ex: 60 segundos).
    await redis_client.setex('chave_do_relatorio_financeiro', 60, novo_relatorio_gerado)
    
    return {"data": novo_relatorio_gerado, "status": "banco_de_dados"}
```

---

## 🛠️ 4. Evitando Erros no uso do Redis Assíncrono

Para manter sua API voando, lembre-se destas três regras ao implementar novas interações com a biblioteca do cache:

1. **A Magia do Await:** O cliente do `redis.asyncio` não retorna os valores brutos de cara. Ele devolve uma *Couroutine*. Você **precisa** usar a palavra `await` antes de qualquer comando (`get`, `set`, `setex`, `delete`). Se esquecer o `await`, o FastAPI pode retornar erro 500 no parser.
2. **Somente Strings (Serialização):** O Redis que instalamos com o `decode_responses=True` devolve sempre texto puro nativamente do Python (`str`). Se o seu cache for armazenar um *Dicionário/JSON* gigangesco, você precisa rodar `json.dumps(dicionario)` antes do `setex`, e ler com `json.loads(string)` depois do `get()`.
3. **Respeite o Tempo de Expiração (TTL):** Evite usar o comando `set()` ao infinito e além. Sempre prefira usar `setex(nome, tempo_em_segundos, valor)`. Se você deixar chaves eternas pra consultas que mudam, os usuários ficarão com os dados desatualizados presos em tela para sempre até derrubar a API.

---

## 🚀 5. Os 5 Padrões Avançados (Casos de Uso)

O arquivo `app/controllers/test/test_controller.py` possui 5 rotas implementadas para você testar na prática o verdadeiro poder do Redis. Experimente chamá-las no SwaggerUI:

### 1. Sistema de Cache Clássico (`GET /test-redis/cache`)
Salva resultados de operações pesadas por um tempo determinado. Se 1000 pessoas pedirem o relatório em 30 segundos, apenas a primeira espera os 5 segundos de Banco de Dados; as outras 999 recebem a resposta instantânea (`0.005s`) via cache.

### 2. Rate Limiting Avançado (`GET /test-redis/rate-limit`)
Bloqueia acessos abusivos (robôs ou ataques DDoS) usando o sistema rápido do Redis. O comando `incr` adiciona +1 ao IP do usuário. Se passar de 5 vezes no mesmo minuto estourando o limite, a rota levanta um erro 429 (Too Many Requests).

### 3. Fila de Tarefas (Mensageria com Listas) (`POST /test-redis/queue`)
FastAPI não deve ficar fazendo processamentos de horas na Thread principal. O Redis usa o comando `lpush` para enfileirar uma Tarefa (ex: gerar PDF) e a API devolve uma resposta amigável para a tela do usuário. Em background, um servidor "Worker" gasta a própria CPU lendo essa fila com `rpop` no seu próprio tempo sem travar o Event Loop.

### 4. Controle de Sessão de Usuário (DenyList) (`POST /test-redis/session/revoke`)
Ao usar JWT Tokens, nós não salvamos a sessão de ninguém no Postgres para ser rápidos (Stateless). Mas e quando o usuário clica em "Loggout" ou é hackeado? Nós gravamos a string daquele Token no Redis marcando como "Cancelado". A nossa dependência (`get_current_user`) passa a dar um rápido `.get(token)` ali em 1ms antes de aceitar autorização. Se existir, levanta um erro 401.

### 5. Leaderboard / Rankings em Tempo Real (`POST /test-redis/leaderboard`)
Ao usar a estrutura poderosa `Sorted Sets` do Redis (`zadd` e `zrevrange`), você adiciona a pontuação de jogadores/vendas na memória RAM e o Redis magicamente mantém um placar Global perfeitamente ordenado instantaneamente, sem precisar sobrecarregar a base de dados SQL com `ORDER BY DESC LIMIT 10`.
