# AREA - Action-Réaction Application

Ce projet est une application complète de gestion d'utilisateurs implémentant le concept d'action-réaction, avec une API backend Go, une interface web React, et une application mobile React Native.

## Structure du projet

- `backend/` : Serveur Go utilisant le framework Gin et une base de données PostgreSQL
- `frontend/` : Application Web React avec Tailwind CSS
- `mobile/` : Application mobile React Native avec Expo
- `docker-compose.yml` : Configuration Docker pour la base de données PostgreSQL

## Fonctionnalités

- Gestion complète des utilisateurs (CRUD - Create, Read, Update, Delete)
- Interface web responsive avec Tailwind CSS
- Application mobile native pour Android et iOS
- API RESTful sécurisée
- Base de données PostgreSQL pour le stockage persistant

## Prérequis

### Pour le développement

- **Go** (version 1.18+)
- **Node.js** (version 16+)
- **npm** (version 8+) ou **yarn** (version 1.22+)
- **Docker** et **Docker Compose** (pour la base de données PostgreSQL)
- **Expo CLI** (pour le développement mobile) : `npm install -g expo-cli`
- **Git** (pour la gestion de versions)

### Pour le déploiement

- Serveur Linux avec Docker installé
- Accès aux ports 8080 (API), 3000 (Web), 19000-19006 (Mobile)

## Installation

### Base de données (PostgreSQL)

```bash
# Démarrer la base de données PostgreSQL
docker-compose up -d
```

### Backend (Go)

```bash
# Installer les dépendances
cd backend
go mod download

# Compiler le backend (optionnel)
go build -o area-server main.go
```

### Frontend (React)

```bash
# Installer les dépendances
cd frontend
npm install
```

### Mobile (React Native)

```bash
# Installer les dépendances
cd mobile
npm install --legacy-peer-deps
```

## Compilation et démarrage

### Backend

```bash
cd backend
# Mode développement
go run main.go

# Mode production
./area-server  # Si compilé précédemment
```

Le serveur backend sera accessible à l'adresse `http://localhost:8080`.

### Frontend

```bash
cd frontend
# Mode développement
npm start

# Compilation pour la production
npm run build
```

L'application frontend sera accessible à l'adresse `http://localhost:3000`.

### Mobile

```bash
cd mobile
# Démarrer le serveur de développement Expo
npx expo start

# Pour Android
npx expo start --android

# Pour iOS
npx expo start --ios

# Pour compiler en bundle APK/IPA
npx expo build:android  # Pour Android
npx expo build:ios      # Pour iOS (nécessite un compte Apple Developer)
```

## API Endpoints

### Gestion des utilisateurs

- `GET /api/users` : Récupérer tous les utilisateurs
- `GET /api/users/:id` : Récupérer un utilisateur spécifique
- `POST /api/users` : Créer un nouvel utilisateur
- `PUT /api/users/:id` : Mettre à jour un utilisateur existant
- `DELETE /api/users/:id` : Supprimer un utilisateur

### Statut du serveur

- `GET /api/health` : Vérifier l'état du serveur

## Technologies utilisées et analyse

### Stack technique

- **Backend**: Go avec le framework Gin
  - *Points positifs*: Performances exceptionnelles, faible empreinte mémoire, compilation statique
  - *Points négatifs*: Écosystème moins mature que Node.js, courbe d'apprentissage pour les développeurs JavaScript

- **Base de données**: PostgreSQL
  - *Points positifs*: Robuste, ACID compliant, extensible, excellent pour les données relationnelles
  - *Points négatifs*: Configuration initiale plus complexe qu'une BDD NoSQL, nécessite Docker

- **Frontend Web**: React avec Tailwind CSS
  - *Points positifs*: Grande flexibilité, écosystème riche, performances optimisées avec le virtual DOM
  - *Points négatifs*: Peut être complexe pour les débutants, nécessite une bonne compréhension de JSX

- **Frontend Mobile**: React Native avec Expo
  - *Points positifs*: Code partagé entre iOS et Android, développement rapide, hot reloading
  - *Points négatifs*: Dépendances parfois complexes à gérer, performances inférieures au natif pour certaines fonctionnalités avancées

### Avantages de cette architecture

1. **Séparation claire des responsabilités**: Backend, frontend et mobile sont indépendants
2. **Évolutivité horizontale**: Chaque composant peut être mis à l'échelle séparément
3. **Réutilisation du code**: Logique partagée entre le web et le mobile
4. **Performances optimisées**: Backend Go ultra-rapide, frontend React optimisé

### Défis et limitations

1. **Complexité de configuration**: Plusieurs technologies à maintenir
2. **Gestion des dépendances mobiles**: Les mises à jour d'Expo peuvent causer des incompatibilités
3. **CORS et sécurité**: Nécessite une configuration précise pour les communications cross-origin

## Bonnes pratiques de développement

1. Utiliser des variables d'environnement pour les configurations sensibles
2. Suivre une approche API-first pour assurer la compatibilité entre web et mobile
3. Implémenter des tests unitaires et d'intégration
4. Utiliser Docker pour garantir la cohérence des environnements

## Contribuer

1. Forker le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commiter vos changements (`git commit -m 'Add some amazing feature'`)
4. Pousser vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.
