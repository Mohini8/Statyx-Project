# Production VPS Deployment Guide

This guide walks you through deploying Statyx to a production Linux VPS with Nginx and systemd.

## Prerequisites

- Ubuntu 20.04+ or similar Linux distro
- Root or sudo access
- Domain name (optional, but recommended)
- 2+ GB RAM and 2+ CPU cores

## 1. Initial VPS Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required tools
sudo apt install -y curl git wget build-essential

# Install Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install pnpm
curl -fsSL https://get.pnpm.io/install.sh | sh -
source ~/.bashrc

# Install Python 3.12+
sudo apt install -y python3 python3-pip python3-venv

# Install Nginx
sudo apt install -y nginx

# Install UFW firewall (optional but recommended)
sudo apt install -y ufw
```

## 2. Clone and configure the repository

```bash
# Navigate to deployment directory
cd /opt

# Clone the repository
sudo git clone https://github.com/Mohini8/Statyx-Project.git
sudo chown -R $USER:$USER Statyx-Project
cd Statyx-Project
```

## 3. Set up environment variables

Create `.env` files for each service:

### 3a. Create `artifacts/api-server/.env`

```bash
cat > artifacts/api-server/.env << 'EOF'
DATABASE_URL=postgresql://postgres.lpftzjvnyxrzrxedxyuu:CiaPhvMTVDYj6HT9@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres
NODE_ENV=production
PORT=3002
SESSION_SECRET=$(openssl rand -hex 32)
EOF
```

### 3b. Create `artifacts/streamlit-app/.env` (if needed)

```bash
cat > artifacts/streamlit-app/.env << 'EOF'
PYTHONUNBUFFERED=1
EOF
```

## 4. Install dependencies

```bash
# Install Node dependencies
pnpm install

# Install Python dependencies for Streamlit
cd artifacts/streamlit-app
python3 -m pip install -r requirements.txt
cd ../..
```

## 5. Build production artifacts

```bash
# Build all frontends and backend
BASE_PATH=/ pnpm --dir artifacts/statyx-ai run build
BASE_PATH=/mockup pnpm --dir artifacts/mockup-sandbox run build
pnpm --dir artifacts/api-server run build
```

## 6. Set up systemd services

Create three systemd service files on your VPS:

### 6a. Python FastAPI backend

```bash
sudo tee /etc/systemd/system/statyx-python.service > /dev/null << 'EOF'
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
EOF
```

### 6b. Node.js API server

```bash
sudo tee /etc/systemd/system/statyx-api.service > /dev/null << 'EOF'
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
EOF
```

### 6c. Enable and start services

```bash
sudo systemctl daemon-reload
sudo systemctl enable statyx-python statyx-api
sudo systemctl start statyx-python statyx-api
sudo systemctl status statyx-python statyx-api
```

## 7. Configure Nginx as reverse proxy

Create the Nginx configuration file:

```bash
sudo tee /etc/nginx/sites-available/statyx.conf > /dev/null << 'EOF'
upstream api_backend {
    server 127.0.0.1:3002;
}

upstream python_backend {
    server 127.0.0.1:8502;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS (uncomment after SSL is set up)
    # return 301 https://$server_name$request_uri;

    root /opt/Statyx-Project/artifacts/statyx-ai/dist/public;
    index index.html;

    # React app routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Mockup sandbox
    location /mockup/ {
        alias /opt/Statyx-Project/artifacts/mockup-sandbox/dist/;
        try_files $uri $uri/ /mockup/index.html;
    }

    # API proxy
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

    # Streamlit proxy
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

    # Python API proxy
    location /api/python/ {
        proxy_pass http://python_backend/api/python/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 100M;  # Allow large file uploads
    }

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}

# HTTPS configuration (uncomment and update after getting SSL certificate)
# server {
#     listen 443 ssl http2;
#     server_name yourdomain.com;
# 
#     ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers HIGH:!aNULL:!MD5;
# 
#     # ... rest of the config same as above ...
# }
EOF
```

Enable the Nginx site:

```bash
sudo ln -s /etc/nginx/sites-available/statyx.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site (optional)
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

## 8. Set up SSL/TLS with Let's Encrypt (recommended)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Update Nginx config with SSL paths (uncomment HTTPS section above)
# Then restart Nginx
sudo systemctl restart nginx

# Auto-renewal
sudo systemctl enable certbot.timer
```

## 9. Configure firewall (optional)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## 10. Verify deployment

```bash
# Check systemd services
sudo systemctl status statyx-python
sudo systemctl status statyx-api

# Check ports
sudo ss -ltnp | grep -E '8502|3002|80|443'

# Test endpoints
curl -s http://127.0.0.1:8502/docs | head -n 5
curl -s http://127.0.0.1:3002/api/streamlit-url

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

## 11. Monitoring and logs

```bash
# View service logs
sudo journalctl -u statyx-python -f
sudo journalctl -u statyx-api -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check disk space
df -h
du -sh /opt/Statyx-Project

# Monitor resources
htop
```

## 12. Update deployment

To deploy a new version:

```bash
cd /opt/Statyx-Project
git pull origin main
pnpm install
pnpm --dir artifacts/api-server run build
BASE_PATH=/ pnpm --dir artifacts/statyx-ai run build

# Restart services
sudo systemctl restart statyx-api
sudo systemctl restart statyx-python
```

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u statyx-api -n 50
sudo journalctl -u statyx-python -n 50
```

### Nginx proxy issues
- Check if services are running: `ss -ltnp | grep 3002`
- Check Nginx config: `sudo nginx -t`
- View errors: `sudo tail -f /var/log/nginx/error.log`

### Database connection issues
- Verify DATABASE_URL: `cat artifacts/api-server/.env`
- Test database: `psql $DATABASE_URL -c "SELECT 1"`

### Port already in use
```bash
# Find and kill process
sudo lsof -i :3002
sudo kill -9 <PID>
```

## Performance tuning

### Increase Nginx worker connections
```bash
sudo nano /etc/nginx/nginx.conf
# Find "worker_connections" and increase to 2048+
sudo systemctl restart nginx
```

### Enable gzip compression
```bash
# Add to Nginx server block
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### Optimize Node.js
Pass flags to service:
```bash
ExecStart=/usr/bin/env node --max-old-space-size=2048 --enable-source-maps ./dist/index.mjs
```

## Backup strategy

```bash
# Daily backup script
sudo tee /usr/local/bin/backup-statyx.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/statyx"
mkdir -p $BACKUP_DIR
pg_dump $DATABASE_URL > $BACKUP_DIR/db-$(date +%Y%m%d-%H%M%S).sql
tar -czf $BACKUP_DIR/app-$(date +%Y%m%d-%H%M%S).tar.gz /opt/Statyx-Project
find $BACKUP_DIR -mtime +7 -delete  # Keep 7 days
EOF

sudo chmod +x /usr/local/bin/backup-statyx.sh

# Add to crontab
(sudo crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-statyx.sh") | sudo crontab -
```

---

Your Statyx project is now live on your VPS! 🚀
