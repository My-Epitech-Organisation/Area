#!/bin/bash
# ============================================================================
# Environment Variables Validation Script
# ============================================================================
# This script validates that all required environment variables are set
# Run before starting the application to catch configuration errors early
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ENV_FILE="${1:-.env}"

echo "============================================================================"
echo "🔍 Validating Environment Variables"
echo "============================================================================"
echo "Reading from: $ENV_FILE"
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ ERROR: $ENV_FILE not found!${NC}"
    echo "Please copy .env.example to .env and fill in your values:"
    echo "  cp .env.example .env"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' "$ENV_FILE" | xargs)

# Array of required variables grouped by category
declare -a REQUIRED_VARS=(
    # Database
    "DB_USER"
    "DB_PASSWORD"
    "DB_NAME"
    "DB_HOST"
    "DB_PORT"

    # Redis
    "REDIS_PORT"
    "REDIS_URL"

    # Django Backend
    "BACKEND_PORT"
    "DJANGO_SETTINGS_MODULE"
    "SECRET_KEY"
    "DEBUG"
    "ENVIRONMENT"

    # Logging
    "LOG_LEVEL"
    "DJANGO_LOG_FILE"

    # JWT
    "JWT_SIGNING_KEY"
       # Email
    "EMAIL_BACKEND"
    "EMAIL_HOST"
    "EMAIL_PORT"
    "EMAIL_USE_TLS"
    "EMAIL_USE_SSL"
    "EMAIL_HOST_USER"
    "EMAIL_HOST_PASSWORD"
    "DEFAULT_FROM_EMAIL"

    # Frontend
    "FRONTEND_PORT"
    "FRONTEND_URL"
    "VITE_API_BASE"

    # CORS & Security
    "ALLOWED_HOSTS"
    "CORS_ALLOW_ALL_ORIGINS"
    "SECURE_SSL_REDIRECT"
    "SESSION_COOKIE_SECURE"
    "CSRF_COOKIE_SECURE"

    # OAuth2
    "GOOGLE_CLIENT_ID"
    "GOOGLE_CLIENT_SECRET"
    "GOOGLE_REDIRECT_URI"
    "GITHUB_CLIENT_ID"
    "GITHUB_CLIENT_SECRET"
    "GITHUB_REDIRECT_URI"

    # Webhooks (JSON dictionary format)
    "WEBHOOK_SECRETS"

    # Celery
    "CELERY_TIMEZONE"
    "CELERY_TASK_ALWAYS_EAGER"

    # Monitoring
    "FLOWER_PORT"

    # Docker
    "COMPOSE_PROJECT_NAME"
)

MISSING_VARS=()
PLACEHOLDER_VARS=()
TOTAL_VARS=${#REQUIRED_VARS[@]}
VALID_VARS=0

# Check each required variable
for VAR in "${REQUIRED_VARS[@]}"; do
    VALUE="${!VAR}"

    if [ -z "$VALUE" ]; then
        MISSING_VARS+=("$VAR")
        echo -e "${RED}❌ MISSING: $VAR${NC}"
    else
        # Check for placeholder values that need to be changed
        if [[ "$VALUE" =~ (your-|CHANGE_ME|change-this|your_|placeholder) ]]; then
            PLACEHOLDER_VARS+=("$VAR")
            echo -e "${YELLOW}⚠️  PLACEHOLDER: $VAR = $VALUE${NC}"
        else
            VALID_VARS=$((VALID_VARS + 1))
            echo -e "${GREEN}✅ $VAR${NC}"
        fi
    fi
done

echo ""
echo "============================================================================"
echo "📊 Validation Summary"
echo "============================================================================"
echo "Total variables checked: $TOTAL_VARS"
echo -e "Valid: ${GREEN}$VALID_VARS${NC}"
echo -e "Missing: ${RED}${#MISSING_VARS[@]}${NC}"
echo -e "Placeholders: ${YELLOW}${#PLACEHOLDER_VARS[@]}${NC}"
echo ""

# Production-specific checks
if [ "$ENVIRONMENT" == "production" ]; then
    echo "============================================================================"
    echo "🔒 Production Environment Checks"
    echo "============================================================================"

    PROD_WARNINGS=0

    if [ "$DEBUG" != "False" ]; then
        echo -e "${RED}❌ DEBUG must be False in production!${NC}"
        PROD_WARNINGS=$((PROD_WARNINGS + 1))
    fi

    if [ "$SECURE_SSL_REDIRECT" != "True" ]; then
        echo -e "${YELLOW}⚠️  SECURE_SSL_REDIRECT should be True in production${NC}"
        PROD_WARNINGS=$((PROD_WARNINGS + 1))
    fi

    if [ "$SESSION_COOKIE_SECURE" != "True" ]; then
        echo -e "${YELLOW}⚠️  SESSION_COOKIE_SECURE should be True in production${NC}"
        PROD_WARNINGS=$((PROD_WARNINGS + 1))
    fi

    if [ "$CSRF_COOKIE_SECURE" != "True" ]; then
        echo -e "${YELLOW}⚠️  CSRF_COOKIE_SECURE should be True in production${NC}"
        PROD_WARNINGS=$((PROD_WARNINGS + 1))
    fi

    if [ "$CORS_ALLOW_ALL_ORIGINS" != "False" ]; then
        echo -e "${RED}❌ CORS_ALLOW_ALL_ORIGINS must be False in production!${NC}"
        PROD_WARNINGS=$((PROD_WARNINGS + 1))
    fi

    if [ ${#PLACEHOLDER_VARS[@]} -gt 0 ]; then
        echo -e "${RED}❌ Placeholder values detected in production!${NC}"
        PROD_WARNINGS=$((PROD_WARNINGS + 1))
    fi

    if [ $PROD_WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ All production checks passed!${NC}"
    fi

    echo ""
fi

# Exit with appropriate code
if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}❌ VALIDATION FAILED: Missing required variables!${NC}"
    echo ""
    echo "Missing variables:"
    for VAR in "${MISSING_VARS[@]}"; do
        echo "  - $VAR"
    done
    exit 1
elif [ "$ENVIRONMENT" == "production" ] && [ $PROD_WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  VALIDATION WARNING: Production environment has security issues!${NC}"
    exit 2
elif [ ${#PLACEHOLDER_VARS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  VALIDATION WARNING: Some variables have placeholder values${NC}"
    echo ""
    echo "Variables with placeholders:"
    for VAR in "${PLACEHOLDER_VARS[@]}"; do
        echo "  - $VAR"
    done
    echo ""
    echo "These may need to be updated before production deployment."
    exit 0
else
    echo -e "${GREEN}✅ VALIDATION PASSED: All required variables are set!${NC}"
    exit 0
fi
