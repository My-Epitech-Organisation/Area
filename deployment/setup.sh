#!/bin/bash
###############################################################################
# AREA Production Setup Script
# Configuration automatique d'un serveur Ubuntu/Debian pour déploiement AREA
###############################################################################

set -e  # Exit on error

echo "============================================"
echo "  AREA Production Setup"
echo "  Domain: areaction.app"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   echo "Usage: sudo bash setup.sh"
   exit 1
fi

echo -e "${GREEN}Step 1/8: System Update${NC}"
apt-get update
apt-get upgrade -y

echo ""
echo -e "${GREEN}Step 2/8: Install Required Packages${NC}"
apt-get install -y \
    curl \
    git \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx \
    htop \
    vim

echo ""
echo -e "${GREEN}Step 3/8: Install Docker${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}Docker installed successfully${NC}"
else
    echo -e "${YELLOW}Docker already installed${NC}"
fi

echo ""
echo -e "${GREEN}Step 4/8: Install Docker Compose${NC}"
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
else
    echo -e "${YELLOW}Docker Compose already installed${NC}"
fi

echo ""
echo -e "${GREEN}Step 5/8: Configure Firewall (UFW)${NC}"
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 8080/tcp  # Backend API
ufw allow 8081/tcp  # Frontend
echo -e "${GREEN}Firewall configured${NC}"

echo ""
echo -e "${GREEN}Step 6/8: Create Dedicated User${NC}"
# Check if user already exists
if id "areaction" &>/dev/null; then
    echo -e "${YELLOW}User 'areaction' already exists${NC}"
else
    echo -e "${YELLOW}Creating dedicated user 'areaction' for security isolation...${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  You will be prompted to set a password for the 'areaction' user${NC}"
    echo -e "${YELLOW}    This user will own the application files and run Docker containers${NC}"
    echo ""

    # Create user with home directory
    adduser --gecos "" areaction

    # Add user to docker group to run docker commands without sudo
    usermod -aG docker areaction

    echo -e "${GREEN}User 'areaction' created successfully${NC}"
fi

echo ""
echo -e "${GREEN}Step 7/8: Create Application Directory${NC}"
mkdir -p /opt/area
chown -R areaction:areaction /opt/area
cd /opt/area

# Get repository info
echo ""
echo -e "${YELLOW}Repository Configuration:${NC}"
read -p "Enter Git repository URL [https://github.com/My-Epitech-Organisation/Area.git]: " REPO_URL
REPO_URL=${REPO_URL:-https://github.com/My-Epitech-Organisation/Area.git}

read -p "Enter Git branch [main]: " GIT_BRANCH
GIT_BRANCH=${GIT_BRANCH:-main}

if [ -d ".git" ]; then
    echo -e "${YELLOW}Repository already exists, pulling latest changes...${NC}"
    sudo -u areaction git pull origin $GIT_BRANCH
else
    echo -e "${GREEN}Cloning repository...${NC}"
    sudo -u areaction git clone -b $GIT_BRANCH $REPO_URL .
fi

echo ""
echo -e "${GREEN}Step 8/8: Environment Configuration${NC}"
echo -e "${YELLOW}Creating production .env file...${NC}"

if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
# Django Settings
DEBUG=False
SECRET_KEY=
ALLOWED_HOSTS=areaction.app,www.areaction.app,localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=area_project.settings
CORS_ALLOWED_ORIGINS=https://areaction.app,https://www.areaction.app

# Database
DB_USER=area_user
DB_PASSWORD=
DB_NAME=area_db
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PORT=6379

# Ports
BACKEND_PORT=8080
FRONTEND_PORT=8081

# OAuth2 - Google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://areaction.app/api/auth/oauth/google/callback/

# OAuth2 - GitHub
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_REDIRECT_URI=https://areaction.app/api/auth/oauth/github/callback/

# Email (SendGrid/Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Production
ENVIRONMENT=production
ENVEOF

    echo -e "${GREEN}.env file created${NC}"
    echo ""
    echo -e "${YELLOW}Please fill in the following required values:${NC}"
    echo ""

    # Generate secure secret key
    SECRET_KEY=$(openssl rand -base64 50 | tr -d '\n')
    sed -i "s/SECRET_KEY=$/SECRET_KEY=$SECRET_KEY/" .env
    echo -e "${GREEN}✓ SECRET_KEY generated${NC}"

    # Database password
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d '\n')
    sed -i "s/DB_PASSWORD=$/DB_PASSWORD=$DB_PASSWORD/" .env
    echo -e "${GREEN}✓ DB_PASSWORD generated${NC}"

    echo ""
    echo -e "${YELLOW}Manual configuration required:${NC}"
    read -p "Google OAuth Client ID: " GOOGLE_CLIENT_ID
    sed -i "s/GOOGLE_CLIENT_ID=$/GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID/" .env

    read -p "Google OAuth Client Secret: " GOOGLE_CLIENT_SECRET
    sed -i "s/GOOGLE_CLIENT_SECRET=$/GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET/" .env

    read -p "GitHub OAuth Client ID: " GITHUB_CLIENT_ID
    sed -i "s/GITHUB_CLIENT_ID=$/GITHUB_CLIENT_ID=$GITHUB_CLIENT_ID/" .env

    read -p "GitHub OAuth Client Secret: " GITHUB_CLIENT_SECRET
    sed -i "s/GITHUB_CLIENT_SECRET=$/GITHUB_CLIENT_SECRET=$GITHUB_CLIENT_SECRET/" .env

    read -p "Email Host User (optional, press Enter to skip): " EMAIL_HOST_USER
    if [ ! -z "$EMAIL_HOST_USER" ]; then
        sed -i "s/EMAIL_HOST_USER=$/EMAIL_HOST_USER=$EMAIL_HOST_USER/" .env
        read -p "Email Host Password: " EMAIL_HOST_PASSWORD
        sed -i "s/EMAIL_HOST_PASSWORD=$/EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD/" .env
    fi

    echo ""
    echo -e "${GREEN}Environment configuration completed${NC}"
