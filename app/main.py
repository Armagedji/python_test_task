from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1 import endpoints as api_v1_endpoints
from app.elastic.search import close_es_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Асинхронный контекстный менеджер приложения.
    """
    yield
    await close_es_client()


app = FastAPI(
    title="Search Service",
    description="A simple search service for documents.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_v1_endpoints.router, prefix="/api/v1", tags=["documents"])


@app.get("/")
async def root():
    """
    Стандартный корневой эндпоинт.
    """
    return {"message": "Welcome to the Search Service"}
