from fastapi import FastAPI
from .database import Base, engine
from .routes import router

app = FastAPI(title="Task Manager API")

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")
