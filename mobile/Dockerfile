FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl git unzip xz-utils zip libglu1-mesa openjdk-17-jdk wget \
    && rm -rf /var/lib/apt/lists/*

ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH

RUN mkdir -p $ANDROID_HOME/cmdline-tools \
    && wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O /tmp/cmdline-tools.zip \
    && unzip /tmp/cmdline-tools.zip -d $ANDROID_HOME/cmdline-tools \
    && mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest \
    && rm /tmp/cmdline-tools.zip

RUN yes | sdkmanager --licenses
RUN sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"

RUN git clone https://github.com/flutter/flutter.git -b stable /flutter
ENV PATH="/flutter/bin:$PATH"

RUN flutter doctor
RUN flutter precache

WORKDIR /app
COPY . .

RUN if [ -f .dart-env ]; then \
    echo "✅ Found .dart-env file"; \
    cat .dart-env; \
    else \
    echo "⚠️  .dart-env not found in context, creating with defaults..."; \
    echo "GOOGLE_CLIENT_ID=replace_google_client_id" > .dart-env && \
    echo "GOOGLE_API_KEY=replace_google_api_key" >> .dart-env && \
    echo "BACKEND_HOST=localhost" >> .dart-env && \
    echo "BACKEND_PORT=8080" >> .dart-env && \
    echo "ENVIRONMENT=development" >> .dart-env && \
    echo "GITHUB_CLIENT_ID=replace_github_client_id" >> .dart-env; \
    cat .dart-env; \
    fi && \
    # Fail the build if required OAuth credentials are missing or empty
    GOOGLE_CLIENT_ID=$(grep -E '^GOOGLE_CLIENT_ID=' .dart-env | sed 's/^GOOGLE_CLIENT_ID=//') && \
    GOOGLE_API_KEY=$(grep -E '^GOOGLE_API_KEY=' .dart-env | sed 's/^GOOGLE_API_KEY=//') && \
    if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_API_KEY" ]; then \
        echo "❌ ERROR: GOOGLE_CLIENT_ID and GOOGLE_API_KEY must be set in .dart-env and not empty."; \
        echo "If you're building for development locally, set ENVIRONMENT=development and provide valid keys or adjust the Dockerfile."; \
        exit 1; \
    fi

RUN flutter pub get

# Build APK with environment variables from .dart-env file
RUN flutter build apk \
    --release \
    -t lib/main.dart \
    --dart-define-from-file=.dart-env \
    --android-skip-build-dependency-validation

RUN mkdir -p /shared && cp build/app/outputs/flutter-apk/app-release.apk /shared/client.apk && \
    echo "✅ APK ready at /shared/client.apk"