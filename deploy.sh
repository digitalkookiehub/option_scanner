#!/bin/bash
set -e

echo "=== Option Screener Backend Deployment ==="

# Step 1: Start with HTTP-only nginx (for SSL cert generation)
echo "[1/4] Starting services with HTTP-only nginx..."
cp nginx-init.conf nginx.conf.bak
cp nginx-init.conf nginx.conf
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d postgres backend nginx

echo "Waiting for services to start..."
sleep 10

# Step 2: Get SSL certificate
echo "[2/4] Obtaining SSL certificate..."
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/lib/letsencrypt \
  -d api.optionscreener.in \
  --email admin@optionscreener.in \
  --agree-tos --no-eff-email

# Step 3: Switch to HTTPS nginx config
echo "[3/4] Switching to HTTPS nginx config..."
cp nginx.conf.bak nginx.conf.http-backup
# Restore the full HTTPS nginx.conf
cat > nginx.conf << 'NGINXEOF'
server {
    listen 80;
    server_name api.optionscreener.in;

    location /.well-known/acme-challenge/ {
        root /var/lib/letsencrypt;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name api.optionscreener.in;

    ssl_certificate /etc/letsencrypt/live/api.optionscreener.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.optionscreener.in/privkey.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
NGINXEOF

# Step 4: Restart nginx with SSL
echo "[4/4] Restarting nginx with SSL..."
docker compose -f docker-compose.prod.yml restart nginx

echo ""
echo "=== Deployment complete! ==="
echo "API available at: https://api.optionscreener.in/api/health"
