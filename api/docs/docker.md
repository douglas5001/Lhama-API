# Docker & Containerização

Para facilitar a inicialização de todo o ecossistema do projeto (Banco de Dados + API do FastAPI), configuramos o Docker Compose.

O Compose provisiona automaticamente um contêiner oficial do `PostgreSQL` isolado e, em seguida, constrói e roda a FastAPI usando os logs e o código mapeados.

## 🚀 Como Iniciar

A partir da **RAIZ do projeto** (onde fica o arquivo `docker-compose.yml`, ou seja, a pasta `Middleware-FastApi` original), rode o comando abaixo:

```bash
docker-compose up --build
```
*Dica: Se você não quiser que o terminal fique "preso" aos logs, adicione `-d` no final para rodar em modo Daemon (em segundo plano).*

### O que o Docker fará debaixo dos panos?
1. Baixa a versão oficial mais leve do Postgres e sobe o banco de dados na porta 5432.
2. Injeta automaticamente suas variáveis do arquivo `api/.env` (DB_USER, PASSWORD, DATABASE) dentro do banco.
3. Constrói um contêiner Python 3.13 otimizado.
4. Instala todas as dependências mapeadas no arquivo `requirements.txt`.
5. Aponta o `HOST` de rede interno do Docker para o nosso contêiner do Postgres.
6. Mapeia a porta `8080` de volta para a sua máquina (localhost).
7. Sobe o Uvicorn monitorando as mudanças do código (hot-reload).

## Volumes
Foi configurado o espelhamento de dois volumes cruciais:
1. **O Banco de Dados:** Ele não será deletado se você matar os contêineres. Seus dados persistem dentro do volume oculto `postgres_data`.
2. **Sistema de Arquivos:** Todo o diretório `/api/` da sua máquina está espelhado no `/app/` do container. Isso quer dizer que se você salvar um arquivo no VS Code na sua máquina, o contêiner detectará e o `Uvicorn` reiniciará a aplicação instantaneamente. Mais do que isso, os arquivos da Loguru (`storage/logs`) salvos no contêiner aparecerão magicamente na sua máquina real! 

## 🔌 Desligando os Contêineres
Se quiser parar todos os contêineres de uma vez, vá na raiz do projeto e rode:
```bash
docker-compose down
```
*(Caso necessite apagar totalmente os bancos de dados criados pra começar do zeo, rode `docker-compose down -v` para destruir os volumes persistentes também).*
