# Hostinger Deployment - AIvid unter www.aivid.ch/generator

## 🔐 Hostinger Zugangsdaten
- **Email**: em.martinma@gmail.com
- **Passwort**: 8nTO9fajy5hP'rsz
- **Panel**: https://hpanel.hostinger.com

## 📋 Deployment-Schritte

### Schritt 1: Hostinger Panel Login
1. Gehen Sie zu https://hpanel.hostinger.com
2. Login mit em.martinma@gmail.com / 8nTO9fajy5hP'rsz
3. Wählen Sie die Website aivid.ch aus

### Schritt 2: Repository auf Server klonen

**Via SSH:**
```bash
# SSH-Zugang aktivieren (im Hostinger Panel unter "Advanced" → "SSH Access")
ssh u123456789@aivid.ch

# Zum public_html Verzeichnis navigieren
cd public_html

# Repository klonen (verwenden Sie Ihr GitHub Token)
git clone -b claude/app-store-video-generator-9L5mk https://YOUR_GITHUB_TOKEN@github.com/emmartinma-del/aivid.git generator

cd generator
```

### Schritt 3: Node.js Version einstellen

Im Hostinger Panel:
1. Gehe zu **Advanced** → **Node.js**
2. Wähle Node.js Version **18.x** oder höher
3. Application Root: `/public_html/generator/apps/web`
4. Application URL: `https://aivid.ch/generator`
5. Application Startup File: `server.js` (wird später erstellt)

### Schritt 4: Umgebungsvariablen konfigurieren

Erstellen Sie `.env` Datei auf dem Server:

```bash
cd /home/u123456789/public_html/generator
nano .env
```

Inhalt:
```env
# Anthropic (Open Claude)
ANTHROPIC_API_KEY=openclaude-0PbTd-meaBPKINR_b6G4HgQqH16ddp-F3nQaPq1HSkByunyj

# Stripe (Test-Keys für MVP)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# OpenAI (für TTS)
OPENAI_API_KEY=sk-...

# Auth Secrets
JWT_SECRET=$(openssl rand -base64 32)
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=https://aivid.ch/generator

# URLs
NEXT_PUBLIC_API_URL=https://api.aivid.ch
FRONTEND_URL=https://aivid.ch/generator

# Database (Hostinger MySQL)
DATABASE_URL=postgresql+asyncpg://u123456789_aivid:PASSWORD@localhost:5432/u123456789_aivid

# Redis (falls verfügbar, sonst lokale Alternative)
REDIS_URL=redis://localhost:6379/0

# S3 (AWS oder Hostinger Object Storage)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_UPLOADS_BUCKET=aivid-uploads
S3_OUTPUTS_BUCKET=aivid-outputs

# Environment
ENVIRONMENT=production
```

### Schritt 5: Datenbank erstellen

Im Hostinger Panel:
1. Gehe zu **Databases** → **MySQL Databases**
2. Erstelle neue Datenbank: `u123456789_aivid`
3. Erstelle User: `u123456789_aivid` mit sicherem Passwort
4. Notiere die Zugangsdaten für DATABASE_URL

**Oder PostgreSQL (falls verfügbar):**
- Prüfe ob PostgreSQL verfügbar ist unter **Databases**
- Falls nicht: Verwende externe PostgreSQL (z.B. Supabase, ElephantSQL)

### Schritt 6: Frontend Build & Deploy

```bash
cd /home/u123456789/public_html/generator/apps/web

# Dependencies installieren
npm install

# Production Build
npm run build

# Server-Datei erstellen
cat > server.js << 'EOF'
const { createServer } = require('http')
const { parse } = require('url')
const next = require('next')

const dev = false
const hostname = '0.0.0.0'
const port = process.env.PORT || 3000

const app = next({ dev, hostname, port })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  createServer(async (req, res) => {
    try {
      const parsedUrl = parse(req.url, true)
      await handle(req, res, parsedUrl)
    } catch (err) {
      console.error('Error occurred handling', req.url, err)
      res.statusCode = 500
      res.end('internal server error')
    }
  }).listen(port, (err) => {
    if (err) throw err
    console.log(`> Ready on http://${hostname}:${port}`)
  })
})
EOF

