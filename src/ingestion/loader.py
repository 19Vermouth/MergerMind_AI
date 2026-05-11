import os
import json
import logging
from datetime import datetime
from typing import BinaryIO

import boto3
from minio import Minio
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .schemas import MADeal, NewsArticle

logger = logging.getLogger(__name__)


class MinIOClient:
    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = access_key or os.getenv("MINIO_ROOT_USER", "minioadmin")
        self.secret_key = secret_key or os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
        self.client = Minio(self.endpoint, self.access_key, self.secret_key, secure=False)
        self.bucket_raw = os.getenv("MINIO_BUCKET_RAW", "dealsense-raw")
        self.bucket_processed = os.getenv("MINIO_BUCKET_PROCESSED", "dealsense-processed")
        self.bucket_models = os.getenv("MINIO_BUCKET_MODELS", "dealsense-models")

    def upload_deal_json(self, deal: MADeal, prefix: str = "deals") -> str:
        timestamp = datetime.utcnow().strftime("%Y/%m/%d/%H%M%S")
        key = f"{prefix}/{timestamp}/{deal.target}_{datetime.utcnow().strftime('%f')}.json"
        data = deal.model_dump_json().encode("utf-8")
        self.client.put_object(self.bucket_raw, key, data, len(data), content_type="application/json")
        logger.info(f"Uploaded deal to MinIO: {key}")
        return key

    def upload_file(self, bucket: str, key: str, data: BinaryIO, content_type: str = "application/octet-stream") -> None:
        self.client.put_object(bucket, key, data, -1, content_type=content_type)

    def download_json(self, bucket: str, key: str) -> dict:
        data = self.client.get_object(bucket, key)
        return json.loads(data.read().decode("utf-8"))

    def list_objects(self, bucket: str, prefix: str = "") -> list[str]:
        return [obj.object_name for obj in self.client.list_objects(bucket, prefix=prefix, recursive=True)]

    def ensure_buckets(self) -> None:
        for bucket in [self.bucket_raw, self.bucket_processed, self.bucket_models]:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"Created bucket: {bucket}")


class PostgresLoader:
    def __init__(
        self,
        host: str | None = None,
        dbname: str | None = None,
        user: str | None = None,
        password: str | None = None,
        port: int = 5432,
    ) -> None:
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.dbname = dbname or os.getenv("POSTGRES_DB", "dealsense")
        self.user = user or os.getenv("POSTGRES_USER", "dealsense_user")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "changeme")
        self.engine: Engine = create_engine(
            f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{port}/{self.dbname}"
        )

    def load_deal(self, deal: MADeal) -> int | None:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO raw.ma_deals (
                        acquirer, target, industry, deal_value_usd,
                        announcement_date, closing_date, deal_status,
                        ev_revenue, ev_ebitda, premium_paid,
                        revenue_usd, ebitda_usd, synergy_revenue_usd,
                        synergy_cost_usd, integration_cost_usd,
                        deal_success, source_url, raw_json
                    ) VALUES (
                        :acquirer, :target, :industry, :deal_value_usd,
                        :announcement_date, :closing_date, :deal_status,
                        :ev_revenue, :ev_ebitda, :premium_paid,
                        :revenue_usd, :ebitda_usd, :synergy_revenue_usd,
                        :synergy_cost_usd, :integration_cost_usd,
                        :deal_success, :source_url, :raw_json
                    ) RETURNING id
                """),
                {
                    "acquirer": deal.acquirer,
                    "target": deal.target,
                    "industry": deal.industry,
                    "deal_value_usd": deal.deal_value_usd,
                    "announcement_date": deal.announcement_date,
                    "closing_date": deal.closing_date,
                    "deal_status": deal.deal_status,
                    "ev_revenue": deal.ev_revenue,
                    "ev_ebitda": deal.ev_ebitda,
                    "premium_paid": deal.premium_paid,
                    "revenue_usd": deal.revenue_usd,
                    "ebitda_usd": deal.ebitda_usd,
                    "synergy_revenue_usd": deal.synergy_revenue_usd,
                    "synergy_cost_usd": deal.synergy_cost_usd,
                    "integration_cost_usd": deal.integration_cost_usd,
                    "deal_success": deal.deal_success,
                    "source_url": deal.source_url,
                    "raw_json": json.dumps(deal.raw_json) if deal.raw_json else None,
                },
            )
            row = result.fetchone()
            conn.commit()
            return row[0] if row else None

    def batch_load_deals(self, deals: list[MADeal], schema: str = "raw") -> int:
        count = 0
        for deal in deals:
            try:
                self.load_deal(deal)
                count += 1
            except Exception as e:
                logger.error(f"Failed to load deal {deal.target}: {e}")
        return count

    def fetch_deals(self, limit: int = 100, industry: str | None = None) -> list[dict]:
        where = f"WHERE industry = '{industry}'" if industry else ""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM raw.ma_deals {where} LIMIT :limit"), {"limit": limit})
            return [dict(row._mapping) for row in result.fetchall()]

    def health_check(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False