#!/bin/bash
# Quick deploy script for Statyx VPS deployment
# Usage: ./deploy.sh yourdomain.com

set -e

DOMAIN=${1:-localhost}
PROJECT_DIR="/opt/Statyx-Project"
REPO_URL="https://github.com/Mohini8/Statyx-Project.git"

echo "=========================================="
echo "Statyx VPS Deployment Script"
echo "Domain: $DOMAIN"
echo "=========================================="

# 1. Update system
echo "[1/8] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
echo "[2/8] Installing dependencies..."
sudo apt install -y curl git build-essential python3 python3-pip python3-venv nodejs nginx

# 3. Install pnpm
echo "[3/8] Installing pnpm..."
curl -fsSL https://get.pnpm.io/install.sh | sh -
source ~/.bashrc

# 4. Clone repository
echo "[4/8] Cloning repository..."
sudo rm -rf $PROJECT_DIR
sudo git clone $REPO_URL $PROJECT_DIR
sudo chown -R $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# 5. Install dependencies
echo "[5/8] Installing project dependencies..."
pnpm install
cd artifacts/streamlit-app && python3 -m pip install -r requirements.txt && cd ../..

# 6. Build production artifacts
echo "[6/8] Building production artifacts..."
BASE_PATH=/ pnpm --dir artifacts/statyx-ai run build
BASE_PATH=/mockup pnpm --dir artifacts/mockup-sandbox run build
pnpm --dir artifacts/api-server run build

# 7. Setup environment and systemd
echo "[7/8] Setting up environment and systemd services..."
cat > artifacts/api-server/.env << EOF
DATABASE_URL=postgresql://postgres.lpftzjvnyxrzrxedxyuu:CiaPhvMTVDYj6HT9@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres
NODE_ENV=production
PORT=3002
SESSION_SECRET=$(openssl rand -hex 32)
EOF

# Create systemd services
sudo tee /etc/systemd/system/statyx-python.service > /dev/null << 'SYSTEMD_PYTHON'
[Unit]
Description=Statyx Python Backend (FastAPI)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/Statyx-Project/artifacts/streamlit-app
ExecStart=/usr/bin/env python3 -m uvicorn api:app --host 0.0.0.0 --port 8502
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
User=www-data
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
SYSTEMD_PYTHON

sudo tee /etc/systemd/system/statyx-api.service > /dev/null << 'SYSTEMD_API'
[Unit]
Description=Statyx Node.js API Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/Statyx-Project/artifacts/api-server
ExecStart=/usr/bin/env node --enable-source-maps ./dist/index.mjs
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
User=www-data
EnvironmentFile=/opt/Statyx-Project/artifacts/api-server/.env

[Install]
WantedBy=multi-user.target
SYSTEMD_API

sudo systemctl daemon-reload
sudo systemctl enable statyx-python statyx-api
sudo systemctl start statyx-python statyx-api

# 8. Setup Nginx
echo "[8/8] Setting up Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/statyx.conf > /dev/null << 'NGINX_CONFIG'
upstream api_backend {
    server 127.0.0.1:3002;
}

upstream python_backend {
    server 127.0.0.1:8502;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    root /opt/Statyx-Project/artifacts/statyx-ai/dist/public;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /mockup/ {
        alias /opt/Statyx-Project/artifacts/mockup-sandbox/dist/;
        try_files $uri $uri/ /mockup/index.html;
    }

    location /api/ {
        proxy_pass http://api_backend/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /streamlit/ {
        proxy_pass http://python_backend/streamlit/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/python/ {
        proxy_pass http://python_backend/api/python/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 100M;
    }

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
}
NGINX_CONFIG

sudo sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/statyx.conf
sudo ln -sf /etc/nginx/sites-available/statyx.conf /etc/nginx/sites-enabled/statyx.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo ""
echo "=========================================="
echo "✅ Deployment complete!"
echo "=========================================="
echo "Services running:"
sudo systemctl status statyx-python --no-pager
sudo systemctl status statyx-api --no-pager
echo ""
echo "Access your app:"
echo "  http://$DOMAIN"
echo ""
echo "View logs:"
echo "  sudo journalctl -u statyx-api -f"
echo "  sudo journalctl -u statyx-python -f"
echo ""
echo "For HTTPS setup, run:"
echo "  sudo certbot certonly --nginx -d $DOMAIN"
echo "=========================================="
