from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class AnalyzeDealRequest(BaseModel):
    acquirer: str = Field(..., min_length=1, max_length=255)
    target: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., min_length=1, max_length=100)
    deal_value_usd: int = Field(..., gt=0)
    premium_paid: Optional[float] = Field(default=0.35, ge=0, le=5)
    cross_border: Optional[bool] = False


class KeyMetrics(BaseModel):
    deal_value_usd: int
    industry: Optional[str] = None
    ml_success_probability: float
    sentiment_score: float
    expected_npv: int
    irr_median: float
    var_95: int
    prob_npv_positive: float
    npv_p50: int
    upside_p90: int
    downside_p10: int
    confidence_band_p25_p75: int


class AnalyzeDealResponse(BaseModel):
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
    analyzed_at: str