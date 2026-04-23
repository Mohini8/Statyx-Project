# 🚀 Statyx Production Deployment

This document provides multiple ways to deploy Statyx to a production VPS.

## 📋 Deployment Options

### Option 1: Quick Bash Deployment (Recommended for simple VPS)
Best for: Ubuntu/Debian VPS, minimal configuration

```bash
cd /path/to/Statyx-Project
chmod +x deploy.sh
./deploy.sh yourdomain.com
```

This script will:
- Install all dependencies (Node.js, Python, Nginx)
- Build production artifacts
- Set up systemd services
- Configure Nginx reverse proxy
- Start all services

### Option 2: Docker Compose (Recommended for complex setups)
Best for: Easy scaling, containerized deployments, multiple VPS environments

```bash
# 1. Build production assets
cd /workspaces/Statyx-Project
BASE_PATH=/ pnpm --dir artifacts/statyx-ai run build
BASE_PATH=/mockup pnpm --dir artifacts/mockup-sandbox run build
pnpm --dir artifacts/api-server run build

# 2. Create .env file
cp .env.docker .env
# Edit .env with your DATABASE_URL and SESSION_SECRET

# 3. Start services
docker-compose up -d

# 4. View logs
docker-compose logs -f
```

### Option 3: Manual Step-by-Step Setup
See: [VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md)

---

## 🔧 Environment Configuration

### Required Variables for Production

**`artifacts/api-server/.env`** (see `.env.example`):
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
NODE_ENV=production
PORT=3002
SESSION_SECRET=<random 64-char hex string>
```

**Generate SESSION_SECRET:**
```bash
openssl rand -hex 32
```

### Optional Variables

```env
# Streamlit URL (default: /streamlit)
STREAMLIT_URL=/streamlit

# Python backend settings
PYTHONUNBUFFERED=1

# Streamlit config (optional)
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Nginx Reverse Proxy                 │
│                   (Port 80/443)                       │
└────────────────┬──────────────────────┬──────────────┘
                 │                      │
        ┌────────▼────────┐    ┌────────▼────────┐
        │  React Frontend  │    │  Node.js API    │
        │   (Port 5173→80) │    │  (Port 3002)    │
        └──────────────────┘    └────────┬────────┘
                                         │
                            ┌────────────▼─────────────┐
                            │  Python FastAPI Backend   │
                            │    (Port 8502)            │
                            └──────────────────────────┘
                                         │
                            ┌────────────▼─────────────┐
                            │   PostgreSQL Database     │
                            │    (Supabase)             │
                            └──────────────────────────┘
```

---

## ✅ Verification Checklist

After deployment, verify everything is working:

```bash
# Check systemd services
sudo systemctl status statyx-api
sudo systemctl status statyx-python

# Test endpoints
curl http://your-domain/api/streamlit-url
curl http://your-domain/

# View logs
sudo journalctl -u statyx-api -n 50
sudo journalctl -u statyx-python -n 50

# Monitor resources
htop
df -h
```

---

## 🔒 Security Best Practices

1. **Use HTTPS (Let's Encrypt)**
   ```bash
   sudo certbot certonly --nginx -d yourdomain.com
   ```

2. **Secure environment variables**
   ```bash
   # Never commit .env files
   # Store DATABASE_URL securely
   chmod 600 artifacts/api-server/.env
   ```

3. **Firewall configuration**
   ```bash
   sudo ufw allow 22/tcp  # SSH
   sudo ufw allow 80/tcp  # HTTP
   sudo ufw allow 443/tcp # HTTPS
   sudo ufw enable
   ```

4. **Regular backups**
   ```bash
   # Database backup
   pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
   ```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u statyx-api -n 100
sudo journalctl -u statyx-python -n 100

# Verify ports are free
sudo ss -ltnp | grep -E '3002|8502'
```

### Nginx 502 Bad Gateway
```bash
# Check if backend services are running
curl -v http://127.0.0.1:3002/api/streamlit-url

# Check Nginx configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log
```

### Database connection errors
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# Verify DATABASE_URL format
cat artifacts/api-server/.env | grep DATABASE_URL
```

### High memory usage
```bash
# Monitor memory
free -h

# Increase Node.js heap space (in systemd service ExecStart)
node --max-old-space-size=2048 ./dist/index.mjs
```

---

## 📈 Monitoring & Maintenance

### Daily Health Checks
```bash
#!/bin/bash
# Run daily via cron

curl -f http://your-domain/api/streamlit-url || echo "API down"
curl -f http://your-domain/ || echo "Frontend down"
ps aux | grep statyx | grep -v grep || echo "Services down"
```

### Log Rotation
```bash
# Already handled by systemd, but verify:
ls -la /var/log/journal/
journalctl --disk-usage
```

### Updates
```bash
# Pull latest code
cd /opt/Statyx-Project
git pull origin main

# Rebuild only what changed
pnpm install
pnpm --dir artifacts/api-server run build

# Restart services
sudo systemctl restart statyx-api
```

---

## 🆘 Support Channels

- **Issues**: Create a GitHub issue at [Statyx-Project/issues](https://github.com/Mohini8/Statyx-Project/issues)
- **Deployment Help**: See [VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md)
- **Docker Compose**: Use `docker-compose logs` for debugging

---

## 📝 Quick Commands

```bash
# View all running services
ps aux | grep statyx

# Restart all services
sudo systemctl restart statyx-api statyx-python

# View real-time logs
sudo journalctl -u statyx-api -f

# Update deployment
cd /opt/Statyx-Project && git pull && pnpm install && pnpm --dir artifacts/api-server run build && sudo systemctl restart statyx-api

# Check database
psql $DATABASE_URL -c "SELECT version();"
```

---

🎉 Your Statyx project is now ready for production!
