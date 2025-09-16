# POC Action-Réaction

Ce projet est un POC (Proof of Concept) simple démontrant une interaction entre un frontend React et un backend Go.

## Structure du projet

- `backend/` : Serveur Go utilisant le framework Gin
- `frontend/` : Application React avec Tailwind CSS

## Fonctionnalités

- Page unique avec un titre et un bouton
- Lors du clic sur le bouton, une requête est envoyée au serveur backend
- Le serveur backend traite la demande et renvoie une réponse
- Le frontend affiche la réponse du serveur

## Prérequis

- Go (version 1.16+)
- Node.js (version 14+)
- npm (inclus avec Node.js)

## Installation

### Backend

```bash
cd backend
go mod download
```

### Frontend

```bash
cd frontend
npm install
```

## Démarrage

Vous pouvez démarrer les deux serveurs (backend et frontend) en utilisant le script `start.sh` :

```bash
./start.sh
```

Ou démarrer chaque serveur séparément :

### Backend

```bash
cd backend
go run main.go
```

Le serveur backend sera accessible à l'adresse `http://localhost:8080`.

### Frontend

```bash
cd frontend
npm start
```

L'application frontend sera accessible à l'adresse `http://localhost:3000`.

## API Endpoints

- `POST /api/trigger` : Déclenche une action sur le serveur
- `GET /api/health` : Vérifie l'état du serveur
