from fastapi import FastAPI
from app.routes import user_routes
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI CRUD - DevOS v1")

app.include_router(user_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI CRUD DevOS v1"}
