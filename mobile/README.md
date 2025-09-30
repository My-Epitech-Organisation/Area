# 📱 AREA Mobile Client (Flutter)

[![Flutter](https://img.shields.io/badge/Flutter-3.0+-02569B?logo=flutter)](https://flutter.dev/)
[![Dart](https://img.shields.io/badge/Dart-3.0+-0175C2?logo=dart)](https://dart.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Le client mobile **Flutter** pour le projet **AREA** (Automation and Reaction Engine), une plateforme d'automatisation inspirée d'IFTTT.  
Cette app permet aux utilisateurs de créer des automatisations personnalisées en connectant des services (ex. : Gmail, Discord, etc.) via des applets.

L'app fonctionne sur **Android** et **iOS**, et communique avec le backend via une API REST.

---

## � Table des Matières
- [�🚀 Démarrage Rapide](#-démarrage-rapide)
- [📋 Prérequis](#-prérequis)
- [🛠️ Installation](#️-installation)
- [🏗️ Architecture](#️-architecture)
- [🧪 Tests](#-tests)
- [📦 Build et Déploiement](#-build-et-déploiement)
- [🛠️ Commandes Utiles](#️-commandes-utiles)
- [⚠️ Problèmes Courants](#️-problèmes-courants)
- [🤝 Contribution](#-contribution)
- [📄 Licence](#-licence)

---

## 🚀 Démarrage Rapide

1. **Clonez le repo** :
   ```bash
   git clone <repository_url>
   cd AREA/mobile
   ```

2. **Installez les dépendances** :
   ```bash
   flutter pub get
   ```

3. **Lancez sur un émulateur** :
   ```bash
   flutter run
   ```

   *(Assurez-vous qu'un émulateur Android ou iOS est lancé)*

---

## 📋 Prérequis

- **Flutter SDK** : Version 3.0+ ([Installation](https://docs.flutter.dev/get-started/install))
- **Dart SDK** : Inclus avec Flutter
- **Android Studio** (pour Android) ou **Xcode** (pour iOS)
- **Git** pour le versioning

Vérifiez votre setup :
```bash
flutter doctor -v
```

---

## 🛠️ Installation

### 1. Installer Flutter
Suivez le guide officiel : [Flutter Installation](https://docs.flutter.dev/get-started/install)

Ajoutez Flutter à votre PATH et vérifiez :
```bash
flutter --version
```

### 2. Configuration Android
- Installez [Android Studio](https://developer.android.com/studio)
- Ouvrez le SDK Manager et installez les SDKs requis
- Variables d'environnement :
  ```bash
  export ANDROID_HOME=$HOME/Android/Sdk
  export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
  ```

### 3. Configuration iOS (macOS uniquement)
- Installez [Xcode](https://developer.apple.com/xcode/)
- Acceptez les licences :
  ```bash
  sudo xcode-select --install
  sudo xcodebuild -license accept
  ```
- Installez CocoaPods :
  ```bash
  sudo gem install cocoapods
  ```

### 4. Lancer le Projet
```bash
cd AREA/mobile
flutter pub get
flutter run
```

Pour lancer sur un device spécifique :
```bash
flutter devices  # Liste des devices
flutter run -d <device_id>
```

---

## 🏗️ Architecture

### Structure des Fichiers
```
lib/
├── main.dart              # Point d'entrée de l'app
├── home_page.dart         # Page principale
├── widgets/               # Widgets réutilisables
│   └── counter_widget.dart
├── models/                # Modèles de données (à ajouter)
├── services/              # Services API (à ajouter)
└── utils/                 # Utilitaires (à ajouter)
```

### Fonctionnalités Clés
- **Authentification** : Connexion utilisateur
- **Applets** : Création et gestion d'automatisations
- **Services** : Intégration avec APIs externes (Gmail, Discord, etc.)
- **UI Responsive** : Design adaptatif pour mobile

### Communication avec le Backend
- API REST via `http` package
- Endpoints : `/auth`, `/applets`, `/services`
- Gestion des erreurs et états de chargement

---

## 🧪 Tests

### Tests Unitaires
```bash
flutter test
```

### Tests d'Intégration
- Tests manuels sur émulateur/simulateur
- Vérifiez les fonctionnalités : connexion, création d'applets, etc.

### Tests sur Devices
- Android : Émulateur ou device physique
- iOS : Simulateur ou device physique (macOS requis)

---

## � Build et Déploiement

### Build Android APK
```bash
flutter build apk --release
# Fichier généré : build/app/outputs/flutter-apk/app-release.apk
```

### Build iOS (macOS)
```bash
flutter build ios --release
# Ouvrez Xcode pour archiver et déployer
```

### Déploiement
- **Play Store** : Utilisez Google Play Console
- **App Store** : Utilisez Xcode et App Store Connect

---

## 🛠️ Commandes Utiles

| Commande | Description |
|----------|-------------|
| `flutter clean` | Nettoie le cache du projet |
| `flutter pub get` | Télécharge les dépendances |
| `flutter analyze` | Analyse statique du code |
| `flutter run` | Lance l'app en mode debug |
| `flutter build apk` | Build APK Android |
| `flutter build ios` | Build app iOS |
| `flutter devices` | Liste des devices connectés |
| `flutter emulators` | Liste des émulateurs |
| `flutter doctor` | Vérifie l'environnement |

---

## ⚠️ Problèmes Courants

| Problème | Solution |
|----------|----------|
| ❌ Émulateur non trouvé | Vérifiez Android Studio/Xcode installé |
| ❌ Erreurs CocoaPods | `cd ios && pod install` |
| ❌ Permissions | Vérifiez variables `ANDROID_HOME` et `PATH` |
| ❌ Build échoue | `flutter clean && flutter pub get` |
| ❌ Hot Reload ne marche pas | Redémarrez l'app |

---

## 🤝 Contribution

1. **Fork** le repo
2. **Créez une branche** : `git checkout -b feature/nouvelle-fonction`
3. **Commitez** : `git commit -m 'Ajout nouvelle fonctionnalité'`
4. **Push** : `git push origin feature/nouvelle-fonction`
5. **Ouvrez une PR**

### Guidelines
- Suivez les conventions Dart/Flutter
- Ajoutez des tests pour nouvelles fonctionnalités
- Mettez à jour ce README si nécessaire
- Pour dépendances : `flutter pub add <package>` puis commit `pubspec.lock`

---

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](../LICENSE) pour plus de détails.

---

*Développé avec ❤️ en Flutter pour Epitech AREA Project*
