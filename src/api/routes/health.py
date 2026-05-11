from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    postgres_ok = False
    minio_ok = False

    try:
        from sqlalchemy import create_engine, text
        host = os.getenv("POSTGRES_HOST", "localhost")
        db = os.getenv("POSTGRES_DB", "dealsense")
        user = os.getenv("POSTGRES_USER", "dealsense_user")
        pw = os.getenv("POSTGRES_PASSWORD", "changeme")
        engine = create_engine(f"postgresql+psycopg2://{user}:{pw}@{host}:5432/{db}")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        postgres_ok = True
    except Exception:
        pass

    try:
        from minio import Minio
        endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
        secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
        client = Minio(endpoint, access_key, secret_key, secure=False)
        buckets = client.list_buckets()
        minio_ok = True
    except Exception:
        pass

    all_ok = postgres_ok and minio_ok

    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        version="1.0.0",
        services={
            "postgres": "up" if postgres_ok else "down",
            "minio": "up" if minio_ok else "down",
        }
    )