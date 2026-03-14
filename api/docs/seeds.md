# Database Seeding

Este documento descreve como o processo de popular o banco de dados (seeding) está estruturado na aplicação e como você pode executá-lo.

O objetivo das *seeds* é popular o banco de dados com dados iniciais ou essenciais para que o sistema funcione corretamente (como usuários administradores, permissões padrões, configurações globais, etc).

## Como executar as Seeds

Para rodar as seeds, basta executar o script `seed.py` na raiz do diretório `api`:

```bash
# Navegue até o diretório api (se ainda não estiver nele)
cd /caminho/para/Middleware-FastApi/api

# Execute o script usando o Python do seu ambiente virtual
python seed.py
```

Você deverá ver logs no console indicando o progresso:
```text
INFO:__main__:Starting database seeds...
INFO:__main__:Seeding user: admin@example.com
INFO:__main__:Admin user seeded successfully!
INFO:__main__:Database seeding completed.
```

## Dados Populados Atualmente

As seeds atuais da aplicação incluem:

### 1. Usuário Administrador (`seed_users`)
O arquivo responsável é `app/database/seeds/user_seed.py`.
Ele verifica se já existe um usuário cadastrado com o e-mail administrador e, caso não exista, cria um usuário padrão:

- **E-mail:** `admin@example.com`
- **Senha:** `adminpassword` (⚠️ Atenção: Para produção, garanta que seu repositório ou serviço utilize o *hash* antes de salvar no banco de dados)
- **Nome:** Admin User
- **Admin:** Sim (`is_admin=True`)
- **Status Ativo:** Sim (`is_active=True`)

Se o usuário já existir no banco, ele ignorará a criação para evitar duplicidades e erros.

## Adicionando novas Seeds

Se você precisar adicionar novos dados (ex: `roles`, `permissions`, `categories`), o processo é:

1. **Crie o arquivo da seed:**
   Crie uma função na pasta `app/database/seeds/` (ex: `app/database/seeds/role_seed.py`).
   
2. **Defina a lógica:**
   Construa as inserções no banco através do repositório da sua entidade (como feito em `UserRepository`). Lembre-se sempre de validar se os dados já existem antes de criar.

3. **Registre no `seed.py`:**
   Abra o arquivo `api/seed.py`, importe sua nova função de seed e a execute dentro do bloco `try`, logo abaixo de `seed_users(db)`:

```python
from app.database.seeds.role_seed import seed_roles

...
    try:
        # Run independent seeds
        seed_users(db)
        seed_roles(db) # Adicionado
```
