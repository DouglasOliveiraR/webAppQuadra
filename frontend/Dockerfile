# Stage 1: Build da aplicação React
FROM node:20-alpine AS build

WORKDIR /app

# Copiar os arquivos de dependência
COPY package.json package-lock.json ./

# Instalar dependências
RUN npm ci

# Copiar o restante do código
COPY . .

# Construir para produção
RUN npm run build

# Stage 2: Servir com NGINX
FROM nginx:alpine

# Copiar o build do estágio anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar a configuração customizada do NGINX
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expor a porta 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
