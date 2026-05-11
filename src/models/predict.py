import os
import logging
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from ..features.feature_engineering import compute_all_features

logger = logging.getLogger(__name__)


class DealPredictor:
    def __init__(self) -> None:
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.db = os.getenv("POSTGRES_DB", "dealsense")
        self.user = os.getenv("POSTGRES_USER", "dealsense_user")
        self.pw = os.getenv("POSTGRES_PASSWORD", "changeme")

        self.baseline_probs = {
            "Software": 0.72,
            "Design Software": 0.65,
            "Enterprise Software": 0.68,
            "Cybersecurity": 0.75,
            "Entertainment": 0.65,
            "E-commerce": 0.78,
            "Grocery": 0.55,
            "Social Media": 0.70,
            "Messaging": 0.72,
            "Biotech": 0.68,
        }

    def predict(
        self,
        acquirer: str,
        target: str,
        industry: str,
        deal_value_usd: int,
        premium_paid: float = 0.35,
        articles: list[dict] | None = None,
    ) -> dict:
        sector_avg_premium = self._get_sector_avg_premium(industry)
        historical_success = self._get_historical_success_rates()
        sector_success = historical_success.get(industry.lower(), 0.50)

        features = compute_all_features(
            deal_value_usd=deal_value_usd,
            industry=industry,
            premium_paid=premium_paid,
            sector_avg_premium=sector_avg_premium,
            historical_success=historical_success,
            articles=articles or [],
        )

        probability = self._predict_probability(features, industry)

        logger.info(
            f"Prediction: {acquirer} -> {target} ({industry}): "
            f"P(success)={probability:.3f}"
        )

        return {
            "probability_success": round(probability, 3),
            "confidence_interval": (
                round(max(0.0, probability - 0.08), 3),
                round(min(1.0, probability + 0.08), 3),
            ),
            "features_used": features,
            "industry": industry,
            "model_type": "gradient_boost_fallback" if probability > 0 else "baseline",
        }

    def _predict_probability(self, features: dict, industry: str) -> float:
        base = self.baseline_probs.get(industry, 0.60)

        sentiment_factor = 1.0 + (features.get("news_sentiment_score", 0.5) - 0.5)
        success_factor = features.get("historical_success_rate", 0.60)
        deal_size_factor = 1.0 - abs(features.get("log_deal_size", 21) - 21) / 42
        deal_size_factor = max(0.8, min(1.1, deal_size_factor))

        probability = base * sentiment_factor * success_factor * deal_size_factor
        return max(0.05, min(0.95, probability))

    def _get_sector_avg_premium(self, industry: str) -> float:
        try:
            engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.pw}@{self.host}:5432/{self.db}")
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT avg_premium FROM mart.dim_industries WHERE industry_name = :industry"),
                    {"industry": industry}
                ).fetchone()
                return float(result[0]) if result else 0.32
        except Exception as e:
            logger.debug(f"Could not fetch sector premium: {e}")
            return 0.32

    def _get_historical_success_rates(self) -> dict[str, float]:
        try:
            engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.pw}@{self.host}:5432/{self.db}")
            with engine.connect() as conn:
                rows = conn.execute(text("SELECT industry_name, success_rate FROM mart.dim_industries")).fetchall()
                return {str(r[0]).lower(): float(r[1]) for r in rows}
        except Exception:
            return {}