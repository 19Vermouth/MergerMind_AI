from typing import Any
from pydantic import BaseModel, Field
from datetime import date
from uuid import UUID


class MADeal(BaseModel):
    acquirer: str
    target: str
    industry: str
    deal_value_usd: int = Field(gt=0)
    announcement_date: date | None = None
    closing_date: date | None = None
    deal_status: str | None = None
    ev_revenue: float | None = None
    ev_ebitda: float | None = None
    premium_paid: float | None = None
    revenue_usd: int | None = None
    ebitda_usd: int | None = None
    synergy_revenue_usd: int | None = None
    synergy_cost_usd: int | None = None
    integration_cost_usd: int | None = None
    deal_success: bool | None = None
    source_url: str | None = None
    raw_json: dict[str, Any] | None = None


class NewsArticle(BaseModel):
    title: str
    content: str | None = None
    source: str | None = None
    author: str | None = None
    published_at: str | None = None
    url: str
    company_tag: str | None = None
    industry_tag: str | None = None


class DealFeatures(BaseModel):
    industry_similarity: float
    log_deal_size: float
    premium_paid: float
    ev_revenue: float | None
    ev_ebitda: float | None
    regulatory_complexity: float
    market_volatility: float
    historical_success_rate: float
    news_sentiment_score: float
    synergy_ratio: float


class MonteCarloResult(BaseModel):
    expected_npv: int
    irr_median: float
    probability_positive_npv: float
    var_95: int
    percentiles: dict[str, int]
    simulation_count: int


class DealAnalysisResult(BaseModel):
    deal_id: UUID
    acquirer: str
    target: str
    deal_value_usd: int
    success_probability: float
    sentiment_score: float
    expected_npv: int
    probability_positive_npv: float
    var_95: int
    irr_median: float
    recommendation: str
    confidence: str
    executive_summary: str
    risk_factors: list[str]
    key_metrics: dict[str, Any]
    simulation_percentiles: dict[str, int]