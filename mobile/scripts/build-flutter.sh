#!/bin/bash
# Flutter Build Helper Script
# Manages build-time variable injection using --dart-define-from-file
#
# Usage:
#   ./scripts/build-flutter.sh run       # Run with configuration
#   ./scripts/build-flutter.sh build     # Build APK/AAB
#   ./scripts/build-flutter.sh web       # Build for web

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DART_ENV_FILE="${SCRIPT_DIR}/.dart-env"

# Function to load or create .dart-env
setup_dart_env() {
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        echo "📄 Loading configuration from .env..."
        
        # Helper function to safely extract env variable values
        get_env_value() {
            local key="$1"
            local default="$2"
            grep "^${key}=" "${SCRIPT_DIR}/.env" | sed "s/^${key}=//" | head -n1 || echo "$default"
        }
        
        # Extract variables safely (handles values with =, quotes, spaces)
        BACKEND_HOST=$(get_env_value "BACKEND_HOST" "localhost")
        BACKEND_PORT=$(get_env_value "BACKEND_PORT" "8080")
        GOOGLE_CLIENT_ID=$(get_env_value "GOOGLE_CLIENT_ID" "")
        GOOGLE_API_KEY=$(get_env_value "GOOGLE_API_KEY" "")
        GITHUB_CLIENT_ID=$(get_env_value "GITHUB_CLIENT_ID" "")
        ENVIRONMENT=$(get_env_value "ENVIRONMENT" "development")
        
        # Write to .dart-env
        cat > "${DART_ENV_FILE}" << EOF
BACKEND_HOST=$BACKEND_HOST
BACKEND_PORT=$BACKEND_PORT
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_API_KEY=$GOOGLE_API_KEY
GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID
ENVIRONMENT=$ENVIRONMENT
EOF
    else
        echo "⚠️  .env not found, creating default .dart-env..."
        cat > "${DART_ENV_FILE}" << EOF
BACKEND_HOST=localhost
BACKEND_PORT=8080
GOOGLE_CLIENT_ID=
GOOGLE_API_KEY=
GITHUB_CLIENT_ID=
ENVIRONMENT=development
EOF
    fi
    
    echo "✅ Configuration ready at: ${DART_ENV_FILE}"
    echo "📋 Contents:"
    cat "${DART_ENV_FILE}" | sed 's/^/   /'
}

# Run Flutter app with configuration
run_flutter() {
    setup_dart_env
    echo ""
    echo "▶️  Running Flutter app with configuration..."
    flutter run --dart-define-from-file="${DART_ENV_FILE}" "$@"
}

# Build Flutter APK with configuration
build_apk() {
    setup_dart_env
    echo ""
    echo "🔨 Building Flutter APK with configuration..."
    flutter build apk --release \
        --dart-define-from-file="${DART_ENV_FILE}" \
        --android-skip-build-dependency-validation \
        "$@"
    
    if [ -f "build/app/outputs/flutter-apk/app-release.apk" ]; then
        echo "✅ APK built successfully!"
        ls -lh build/app/outputs/flutter-apk/app-release.apk
    fi
}

# Build Flutter AAB with configuration
build_aab() {
    setup_dart_env
    echo ""
    echo "🔨 Building Flutter AAB with configuration..."
    flutter build appbundle --release \
        --dart-define-from-file="${DART_ENV_FILE}" \
        "$@"
    
    if [ -f "build/app/outputs/bundle/release/app-release.aab" ]; then
        echo "✅ AAB built successfully!"
        ls -lh build/app/outputs/bundle/release/app-release.aab
    fi
}

# Build for web with configuration
build_web() {
    setup_dart_env
    echo ""
    echo "🌐 Building Flutter for Web with configuration..."
    flutter build web --release \
        --dart-define-from-file="${DART_ENV_FILE}" \
        "$@"
    
    echo "✅ Web build completed!"
}

# Show help
show_help() {
    cat << EOF
Flutter Build Helper Script

Usage:
    $0 <command> [options]

Commands:
    run     Run the Flutter app with injected configuration
    build   Build Android APK with injected configuration
    aab     Build Android App Bundle with injected configuration
    web     Build for Web with injected configuration
    setup   Setup .dart-env from .env file
    help    Show this help message

Examples:
    # Run app with development configuration
    $0 run

    # Build production APK
    $0 build

    # Build and run on specific device
    $0 run -d <device_id>

Configuration:
    This script reads from .env and creates .dart-env for Flutter builds.
    Variables used:
    - BACKEND_HOST      (default: localhost)
    - BACKEND_PORT      (default: 8080)
    - GOOGLE_CLIENT_ID  (required)
    - GOOGLE_API_KEY    (required)
    - GITHUB_CLIENT_ID  (optional)
    - ENVIRONMENT       (default: development)

Note:
    Variables are injected at build time using --dart-define-from-file,
    NOT from Platform.environment at runtime.

EOF
}

# Main
case "${1:-help}" in
    run)
        shift
        run_flutter "$@"
        ;;
    build|apk)
        shift
        build_apk "$@"
        ;;
    aab)
        shift
        build_aab "$@"
        ;;
    web)
        shift
        build_web "$@"
        ;;
    setup)
        setup_dart_env
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
