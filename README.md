# AIvid – Automated App Store Video Generator

AI-powered platform that generates professional App Store and Google Play preview videos for mobile app publishers.

## Quick Start

```bash
cp .env.example .env
# Fill in ANTHROPIC_API_KEY and STRIPE_SECRET_KEY at minimum
docker-compose up
```

- Frontend: http://localhost:3000
- API: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin / minioadmin123)

## Architecture

| Layer | Tech |
|---|---|
| Frontend | Next.js 14, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.12) |
| Job Queue | Celery + Redis |
| Database | PostgreSQL 16 |
| Storage | S3 / MinIO (local) |
| Video | FFmpeg |
| AI Script | Anthropic Claude |
| Voiceover | ElevenLabs / OpenAI TTS |

## Development

```bash
# API only
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Worker only
celery -A app.worker.celery_app worker --loglevel=info

# Frontend only
cd apps/web
npm install
npm run dev
```

## Deployment

- Frontend → Vercel (auto-deploy from main)
- API + Worker → AWS ECS Fargate
- Database → AWS RDS PostgreSQL
- Storage → AWS S3 + CloudFront
