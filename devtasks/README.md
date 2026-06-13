# DevTasks

Open-source task management SaaS. Portable, containerized, deployable anywhere.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + SQLAlchemy + PostgreSQL |
| Frontend | React + Vite |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Infra | Docker Compose |

## Quickstart

```bash
git clone <repo>
cd devtasks
cp .env.example .env          # edit JWT_SECRET and passwords
docker compose up -d
```

- Frontend → http://localhost:3000  
- Backend API → http://localhost:8000  
- API Docs → http://localhost:8000/docs  

## Environment Variables

| Variable | Default | Required |
|----------|---------|----------|
| `POSTGRES_USER` | `postgres` | No |
| `POSTGRES_PASSWORD` | `postgrespassword` | **Change in prod** |
| `POSTGRES_DB` | `devtasks_db` | No |
| `DATABASE_URL` | auto-composed | No |
| `JWT_SECRET` | default | **Change in prod** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | No |

## API Endpoints

```
POST /auth/register   — create account
POST /auth/login      — get JWT token
GET  /users/me        — current user
GET  /users/          — list users (admin only)
GET  /tasks/          — list tasks (own, or all if admin)
POST /tasks/          — create task
GET  /tasks/{id}      — get task
PATCH /tasks/{id}     — update task
DELETE /tasks/{id}    — delete task
GET  /health          — health check
```

## Running Tests

```bash
cd backend
pip install -r requirements.txt
DATABASE_URL=sqlite:///./test.db JWT_SECRET=testsecret pytest tests/ -v
```

## Docker Commands

```bash
docker compose up -d          # start all services
docker compose logs -f        # view logs
docker compose down           # stop
docker compose down -v        # stop + remove volumes
```

## Architecture

```
devtasks/
├── .env.example
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py       ← FastAPI app + lifespan
│   │   ├── config.py     ← pydantic-settings
│   │   ├── database.py   ← SQLAlchemy session
│   │   ├── models.py     ← User + Task ORM models
│   │   ├── schemas.py    ← Pydantic request/response
│   │   ├── auth.py       ← JWT + bcrypt utilities
│   │   └── routers/
│   │       ├── auth.py   ← /auth/*
│   │       ├── tasks.py  ← /tasks/*
│   │       └── users.py  ← /users/*
│   └── tests/
│       └── test_api.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── src/
        ├── api.js          ← fetch wrapper
        ├── context/        ← AuthContext
        └── pages/          ← Login, Register, Dashboard
```
