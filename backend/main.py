import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import init_db
from backend.api.router import api_router

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    if settings.debug:
        await init_db()
    yield
    # shutdown (nothing to clean up for now)


app = FastAPI(
    title="Cortex",
    description="Intelligent document processing pipeline",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"name": "cortex", "version": "0.1.0", "docs": "/docs"}
# structured json logs for easier debugging
# OpenAPI examples for all endpoints, better descriptions
