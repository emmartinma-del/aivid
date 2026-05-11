# 🚀 Quick Start - AIvid unter www.aivid.ch/generator

## ✅ Was wurde bereits gemacht

1. ✅ GitHub Branch `claude/app-store-video-generator-9L5mk` geklont
2. ✅ Next.js für `/generator` Basepath konfiguriert
3. ✅ `.env` Datei mit Production-URLs erstellt
4. ✅ Umfassende Deployment-Dokumentation erstellt
5. ✅ Änderungen committed und gepusht

## 📍 Nächste Schritte

### Schritt 1: API-Keys konfigurieren

Bearbeiten Sie die `.env` Datei und fügen Sie Ihre echten API-Keys ein:

```bash
cd /Users/admin/Applications/AIVID/aivid-website
nano .env
```

**Erforderliche Keys:**
- `ANTHROPIC_API_KEY` - Für AI-Skript-Generierung (Claude)
- `STRIPE_SECRET_KEY` - Für Zahlungsabwicklung
- `STRIPE_WEBHOOK_SECRET` - Für Stripe Webhooks
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` - Stripe Public Key
- `OPENAI_API_KEY` oder `ELEVENLABS_API_KEY` - Für Voiceover-Generierung

**Secrets generieren:**
```bash
# JWT Secret
openssl rand -base64 32

# NextAuth Secret
openssl rand -base64 32
```

### Schritt 2: Lokales Testing (Optional)

Testen Sie die Applikation lokal mit Docker:

```bash
cd /Users/admin/Applications/AIVID/aivid-website
docker-compose up
```

Öffnen Sie dann:
- Frontend: http://localhost:3000/generator
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin / minioadmin123)

### Schritt 3: Deployment wählen

Sie haben drei Optionen:

#### Option A: Vercel (Empfohlen für Frontend)
```bash
cd apps/web
npm install -g vercel
vercel login
vercel
```

Dann in Vercel Dashboard:
- Domain konfigurieren: `aivid.ch/generator`
- Environment Variables setzen
- Deploy mit `vercel --prod`

#### Option B: Docker auf eigenem Server
```bash
# Auf Ihrem Server
git clone -b claude/app-store-video-generator-9L5mk https://github.com/emmartinma-del/aivid.git
cd aivid
cp .env.example .env
# .env bearbeiten
docker-compose up -d
```

Dann Nginx/Apache Reverse Proxy konfigurieren (siehe DEPLOYMENT.md)

#### Option C: AWS (Backend) + Vercel (Frontend)
- Backend auf AWS ECS Fargate
- Frontend auf Vercel
- Siehe detaillierte Anleitung in DEPLOYMENT.md

### Schritt 4: Domain & SSL konfigurieren

**DNS-Einträge:**
- A-Record: `aivid.ch` → Ihre Server-IP
- CNAME: `api.aivid.ch` → Ihre API-Server-IP oder Load Balancer

**SSL-Zertifikat (Let's Encrypt):**
```bash
sudo certbot --nginx -d aivid.ch -d api.aivid.ch
```

### Schritt 5: Datenbank Setup

```bash
cd apps/api
# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Migrations ausführen
alembic upgrade head
```

### Schritt 6: Testen

Nach dem Deployment:
- ✅ Frontend erreichbar: https://aivid.ch/generator
- ✅ API erreichbar: https://api.aivid.ch/docs
- ✅ Video-Generierung funktioniert
- ✅ Stripe-Zahlungen funktionieren

## 📋 Deployment-Checkliste

Vor dem Production-Deployment:

- [ ] Alle API-Keys in `.env` eingetragen
- [ ] JWT_SECRET und NEXTAUTH_SECRET generiert
- [ ] PostgreSQL Datenbank erstellt
- [ ] Redis Server läuft
- [ ] S3 Buckets erstellt (aivid-uploads, aivid-outputs)
- [ ] Domain DNS konfiguriert
- [ ] SSL-Zertifikat installiert
- [ ] Reverse Proxy konfiguriert (Nginx/Apache)
- [ ] Database Migrations ausgeführt
- [ ] Stripe Webhooks konfiguriert
- [ ] Backup-Strategie implementiert
- [ ] Monitoring eingerichtet

## 🔧 Wichtige Dateien

- `DEPLOYMENT.md` - Vollständige Deployment-Anleitung
- `.env` - Umgebungsvariablen (NICHT committen!)
- `apps/web/next.config.mjs` - Next.js Konfiguration mit /generator Basepath
- `docker-compose.yml` - Docker Setup für lokale Entwicklung

## 📞 Hilfe benötigt?

Siehe `DEPLOYMENT.md` für:
- Detaillierte Deployment-Optionen
- Infrastruktur-Anforderungen
- Troubleshooting
- Monitoring & Logs

## 🎯 Zusammenfassung

Die Applikation ist jetzt bereit für das Deployment unter `www.aivid.ch/generator`:

1. **Konfiguration**: Next.js läuft unter `/generator` Basepath
2. **Code**: Alle Änderungen sind im Branch `claude/app-store-video-generator-9L5mk`
3. **Dokumentation**: Vollständige Anleitung in `DEPLOYMENT.md`
4. **Nächster Schritt**: API-Keys konfigurieren und Deployment-Option wählen

Viel Erfolg! 🚀
