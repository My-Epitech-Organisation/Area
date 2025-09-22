FROM node:20
WORKDIR /app
COPY package*.json tsconfig.json ./
RUN npm install
COPY src ./src
EXPOSE 8080
CMD ["npm", "run", "dev"]
