FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Expose apk files from volume at /apk via Next public folder mount (symlink)
RUN mkdir -p public && ln -s /apk public/apk || true

EXPOSE 3000

CMD ["sh", "-c", "npm run dev -- -p 3000"]
