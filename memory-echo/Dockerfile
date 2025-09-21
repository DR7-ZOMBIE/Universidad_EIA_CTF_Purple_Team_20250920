FROM node:20-bullseye

# Python para generar la imagen de memoria en build
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Archivos de la app
COPY package.json ./package.json
RUN npm install --omit=dev --no-audit --no-fund

COPY app.js ./app.js
COPY public ./public
COPY tools ./tools
COPY artifacts/mem_gen.py ./artifacts/mem_gen.py

# Genera la imagen de memoria (pequeña ~6–8MB)
RUN mkdir -p artifacts \
 && python3 artifacts/mem_gen.py  artifacts/mem.raw

# Exponer mem.raw para descarga
# (no copiamos un binario enorme desde el host; se genera en build)
# Si aun así quieres fijarlo, puedes ADD, pero mantenerlo pequeño es mejor.

EXPOSE 80
CMD ["node", "app.js"]
