from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import logging
import uuid
from typing import Any

from .routes import deals, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DealSense AI API starting up...")
    yield
    logger.info("DealSense AI API shutting down...")


app = FastAPI(
    title="DealSense AI",
    description="AI-Powered M&A Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deals.router, prefix="/api/v1", tags=["deals"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    return {
        "name": "DealSense AI",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }