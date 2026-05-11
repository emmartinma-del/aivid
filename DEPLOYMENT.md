# Deployment-Anleitung für AIvid unter www.aivid.ch/generator

## 📋 Übersicht

Diese Anleitung beschreibt, wie die AIvid App Store Video Generator Applikation unter `www.aivid.ch/generator` deployed wird.

## ✅ Bereits durchgeführte Konfigurationen

### 1. Next.js Basepath-Konfiguration
Die `apps/web/next.config.mjs` wurde angepasst, um unter `/generator` zu laufen:
```javascript
basePath: "/generator",
assetPrefix: "/generator",
```

### 2. Umgebungsvariablen
Eine `.env` Datei wurde erstellt mit Production-URLs:
- `NEXTAUTH_URL=https://aivid.ch/generator`
- `NEXT_PUBLIC_API_URL=https://api.aivid.ch`
- `FRONTEND_URL=https://aivid.ch/generator`

## 🚀 Deployment-Optionen

### Option 1: Vercel Deployment (Empfohlen für Frontend)

#### Schritt 1: Vercel-Projekt erstellen
```bash
cd /Users/admin/Applications/AIVID/aivid-website/apps/web
npm install -g vercel
vercel login
vercel
```

#### Schritt 2: Umgebungsvariablen in Vercel setzen
Im Vercel Dashboard unter Settings → Environment Variables:
- `NEXT_PUBLIC_API_URL` → `https://api.aivid.ch`
- `NEXTAUTH_URL` → `https://aivid.ch/generator`
- `NEXTAUTH_SECRET` → (generieren mit `openssl rand -base64 32`)
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` → Ihr Stripe Public Key

#### Schritt 3: Custom Domain konfigurieren
In Vercel Settings → Domains:
- Domain hinzufügen: `aivid.ch`
- Subdomain Path: `/generator`

#### Schritt 4: Build & Deploy
```bash
vercel --prod
```

### Option 2: Docker Deployment (Vollständige Stack)

#### Schritt 1: Umgebungsvariablen konfigurieren
Bearbeiten Sie die `.env` Datei und fügen Sie echte API-Keys ein:
```bash
cd /Users/admin/Applications/AIVID/aivid-website
nano .env
```

Erforderliche Keys:
- `ANTHROPIC_API_KEY` - Für AI-Skript-Generierung
- `STRIPE_SECRET_KEY` - Für Zahlungen
- `OPENAI_API_KEY` oder `ELEVENLABS_API_KEY` - Für Voiceover

#### Schritt 2: Docker Compose starten
```bash
docker-compose up -d
```

Dies startet:
- Frontend auf Port 3000
- API auf Port 8000
- PostgreSQL Datenbank
- Redis für Job Queue
- MinIO für lokalen Storage
- Celery Worker für Video-Generierung

#### Schritt 3: Reverse Proxy konfigurieren (Nginx/Apache)

**Nginx Konfiguration:**
```nginx
# Frontend unter /generator
location /generator {
    proxy_pass http://localhost:3000/generator;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}

# API unter /api oder api.aivid.ch
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Apache Konfiguration:**
```apache
# Frontend unter /generator
ProxyPass /generator http://localhost:3000/generator
ProxyPassReverse /generator http://localhost:3000/generator

# API
ProxyPass /api http://localhost:8000
ProxyPassReverse /api http://localhost:8000
```

### Option 3: Separate Backend/Frontend Deployment

#### Backend (FastAPI + Worker)
Laut README wird das Backend auf AWS ECS Fargate deployed:

1. **Docker Images bauen:**
```bash
cd apps/api
docker build -t aivid-api:latest -f Dockerfile .
docker build -t aivid-worker:latest -f Dockerfile.worker .
```

2. **Zu AWS ECR pushen:**
```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
docker tag aivid-api:latest YOUR_ECR_URL/aivid-api:latest
docker tag aivid-worker:latest YOUR_ECR_URL/aivid-worker:latest
docker push YOUR_ECR_URL/aivid-api:latest
docker push YOUR_ECR_URL/aivid-worker:latest
```

3. **ECS Task Definitions erstellen** mit den Umgebungsvariablen aus `.env`

#### Frontend (Next.js)
Siehe Option 1 (Vercel) oder bauen Sie ein statisches Export:

```bash
cd apps/web
npm install
npm run build
npm run start
```

## 🔧 Infrastruktur-Anforderungen

### Datenbank
- PostgreSQL 16
- Verbindung: `DATABASE_URL` in `.env`
- Migrations ausführen:
```bash
cd apps/api
alembic upgrade head
```

### Redis
- Für Celery Job Queue
- `REDIS_URL` in `.env`

### S3 Storage
- AWS S3 oder MinIO
- Zwei Buckets: `aivid-uploads` und `aivid-outputs`
- Konfiguration in `.env`:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `S3_UPLOADS_BUCKET`
  - `S3_OUTPUTS_BUCKET`

### FFmpeg
- Muss auf dem Worker-Server installiert sein
- Wird für Video-Komposition verwendet

## 🔐 Sicherheit

### Secrets generieren
```bash
# JWT Secret
openssl rand -base64 32

# NextAuth Secret
openssl rand -base64 32
```

### SSL/TLS
- Verwenden Sie Let's Encrypt für HTTPS
- Certbot Installation:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d aivid.ch
```

## 🧪 Testing

### Lokales Testing
```bash
cd /Users/admin/Applications/AIVID/aivid-website
docker-compose up
```

Dann öffnen Sie:
- Frontend: http://localhost:3000/generator
- API Docs: http://localhost:8000/docs

### Production Testing
Nach dem Deployment:
- Frontend: https://aivid.ch/generator
- API Health Check: https://api.aivid.ch/health (falls implementiert)

## 📊 Monitoring

### Logs überwachen
```bash
# Docker Logs
docker-compose logs -f web
docker-compose logs -f api
docker-compose logs -f worker

# Vercel Logs
vercel logs
```

## 🔄 Updates & Rollbacks

### Update durchführen
```bash
cd /Users/admin/Applications/AIVID/aivid-website
git pull origin claude/app-store-video-generator-9L5mk
docker-compose down
docker-compose build
docker-compose up -d
```

### Rollback
```bash
git checkout <previous-commit>
docker-compose down
docker-compose build
docker-compose up -d
```

## 📝 Checkliste vor Production-Deployment

- [ ] Alle API-Keys in `.env` eingetragen
- [ ] JWT_SECRET und NEXTAUTH_SECRET generiert
- [ ] PostgreSQL Datenbank erstellt
- [ ] Redis Server läuft
- [ ] S3 Buckets erstellt und konfiguriert
- [ ] Domain DNS konfiguriert (A-Record auf Server-IP)
- [ ] SSL-Zertifikat installiert
- [ ] Nginx/Apache Reverse Proxy konfiguriert
- [ ] Database Migrations ausgeführt
- [ ] Stripe Webhooks konfiguriert
- [ ] Backup-Strategie implementiert
- [ ] Monitoring eingerichtet

## 🆘 Troubleshooting

### Frontend lädt nicht
- Prüfen Sie `basePath` in `next.config.mjs`
- Prüfen Sie Nginx/Apache Proxy-Konfiguration
- Logs: `docker-compose logs web`

### API nicht erreichbar
- Prüfen Sie `NEXT_PUBLIC_API_URL` in Frontend
- Prüfen Sie CORS-Einstellungen in FastAPI
- Logs: `docker-compose logs api`

### Videos werden nicht generiert
- Prüfen Sie Worker-Logs: `docker-compose logs worker`
- Prüfen Sie Redis-Verbindung
- Prüfen Sie FFmpeg-Installation
- Prüfen Sie API-Keys (Anthropic, ElevenLabs/OpenAI)

## 📞 Support

Bei Fragen oder Problemen:
- GitHub Issues: https://github.com/emmartinma-del/aivid/issues
- Email: support@aivid.ch
