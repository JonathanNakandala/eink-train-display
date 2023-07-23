FROM node

WORKDIR /usr/src/app

COPY package*.json ./


RUN npm install

COPY . .
RUN npm run build




EXPOSE 8927

CMD [ "npm", "run", "start" ]