# Starten
npm start
```

### Schritt 7: Backend API Setup

```bash
cd /home/u123456789/public_html/generator/apps/api

# Python Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Database Migrations
alembic upgrade head

# API starten (mit Supervisor oder PM2)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Schritt 8: Reverse Proxy konfigurieren

Erstelle `.htaccess` in `/public_html`:

```apache
RewriteEngine On

# API Proxy
RewriteCond %{REQUEST_URI} ^/api/
RewriteRule ^api/(.*)$ http://localhost:8000/$1 [P,L]

# Generator App Proxy
RewriteCond %{REQUEST_URI} ^/generator
RewriteRule ^generator(.*)$ http://localhost:3000/generator$1 [P,L]

# SSL Redirect
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

### Schritt 9: Process Manager (PM2)

```bash
# PM2 installieren
npm install -g pm2

# Frontend starten
cd /home/u123456789/public_html/generator/apps/web
pm2 start npm --name "aivid-web" -- start

# Backend starten
cd /home/u123456789/public_html/generator/apps/api
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "aivid-api"

# Celery Worker starten
pm2 start "celery -A app.worker.celery_app worker --loglevel=info" --name "aivid-worker"

# Auto-Start bei Reboot
pm2 startup
pm2 save
```

### Schritt 10: SSL-Zertifikat

Im Hostinger Panel:
1. Gehe zu **SSL** → **Manage SSL**
2. Aktiviere **Free SSL** (Let's Encrypt)
3. Warte auf Aktivierung (~5 Minuten)

## 🔧 Alternative: Docker auf Hostinger VPS

Falls Sie einen Hostinger VPS haben:

```bash
# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose installieren
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Repository klonen (verwenden Sie Ihr GitHub Token)
git clone -b claude/app-store-video-generator-9L5mk https://YOUR_GITHUB_TOKEN@github.com/emmartinma-del/aivid.git
cd aivid

# .env konfigurieren
cp .env.example .env
nano .env

# Starten
docker-compose up -d
```

## 📊 Monitoring & Logs

```bash
# PM2 Status
pm2 status

# Logs anzeigen
pm2 logs aivid-web
pm2 logs aivid-api
pm2 logs aivid-worker

# Restart
pm2 restart all
```

## ⚠️ Wichtige Hinweise

1. **Shared Hosting Limitierungen**: 
   - Hostinger Shared Hosting hat Ressourcen-Limits
   - Video-Generierung ist ressourcenintensiv
   - Erwägen Sie VPS für Production

2. **Redis Alternative**:
   - Falls Redis nicht verfügbar: Verwenden Sie Memory-Backend für Celery
   - Oder externe Redis (Redis Labs, Upstash)

3. **S3 Storage**:
   - Hostinger bietet Object Storage
   - Oder verwenden Sie AWS S3, Cloudflare R2

4. **Backup**:
   - Hostinger bietet automatische Backups
   - Zusätzlich: Regelmäßige DB-Exports

## 🚀 Quick Deploy Script

```bash
#!/bin/bash
# deploy.sh

cd /home/u123456789/public_html/generator

# Pull latest changes
git pull origin claude/app-store-video-generator-9L5mk

# Frontend
cd apps/web
npm install
npm run build
pm2 restart aivid-web

# Backend
cd ../api
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
pm2 restart aivid-api
pm2 restart aivid-worker

echo "✅ Deployment complete!"
```

## 📞 Support

Bei Problemen:
- Hostinger Support: https://www.hostinger.com/support
- Hostinger Tutorials: https://www.hostinger.com/tutorials
- Logs prüfen: `pm2 logs`

## ✅ Deployment-Checkliste

- [ ] Hostinger Panel Login
- [ ] SSH-Zugang aktiviert
- [ ] Repository geklont
- [ ] Node.js Version eingestellt (18.x+)
- [ ] .env Datei konfiguriert
- [ ] Datenbank erstellt
- [ ] Dependencies installiert
- [ ] Frontend gebaut
- [ ] Backend gestartet
- [ ] PM2 konfiguriert
- [ ] Reverse Proxy eingerichtet
- [ ] SSL aktiviert
- [ ] Test: https://aivid.ch/generator funktioniert
