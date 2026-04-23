# VPS Deployment Guide

This repository contains:

- `artifacts/statyx-ai`: main React/Vite frontend
- `artifacts/mockup-sandbox`: additional React/Vite mockup frontend
- `artifacts/api-server`: Express API server + reverse proxy
- `artifacts/streamlit-app`: Python Streamlit app and FastAPI backend

## What changed for VPS

- `artifacts/statyx-ai/vite.config.ts` now defaults `BASE_PATH` to `/`
- `artifacts/mockup-sandbox/vite.config.ts` now defaults `BASE_PATH` to `/`
- `@replit` Vite plugins are only loaded when `REPL_ID` is present
- `artifacts/api-server/src/routes/analytics.ts` supports a configurable `STREAMLIT_URL`

These changes make the project usable on a plain VPS without Replit/Codespace environment variables.

## Recommended VPS setup

1. Install Node.js 20+ and pnpm
2. Install Python 3.12+ and pip

### Example Ubuntu commands

```bash
sudo apt update
sudo apt install -y curl git python3 python3-pip
curl -fsSL https://get.pnpm.io/install.sh | sh -
source ~/.bashrc
```

## Install dependencies

```bash
cd /path/to/Statyx-Project
pnpm install
cd artifacts/streamlit-app
python -m pip install -r requirements.txt
```

## Build the frontends

```bash
cd /path/to/Statyx-Project/artifacts/statyx-ai
BASE_PATH=/ pnpm run build

cd /path/to/Statyx-Project/artifacts/mockup-sandbox
BASE_PATH=/mockup pnpm run build
```

If you do not need `mockup-sandbox`, skip the second build.

## Build the API server

```bash
cd /path/to/Statyx-Project/artifacts/api-server
pnpm run build
```

## Start the services

### Python backend

```bash
cd /path/to/Statyx-Project/artifacts/streamlit-app
python -m uvicorn api:app --host 0.0.0.0 --port 8502
```

### Streamlit app (if you need it)

```bash
cd /path/to/Statyx-Project/artifacts/streamlit-app
python -m streamlit run app.py --server.port=8501 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
```

### Node API server

```bash
cd /path/to/Statyx-Project/artifacts/api-server
export NODE_ENV=production
export PORT=3002
export DATABASE_URL="<your database url>"
pnpm run start
```

## Proxy / Hosting strategy

On a VPS, use either Nginx or a process manager to expose the services. Example Nginx configuration:

```nginx
server {
  listen 80;
  server_name example.com;

  root /path/to/Statyx-Project/artifacts/statyx-ai/dist;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /mockup/ {
    alias /path/to/Statyx-Project/artifacts/mockup-sandbox/dist/;
    try_files $uri $uri/ /mockup/index.html;
  }

  location /api/ {
    proxy_pass http://127.0.0.1:3002/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  location /streamlit/ {
    proxy_pass http://127.0.0.1:8501/streamlit/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }

  location /api/python/ {
    proxy_pass http://127.0.0.1:8502/api/python/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  }
}
```

## Run as managed services

Use `systemd`, `pm2`, or `supervisord` to keep the processes alive.

### Example `systemd` service for API server

Create `/etc/systemd/system/statyx-api.service`:

```ini
[Unit]
Description=Statyx API Server
After=network.target

[Service]
WorkingDirectory=/path/to/Statyx-Project/artifacts/api-server
Environment=NODE_ENV=production
Environment=PORT=3002
Environment=DATABASE_URL=<your database url>
ExecStart=/usr/bin/env pnpm run start
Restart=always
User=www-data

[Install]
WantedBy=multi-user.target
```

### Example `systemd` service for Python backend

Create `/etc/systemd/system/statyx-python.service`:

```ini
[Unit]
Description=Statyx Python Backend
After=network.target

[Service]
WorkingDirectory=/path/to/Statyx-Project/artifacts/streamlit-app
ExecStart=/usr/bin/env python -m uvicorn api:app --host 0.0.0.0 --port 8502
Restart=always
User=www-data

[Install]
WantedBy=multi-user.target
```

## Important notes

- If you want a single domain for everything, use Nginx to serve the static frontend and proxy API/Streamlit paths.
- The app now runs on a normal VPS without requiring `REPL_ID` or Replit runtime variables.
- You may still need to configure a production database URL instead of the embedded Supabase URL.
- If you want, I can also add a `docker-compose.yml` and Dockerfiles for fully containerized deployment.
