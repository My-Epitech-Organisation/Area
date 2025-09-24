# Area

Minimal POC: Django + Postgres API, Next.js web, optional Android mobile client (Compose + Ktor).

## Prerequisites

- Docker + Docker Compose
- Node.js 20+ (for local web if not using Docker)
- Python 3.11+ (for local server if not using Docker)
- Android SDK (cmdline-tools) + JDK 17 for mobile build (no Android Studio required)

## Quick Start (Docker)

```bash
# From repo root
docker compose up -d

# API: http://localhost:8080/about.json
# Web: http://localhost:8081
# APK (if provided): http://localhost:8081/apk/client.apk
```

## Backend (Django) – local

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_DEBUG=True POSTGRES_HOST=localhost POSTGRES_DB=area POSTGRES_USER=area POSTGRES_PASSWORD=area
python manage.py migrate
python manage.py runserver 0.0.0.0:8080
```

## Frontend (Next.js) – local

```bash
cd web
npm ci
npm run dev # http://localhost:3000 (mapped to 8081 in Docker)
```

## Mobile (Android)

Install SDK + build-tools (one-time):

```bash
export ANDROID_SDK_ROOT="$HOME/Android/Sdk"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export PATH="$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH"

yes | sdkmanager --licenses
sdkmanager --install "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

Build the APK:

```bash
cd mobile/android-app
printf "sdk.dir=%s\n" "$ANDROID_SDK_ROOT" > local.properties
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
```

Point the app to your machine IP (for testing on a phone):

- Update `API_BASE_URL` in `mobile/android-app/app/build.gradle.kts` to `http://<your_LAN_IP>:8080`
- Rebuild `./gradlew assembleDebug`

Serve the APK from the web container:

```bash
# Ensure web is up
docker compose up -d web

# Copy APK into web container
docker cp mobile/android-app/app/build/outputs/apk/debug/app-debug.apk $(docker compose ps -q web):/apk/client.apk

# Download from phone
# http://<your_LAN_IP>:8081/apk/client.apk
```

## Notes

- CORS/hosts are configured for localhost by default. When using a phone, add your LAN IP to `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` in `docker-compose.yml` under `server.environment`, then `docker compose up -d server`.
- If your LAN IP changes, update both `docker-compose.yml` and the mobile `API_BASE_URL` and rebuild.
