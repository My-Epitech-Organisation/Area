# 📱 AREA Mobile Client (Flutter)

This folder contains the **Flutter mobile client** for the AREA project.
It runs on **Android** and **iOS**, and communicates with the backend via REST API.

---

## 🚀 Getting Started

### 1. Install Flutter
Follow the official guide: [Flutter Installation](https://docs.flutter.dev/get-started/install)

Make sure to:
- Add Flutter to your PATH
- Run `flutter doctor` to check for missing dependencies

```bash
flutter doctor -v
```

---

## 🛠️ Installation

### 1. Flutter Setup

Follow the official guide: [Flutter Installation](https://docs.flutter.dev/get-started/install)

Add Flutter to your PATH and verify:
```bash
flutter --version
```

### 2. Android Configuration

- Install [Android Studio](https://developer.android.com/studio)
- Open SDK Manager and install required SDKs
- Environment variables:
  ```bash
  export ANDROID_HOME=$HOME/Android/Sdk
  export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
  ```

### 3. iOS Configuration (macOS only)

- Install [Xcode](https://developer.apple.com/xcode/)
- Accept licenses:
  ```bash
  sudo xcode-select --install
  sudo xcodebuild -license accept
  ```
- Install CocoaPods:
  ```bash
  sudo gem install cocoapods
  ```

### 4. Run the Project

```bash
cd AREA/mobile
flutter pub get
flutter run
```

To run on a specific device:
```bash
flutter devices  # List available devices
flutter run -d <device_id>
```

---

## 🏗️ Architecture

### File Structure

```text
lib/
├── main.dart              # App entry point
├── home_page.dart         # Main page
├── widgets/               # Reusable widgets
│   └── counter_widget.dart
├── models/                # Data models (to be added)
├── services/              # API services (to be added)
└── utils/                 # Utilities (to be added)
```

### Key Features

- **Authentication**: User login
- **Applets**: Creation and management of automations
- **Services**: Integration with external APIs (Gmail, Discord, etc.)
- **Responsive UI**: Adaptive design for mobile

### Backend Communication

- API REST via `http` package
- Endpoints: `/auth`, `/applets`, `/services`
- Error handling and loading states management

---

## 🧪 Testing

### Unit Tests

```bash
flutter test
```

### Integration Tests

- Manual testing on emulator/simulator
- Verify features: login, applet creation, etc.

### Device Testing

- Android: Emulator or physical device
- iOS: Simulator or physical device (macOS required)

---

## 📦 Build and Deployment

### Build Android APK

```bash
flutter build apk --release
# Generated file: build/app/outputs/flutter-apk/app-release.apk
```

### Build iOS (macOS)

```bash
flutter build ios --release
# Open Xcode to archive and deploy
```

### Deployment

- **Play Store**: Use Google Play Console
- **App Store**: Use Xcode and App Store Connect

---

## 🛠️ Useful Commands

| Command | Description |
|----------|-------------|
| `flutter clean` | Clean project cache |
| `flutter pub get` | Download dependencies |
| `flutter analyze` | Static code analysis |
| `flutter run` | Run app in debug mode |
| `flutter build apk` | Build Android APK |
| `flutter build ios` | Build iOS app |
| `flutter devices` | List connected devices |
| `flutter emulators` | List available emulators |
| `flutter doctor` | Check environment |

---

## ⚠️ Common Issues

| Issue | Solution |
|----------|----------|
| ❌ Emulator not found | Check Android Studio/Xcode installation |
| ❌ CocoaPods errors | `cd ios && pod install` |
| ❌ Permissions | Check `ANDROID_HOME` and `PATH` variables |
| ❌ Build fails | `flutter clean && flutter pub get` |
| ❌ Hot Reload not working | Restart the app |

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/new-feature`
3. **Commit**: `git commit -m 'Add new feature'`
4. **Push**: `git push origin feature/new-feature`
5. **Open a PR**

### Guidelines

- Follow Dart/Flutter conventions
- Add tests for new features
- Update this README if necessary
- For dependencies: `flutter pub add <package>` then commit `pubspec.lock`

---

## 📄 License

This project is under MIT license. See [LICENSE](../LICENSE) for more details.

---

Developed with ❤️ in Flutter for Epitech AREA Project
