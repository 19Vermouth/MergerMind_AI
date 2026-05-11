import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


def compute_industry_similarity(
    target_industry: str,
    historical_industries: list[str],
) -> float:
    if not historical_industries:
        return 0.5
    matches = sum(1 for ind in historical_industries if ind.lower() in target_industry.lower())
    return min(matches / max(len(historical_industries), 1), 1.0)


def compute_premium_score(
    premium_paid: float,
    sector_avg_premium: float,
) -> float:
    if sector_avg_premium <= 0:
        return 0.5
    ratio = premium_paid / sector_avg_premium
    return max(0.0, min(1.0, 1.0 - (ratio - 1.0) / 2.0))


def compute_regulatory_complexity(
    deal_value_usd: int,
    industry: str,
    cross_border: bool = False,
) -> float:
    base_complexity = min(deal_value_usd / 10_000_000_000, 1.0)

    regulated_industries = [
        "banking", "financial", "healthcare", "biotech", "pharma",
        "telecom", "media", "defense", "energy",
    ]
    industry_mult = 1.3 if any(r in industry.lower() for r in regulated_industries) else 1.0

    cross_border_mult = 1.2 if cross_border else 1.0

    return min(base_complexity * industry_mult * cross_border_mult, 1.0)


def compute_market_volatility(vix: float = 20.0) -> float:
    return min(vix / 40.0, 1.0)


def compute_sector_success_rate(
    industry: str,
    historical_success: dict[str, float],
) -> float:
    return historical_success.get(industry.lower(), 0.50)


def compute_sentiment_from_articles(articles: list[dict]) -> float:
    if not articles:
        return 0.5
    scores = [a.get("sentiment_score", 0.0) for a in articles]
    return float(np.mean(scores)) if scores else 0.5


def compute_all_features(
    deal_value_usd: int,
    industry: str,
    premium_paid: float,
    sector_avg_premium: float,
    historical_success: dict[str, float],
    articles: list[dict],
    vix: float = 20.0,
    cross_border: bool = False,
) -> dict[str, float]:
    return {
        "log_deal_size": np.log(deal_value_usd) if deal_value_usd > 0 else 0.0,
        "industry_similarity": 0.6,
        "premium_score": compute_premium_score(premium_paid, sector_avg_premium),
        "regulatory_complexity": compute_regulatory_complexity(deal_value_usd, industry, cross_border),
        "market_volatility": compute_market_volatility(vix),
        "historical_success_rate": compute_sector_success_rate(industry, historical_success),
        "news_sentiment_score": compute_sentiment_from_articles(articles),
        "synergy_ratio": 0.1,
        "deal_size_percentile": 0.5,
        "acquirer_track_record": 0.7,
        "target_financial_health": 0.6,
    }