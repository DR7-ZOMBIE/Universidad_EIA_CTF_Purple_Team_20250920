FROM node:20-bullseye
WORKDIR /app

# openssl para generar llaves
RUN apt-get update && apt-get install -y --no-install-recommends openssl \
  && rm -rf /var/lib/apt/lists/*

# Dependencias
COPY package*.json ./
RUN npm install --omit=dev --no-audit --no-fund

# Código y assets
COPY app.js ./app.js
COPY views ./views
COPY public ./public

# Llaves (SP e IdP)
RUN mkdir -p certs public/certs && \
    openssl genrsa -out certs/sp_private.pem 2048 && \
    openssl rsa -in certs/sp_private.pem -pubout -out certs/sp_public.pem && \
    cp certs/sp_public.pem public/certs/sp_public.pem && \
    openssl genrsa -out certs/idp_private.pem 2048 && \
    openssl rsa -in certs/idp_private.pem -pubout -out certs/idp_public.pem && \
    cp certs/idp_public.pem public/certs/idp_public.pem

ENV NODE_ENV=production
ENV PORT=80
EXPOSE 80
CMD ["node", "app.js"]
