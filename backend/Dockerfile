FROM python:3.12-slim

WORKDIR /app

# Instalar dependências de sistema necessárias (se houver, por exemplo para bcrypt/cffi)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas os requirements primeiro para usar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação
COPY ./app /app

# Expor a porta que o Uvicorn vai usar
EXPOSE 8000

# Comando para rodar a aplicação usando o diretório correto (/app já está no WORKDIR)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
