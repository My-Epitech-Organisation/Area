# Scripts de Linting Django

Ce dossier contient les scripts pour maintenir la qualité du code dans le backend Django du projet AREA.

## 📋 Contenu

- `lint-check.sh` - Script de vérification (lecture seule)
- `lint-fix.sh` - Script d'auto-correction
- `README.md` - Cette documentation

## 🚀 Installation

### 1. Installer les dépendances de développement

```bash
# Depuis le dossier backend/
pip install -r requirements-dev.txt
```

### 2. Vérifier la configuration

Les outils sont configurés via `pyproject.toml` dans le dossier backend.

## 🔧 Utilisation

### Vérification complète du code (lecture seule)

```bash
# Vérifier tout le projet
./scripts/lint-check.sh

# Vérifier un module spécifique
./scripts/lint-check.sh users/

# Vérifier un fichier spécifique
./scripts/lint-check.sh users/models.py
```

### Auto-correction du code

```bash
# Corriger tout le projet
./scripts/lint-fix.sh

# Corriger un module spécifique
./scripts/lint-fix.sh automations/

# Corriger un fichier spécifique
./scripts/lint-fix.sh users/views.py
```

## 🔍 Outils utilisés

### 🎨 Formatage automatique
- **Black** : Formatage du code Python (PEP 8)
- **isort** : Tri et organisation des imports

### 📏 Vérification de style
- **flake8** : Vérification du style et détection d'erreurs
  - Plugins : `flake8-django`, `flake8-bugbear`, `flake8-comprehensions`

### 🔍 Analyse statique

- **bandit** : Analyse de sécurité

## ⚙️ Configuration

### Exclusions automatiques
Les outils ignorent automatiquement :
- `migrations/` - Fichiers générés par Django
- `__pycache__/` - Cache Python
- `venv/` - Environnement virtuel
- `.mypy_cache/` - Cache mypy
- `reports/` - Rapports générés

### Paramètres principaux
- **Longueur de ligne** : 88 caractères (standard Black)
- **Version Python** : 3.13
- **Profil isort** : Compatible Black

## 🎯 Codes de retour

Le script `lint-check.sh` utilise des codes de retour binaires :

- `0` : Tout est conforme ✅
- `1` : Problèmes de formatage (auto-corrigeable) 🎨
- `2` : Problèmes de style (manuel) 📏
- `8` : Problèmes de sécurité (manuel) 🔒

Les codes peuvent se combiner (ex: `3` = formatage + style).

## 📊 Exemple de sortie

### Vérification réussie
```
🔍 Django Backend Code Quality Check
========================================
🐍 Activating virtual environment...
📂 Checking: .

🎨 Checking code formatting with Black...
✅ Black formatting: PASSED

📚 Checking import sorting with isort...
✅ Import sorting: PASSED

📏 Checking code style with flake8...
✅ Code style: PASSED

 Checking security with bandit...
✅ Security check: PASSED

========================================
🎉 All checks passed! Your code is clean.
```

### Vérification avec erreurs
```
❌ Black formatting: FAILED
Run './scripts/lint-fix.sh' to auto-format your code

❌ Import sorting: FAILED
Run './scripts/lint-fix.sh' to auto-sort your imports

❌ Code style: FAILED
Please fix the style issues reported above
```

## 🛠️ Dépannage

### Erreur : "Virtual environment not found"
```bash
# Créer et configurer le venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Erreur : "Development dependencies not found"
Le script installe automatiquement les dépendances manquantes.

### Performance lente sur gros projets
```bash
# Utiliser des chemins spécifiques
./scripts/lint-check.sh users/models.py
./scripts/lint-fix.sh automations/
```

## 🚀 Intégration IDE

### VS Code
Ajouter à `.vscode/settings.json` :
```json
{
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.linting.flake8Enabled": true
}
```

### PyCharm
1. File → Settings → Tools → External Tools
2. Ajouter les scripts comme outils externes

## 📝 Workflow recommandé

1. **Avant commit** :
   ```bash
   ./scripts/lint-fix.sh
   ./scripts/lint-check.sh
   ```

2. **Pendant développement** :
   ```bash
   # Auto-correction fréquente
   ./scripts/lint-fix.sh users/
   ```

3. **Avant push** :
   ```bash
   # Vérification complète
   ./scripts/lint-check.sh
   ```

## 🔄 Mise à jour

Pour mettre à jour les outils :
```bash
pip install -r requirements-dev.txt --upgrade
```

## 📚 Ressources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [bandit Documentation](https://bandit.readthedocs.io/)

## 🤝 Contribution

Lors d'ajout de nouveaux modules Django :
1. Ajouter le module à `known_first_party` dans `pyproject.toml`
2. Tester avec `./scripts/lint-check.sh nom_module/`
3. Ajuster les exclusions si nécessaire