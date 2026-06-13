from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, get_engine
from app.routers import auth, tasks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DevTasks API",
    version="1.0.0",
    description="Task management SaaS — portable, containerized, open source",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}
