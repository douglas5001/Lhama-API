# Usa uma imagem oficial leve do Python (Versão >= 3.10 recomendada para FastAPI)
FROM python:3.14-slim

# Define variáveis de ambiente pro Python rodar otimizado no Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências de compilação essenciais (para bibliotecas como psycopg2/bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependência primeiro (Aproveita o cache do Docker)
COPY requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Uvicorn vai usar
EXPOSE 8080

# Copia todo o código fonte para dentro do container
COPY . .

# Comando final que inicia sua aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
