# Guia de Boas Práticas: Arquitetura Assíncrona no FastAPI

Ao migrar a aplicação para um ecossistema **100% Assíncrono** (FastAPI + AsyncPG + SQLAlchemy 2.0 Async), elevamos a performance do projeto ao "Padrão Ouro" da indústria, permitindo milhares de conexões simultâneas sem o uso excessivo de RAM ou CPU.

No entanto, o uso do `async/await` exige uma mudança de paradigma. Abaixo estão as **Três Regras de Ouro** para desenvolvedores que atuarão nesta base de código:

---

## 1. A Regra de Ouro: Nunca Bloqueie o Event Loop ("O Trava-Tudo")
Como milhares de requisições de clientes agora rodam em uma única Thread principal (o *Event Loop*), que reveza a vez entre elas, **nunca execute tarefas estritamente de CPU (pesadas) de forma síncrona dentro da rota**.

- ❌ **ERRO FATAL:** Se em uma rota `async def` você processar uma planilha de Excel de 1 milhão de linhas ou converter um vídeo (que leve 10 segundos de CPU), **NENHUM** outro usuário no mundo conseguirá acessar sua API durante esse tempo. A API inteira congela para todos.
- ✅ **A SOLUÇÃO:** O `async def` serve exclusivamente para "esperar tráfego de I/O" (ir ao Banco de Dados, acessar Discos ou consultar outras APIs na rede). 
  - Para processamentos pesados de matemática ou arquivos, utilize o `BackgroundTasks` nativo do FastAPI ou delegue para filas externas (como Celery + Redis).

---

## 2. Abandone Bibliotecas Síncronas Legadas
Muitos tutoriais na internet recomendam bibliotecas famosas para tarefas comuns. Se elas não suportam `asyncio`, elas vão travar a sua aplicação.

Um exemplo clássico é consumir APIs de terceiros (Correios, Google, Pagamentos).
- ❌ **Não use `requests`:** Se você usar `requests.get()` dentro de uma rota `async def`, a sua API vai parar e esperar o Google responder bloqueando o servidor inteiro.
- ✅ **Use `httpx`:** A partir de agora, prefira versões projetadas para o mundo assíncrono. No lugar do `requests`, use o `httpx` e aguarde a chamada de rede liberando o Event Loop:
  ```python
  # Jeito correto
  async with httpx.AsyncClient() as client:
      response = await client.get('https://api.exemplo.com')
  ```

---

## 3. O Efeito Dominó do \`await\`
O ecossistema assíncrono é contagioso de baixo para cima. Se o seu Repositório (que vai no Banco) é `async def`, isso cria uma reação em cadeia obrigatória.

- **A Cadeia:** O Service que chama o Repositório precisa usar o `await`, o que o obriga a virar `async def`. Por sua vez, o Controller que chama o Service também precisa usar `await` e virar `async def`.
- ⚠️ **O Perigo do Esquecimento:** Se você esquecer de digitar a palavra `await` antes de chamar uma função do banco de dados ou do serviço, o Python **NÃO** vai disparar uma exceção de quebra do sistema na hora. Em vez disso, ele retornará para você um objeto "Coroutine" não avaliado. Isso gera "bugs silenciosos" no fluxo de dados que são difíceis de rastrear.

**Resumo da obra:** Tudo que demorar (Rede ou Banco de Dados) deve ser antecedido por um `await`. Tudo que for processamento puro de CPU, construa de modo que seja processado nos bastidores, fora do caminho das requisições principais dos usuários.

## 5. Posso usar Loop For em arquiteturas Async?
Sim, você PODE usar `for` em funções assíncronas! O mito de que não se deve usar loops `for` no `asyncio` vem de uma confusão comum.

O problema não é o loop em si, mas sim **o que você faz de pesado dentro dele**.
- ✅ **Permitido:** Iterar sobre 1.000, 10.000 itens fazendo formatações simples de texto em segundos (CPU não percebe).
- ❌ **Proibido (O Terror do Event Loop):** Colocar um processamento que leve VÁRIOS SEGUNDOS reais preso num loop *síncrono* de imagem, conversão ou matemática pesada usando uma lib antiga (como Pandas ou NumPy bruto sem cuidado). Isso vai congelar todas as outras conexões do servidor.

Se precisar percorrer centenas de itens para inserir no Banco de Dados (onde envolve Rede):
- ✅ Use apenas o `await` normalmente dentro do for: `await repositorio.salvar(item)`
- ✅ (Avançado) Use o `asyncio.gather()` para disparar todas as inserções de uma vez só no banco!

## 6. Para que serve o `await` nas funções pesadas?
A palavra `await` é literalmente o maestro que impede o seu servidor de travar. Em português, ela significa "Aguarde".

Quando uma rota assíncrona bate de frente com uma operação de "I/O" (Input/Output), como ir até o PostgreSQL no outro lado de um cabo de rede, a leitura é extremamente lenta do ponto de vista do processador (microssegundos vs nanossegundos). 

Sem o `await`, o Python ficaria "congelado" nessa linha de código sentando e esperando a rede responder, impedindo qualquer outra pessoa no site de ser atendida.

O **`await`** diz ao Event Loop (o coração do FastAPI):
*"Mestre, eu vou buscar essa informação no banco e isso vai demorar um pouco. PODE IR ATENDER OUTRAS REQUISIÇÕES DE OUTRO CLIENTE enquanto eu não volto. Quando os dados chegarem da rede, me avise que eu continuo dessa linha em diante."*

Dessa forma, enquanto 1 cliente está "preso" no banco de dados (no `await`), a CPU única do seu servidor consegue atender 100.000 outros requests perfeitamente!

## 7. Preciso de Workers para o Redis ou testes de bloqueio (`asyncio.sleep`)?
Não! A beleza do `asyncio` e do Event Loop é justamente resolver o problema da lentidão **sem** precisar abrir vários Workers ou Threads.

O FastAPI, rodando com **1 único Worker** (uma única instância e 1 único núcleo de CPU), consegue lidar com dezenas de milhares de clientes que estão "pausados" esperando o banco de dados (`await db.execute`) ou esperando o tempo passar (`await asyncio.sleep()`).

- **Quando o Worker faz diferença?** Apenas se a sua aplicação receber **tantas** requisições simultâneas que a CPU atinja 100% de uso apenas tentando ler os arquivos JSON ou rotear o tráfego. Como servidores modernos costumam ter 2, 4 ou 8 núcleos de CPU, rodamos o Uvicorn com Múltiplos Workers (ex: `--workers 4`) para espalhar essa carga matemática entre os núcleos. O ganho é de capacidade bruta de I/O em rede e processamento puro, não de "pular bloqueios".
