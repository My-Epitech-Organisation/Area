# Dockerfile pour le backend Go (Gin + SQLite + MongoDB)
FROM golang:1.21-alpine

WORKDIR /app

# Installe les dépendances nécessaires
RUN apk add --no-cache git sqlite

# Copie le code source
COPY . .

# Installe les modules Go
RUN go mod tidy

# Compile l'application
RUN go build -o backend main.go

# Expose le port utilisé par Gin
EXPOSE 8080

# Démarre le backend
CMD ["/app/backend"]
