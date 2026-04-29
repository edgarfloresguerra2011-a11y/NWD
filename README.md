# Nexus Warmup Dashboard (NWD)

SaaS app for email warm-up and cold email campaign management.

## Stack
- **Backend**: Python FastAPI + SQLite + SQLAlchemy async
- **Frontend**: React TypeScript + Vite + Tailwind CSS

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9876
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API
Swagger docs at `http://localhost:9876/docs`
