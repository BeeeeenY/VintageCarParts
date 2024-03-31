FROM node:18
WORKDIR /usr/src/app
COPY package*.json server.js ./
COPY views /usr/src/app/views
COPY static /usr/src/app/static
COPY ./serviceAccountKey.json ./
RUN npm install
EXPOSE 5009
CMD ["npm", "start"]