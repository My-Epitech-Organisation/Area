FROM ubuntu:22.04

# Dépendances système
RUN apt-get update && apt-get install -y \
    curl git unzip xz-utils zip libglu1-mesa openjdk-17-jdk wget \
    && rm -rf /var/lib/apt/lists/*

# Installer Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

RUN mkdir -p $ANDROID_HOME/cmdline-tools \
    && wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O /tmp/cmdline-tools.zip \
    && unzip /tmp/cmdline-tools.zip -d $ANDROID_HOME/cmdline-tools \
    && mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest \
    && rm /tmp/cmdline-tools.zip

RUN yes | sdkmanager --licenses
RUN sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"

# Installer Flutter
RUN git clone https://github.com/flutter/flutter.git -b stable /flutter
ENV PATH="/flutter/bin:$PATH"

# Préparer Flutter
RUN flutter doctor
RUN flutter precache

# Copier code et builder APK
WORKDIR /app
COPY . .
RUN flutter pub get
# RUN flutter build apk --release -t lib/main.dart
RUN flutter build apk --release -t lib/main.dart --android-skip-build-dependency-validation


# Placer APK dans le volume partagé
RUN mkdir -p /shared && cp build/app/outputs/flutter-apk/app-release.apk /shared/client.apk