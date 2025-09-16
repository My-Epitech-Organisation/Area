
# Zapier/Make POC Backend (Go)

API REST simple pour gérer des workflows et actions.

## Démarrage

```sh
cd zapier-poc-backend
go mod tidy
go run main.go
```

Ou via VS Code :

- Ouvre le dossier `zapier-poc-backend` dans VS Code
- Lance la tâche "Run Go Backend" (Terminal > Run Task)

## Endpoints

- `GET /workflows` : liste des workflows
- `POST /workflows` : crée un workflow (JSON: id, name, actions[])
- `GET /actions` : liste des actions disponibles
- `POST /workflows/:id/execute` : exécute un workflow (retourne la simulation d'exécution)
