FROM node:20-bullseye

WORKDIR /app
COPY package.json ./package.json
RUN npm install --omit=dev --no-audit --no-fund

COPY app.js ./app.js
COPY public ./public

EXPOSE 80
CMD ["node", "app.js"]
