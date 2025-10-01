# 📱 Mobile Client (Flutter)

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

To initialize a new Flutter project (if needed):
```bash
flutter create .
```

### 2. Android Setup
Install Android Studio from [here](https://developer.android.com/studio)

Open Android Studio and install the required SDKs and emulators via the SDK Manager.

Ensure environment variables are set:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

### 3. iOS Setup (macOS only)
Install Xcode from the App Store or [here](https://developer.apple.com/xcode/).

Accept licenses and install command line tools:

```bash
sudo xcode-select --install
sudo xcodebuild -license accept
```

Install CocoaPods (if not already installed):
```bash
sudo gem install cocoapods
```

### 4. Run the Project

Clone the repository and navigate to the mobile directory:
```bash
git clone <repository_url>
cd AREA/mobile
```

Run on Android emulator
```bash
flutter emulators --launch <emulator_id>
```

Run on iOS simulator (if macOS available)
```bash
open -a Simulator
```

```bash
flutter pub get
flutter run
# Or specify device:
flutter run -d <device_id>
```

## 🧪 Testing
- Unit tests: not required at this stage
- Manual tests:
    - Run on Android emulator
    - Run on iOS simulator (if macOS available)

## 🛠️ Common Commands
```bash
flutter clean               # Clean the project
flutter pub get            # Get dependencies
flutter analyze            # Analyze the code
flutter build apk          # Build Android APK
flutter build ios          # Build iOS app
flutter run                # Run the app
flutter devices            # List connected devices
flutter emulators         # List available emulators
flutter emulators --launch <emulator_id>  # Launch a specific emulator
flutter doctor -v          # Check environment setup
```

## ⚠️ Common Issues
❌ Emulator not found → Make sure Android Studio or Xcode is properly installed.

❌ CocoaPods errors on iOS → Run pod install in the ios directory.

❌ Permission issues → Check that environment variables are set correctly.

📖 Contributing
If you add a new dependency, run:

```bash
flutter pub get
```

and commit the updated `pubspec.lock`.

Update this `README.md` with any additional setup instructions if needed.
