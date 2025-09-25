FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
# Install deps; prefer ci when lockfile exists, else install
RUN if [ -f package-lock.json ]; then \
			npm ci; \
		else \
			npm install; \
		fi

COPY . .

# Expose apk files from volume at /apk via Next public folder mount (symlink)
RUN mkdir -p public && ln -s /apk public/apk || true \
	&& ln -s /apk/client.apk public/client.apk || true

EXPOSE 3000

CMD ["sh", "-c", "npm run dev -- -p 3000"]
