# Nexus Warmup Dashboard (NWD)

SaaS app para warmup de emails y gestión de campañas cold email.

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12 · FastAPI · SQLAlchemy async |
| Base de datos | PostgreSQL 16 |
| Cola de tareas | Celery + Redis |
| Frontend | React · TypeScript · Vite · Tailwind CSS |
| Contenedores | Docker + Docker Compose |

## Inicio rápido

### Con Docker (recomendado)

```bash
# 1. Clonar y entrar al repo
git clone https://github.com/edgarfloresguerra2011-a11y/NWD.git
cd NWD

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus valores

# 3. Levantar todo
docker compose up --build
```

Servicios disponibles:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Flower (monitor Celery): http://localhost:5555

### Desarrollo local (sin Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # editar con DATABASE_URL local
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
cp .env.example .env.local   # editar VITE_API_URL si es necesario
npm install
npm run dev
```

## Migraciones de base de datos

```bash
# Crear nueva migración
cd backend
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head
```

## API

Swagger UI disponible en `http://localhost:8000/docs`

Endpoints principales:
- `POST /api/v1/auth/register` — Registro de usuario
- `POST /api/v1/auth/login` — Login, retorna JWT
- `GET /api/v1/accounts/` — Listar cuentas de email
- `POST /api/v1/accounts/` — Agregar cuenta de email
- `PATCH /api/v1/accounts/{id}/warmup` — Activar/desactivar warmup
- `GET /api/v1/campaigns/` — Listar campañas
- `POST /api/v1/campaigns/` — Crear campaña

## Arquitectura

```
NWD/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # Endpoints FastAPI
│   │   ├── core/           # Config, seguridad JWT
│   │   ├── db/             # Sesión SQLAlchemy
│   │   ├── models/         # Modelos ORM
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Celery tasks, lógica warmup
│   │   └── main.py
│   ├── alembic/            # Migraciones DB
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .env.example
├── .github/workflows/ci.yml
└── docker-compose.yml
```
