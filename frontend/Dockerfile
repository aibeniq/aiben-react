# simplified version that uses 'npm run dev', to avoid stringent error checking from a true Docker build
FROM node:20

WORKDIR /app

COPY package*.json ./

#force it to install vite...
ENV NODE_ENV=development

RUN npm install

COPY . .

EXPOSE 5173

CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0"]