else
    echo -e "${YELLOW}.env file already exists, skipping...${NC}"
fi

echo ""
echo -e "${GREEN}Step 8/8: SSL Certificate Setup${NC}"
echo -e "${YELLOW}Setting up Let's Encrypt SSL certificate...${NC}"

read -p "Enter email for Let's Encrypt notifications: " LETSENCRYPT_EMAIL

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
fi

# Create nginx config for certbot
cat > /etc/nginx/sites-available/area << 'NGINXEOF'
server {
    listen 80;
    server_name areaction.app www.areaction.app;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/area /etc/nginx/sites-enabled/area
rm -f /etc/nginx/sites-enabled/default

mkdir -p /var/www/certbot
nginx -t && systemctl reload nginx

# Get SSL certificate
certbot certonly --nginx \
    --email $LETSENCRYPT_EMAIL \
    --agree-tos \
    --no-eff-email \
    -d areaction.app \
    -d www.areaction.app

# Update nginx config with SSL
cat > /etc/nginx/sites-available/area << 'NGINXSSLEOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name areaction.app www.areaction.app;
    return 301 https://$host$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name areaction.app www.areaction.app;

    ssl_certificate /etc/letsencrypt/live/areaction.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/areaction.app/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    # Frontend - React App
    location / {
        proxy_pass http://localhost:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8080/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8080/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files
    location /static/ {
        alias /opt/area/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/area/mediafiles/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # APK download
    location /client.apk {
        alias /opt/area/mobile-build/client.apk;
        add_header Content-Type application/vnd.android.package-archive;
        add_header Content-Disposition "attachment; filename=area-client.apk";
    }
}
NGINXSSLEOF

nginx -t && systemctl reload nginx

echo ""
echo -e "${GREEN}Step 9/10: Setup Auto-renewal for SSL${NC}"
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && systemctl reload nginx") | crontab -

echo ""
echo -e "${GREEN}Step 10/10: Set Correct Permissions${NC}"
# Ensure areaction user owns all application files
chown -R areaction:areaction /opt/area

# Add deployment script to areaction user's path and make it accessible
chmod +x /opt/area/deployment/manage.sh
echo -e "${GREEN}Permissions set correctly${NC}"

echo ""
echo "============================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "============================================"
echo ""
echo -e "${YELLOW}Security Notice:${NC}"
echo "  - Application runs as dedicated user 'areaction'"
echo "  - Docker containers isolated from root user"
echo "  - All files owned by areaction:areaction"
echo ""
echo "Next steps:"
echo "1. Review and update /opt/area/.env with your credentials"
echo "2. Configure DNS for areaction.app to point to this server IP"
echo "3. Switch to areaction user and start the application:"
echo "   sudo su - areaction"
echo "   cd /opt/area"
echo "   ./deployment/manage.sh start"
echo ""
echo "Management commands (as areaction user):"
echo "  sudo su - areaction"
echo "  cd /opt/area"
echo "  ./deployment/manage.sh [start|stop|restart|logs|pull|reset|status]"
echo ""
echo "Application URLs:"
echo "  Frontend: https://areaction.app"
echo "  Backend API: https://areaction.app/api/"
echo "  APK Download: https://areaction.app/client.apk"
echo ""
