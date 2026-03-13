# Guia de Uso do Alembic

O Alembic é a ferramenta oficial de migrações (migrations) para o SQLAlchemy. Ele permite versionar as alterações feitas na estrutura do banco de dados (tabelas, colunas, chaves estrangeiras, etc.) de forma segura e incremental.

Neste projeto, o Alembic já foi integrado e configurado para ler as credenciais do banco de dados dinamicamente a partir do seu arquivo `.env` e dos modelos importados no arquivo `alembic/env.py`.

## Comandos Essenciais

Certifique-se sempre de estar com o seu ambiente virtual ativado (`source .venv/bin/activate`) e estar na raiz do projeto (onde fica o arquivo `alembic.ini`) antes de rodar os comandos.

### 1. Criar uma nova migração (Autogenerate)
Sempre que você criar um novo **Model** ou **alterar** um Model existente (adicionar coluna, mudar tipo, etc.), você precisa gerar um script de migração. O Alembic compara seus Models com o estado atual do banco e gera o script automaticamente.

```bash
alembic revision --autogenerate -m "Descrição da sua alteração"
```
*Exemplo: `alembic revision --autogenerate -m "Criando a tabela users"`*
Isso criará um novo arquivo dentro da pasta `alembic/versions/`. **Recomendação:** Sempre abra esse arquivo gerado e revise-o para garantir que o Alembic detectou as alterações corretamente.

### 2. Aplicar migrações ao Banco de Dados (Upgrade)
O comando acima apenas cria o arquivo (o histórico). Para executar essas alterações no banco de dados de fato, execute:

```bash
alembic upgrade head
```
Este comando executa todos os scripts pendentes até a versão mais recente (`head`).

### 3. Desfazer uma migração (Downgrade)
Se você aplicou uma migração por engano e precisa reverter a estrutura do banco para o passo anterior, use:

```bash
alembic downgrade -1
```
*Observação: Você também pode usar um ID de hash específico em vez de `-1` para voltar para uma versão pontual.*

### 4. Ver o histórico completo
Para listar todas as migrações que já foram criadas:

```bash
alembic history
```

## Resumo do Fluxo de Trabalho (Workflow)

1. Crie ou modifique um arquivo de Model (ex: `app/database/models/user/user_model.py`).
2. Garanta que o Model está sendo importado dentro de `alembic/env.py` (caso seja um model novo).
3. Rode `alembic revision --autogenerate -m "Sua mensagem aqui"`.
4. Rode `alembic upgrade head` para aplicar as mudanças no banco.

## Importante sobre Ambientes (DEV, HML, PRD)
O script de `env.py` do Alembic está configurado para ler as variáveis `DB`, `USER`, `PASSWORD`, `HOST`, `PORT` e `DATABASE` definidas no seu `.env` através do `app.core.config.settings`. Lembre-se de apontar corretamente para o banco desejado antes de rodar o `upgrade`.
