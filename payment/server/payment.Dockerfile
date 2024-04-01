FROM node:18

WORKDIR /usr/src/app

COPY package*.json server.js ./
COPY swagger.yaml ./
COPY .env ./
RUN npm install

EXPOSE 3000

CMD ["npm", "run", "devStart"]