import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ScoringWeights:
    ml: float = 0.35
    sentiment: float = 0.25
    simulation: float = 0.40


@dataclass
class DealScore:
    raw_score: float
    normalized_score: float
    recommendation: str
    confidence: str
    risk_factors: list[str]
    key_metrics: dict


class DealScorer:
    def __init__(self, weights: Optional[ScoringWeights] = None) -> None:
        self.weights = weights or ScoringWeights()

    def score(
        self,
        ml_probability: float,
        sentiment_score: float,
        simulation_result: dict,
        deal_value_usd: int,
        industry: Optional[str] = None,
    ) -> DealScore:
        sim_score = self._compute_simulation_score(simulation_result)
        raw = (
            self.weights.ml * ml_probability
            + self.weights.sentiment * sentiment_score
            + self.weights.simulation * sim_score
        )
        normalized = min(max(raw, 0.0), 1.0)

        recommendation, confidence = self._get_recommendation(normalized, simulation_result)
        risk_factors = self._identify_risk_factors(
            ml_probability, sentiment_score, simulation_result, deal_value_usd
        )
        key_metrics = self._build_key_metrics(
            ml_probability, sentiment_score, simulation_result, deal_value_usd, industry
        )

        logger.info(
            f"Deal scored: raw={raw:.3f}, normalized={normalized:.3f}, "
            f"recommendation={recommendation}, confidence={confidence}"
        )

        return DealScore(
            raw_score=raw,
            normalized_score=normalized,
            recommendation=recommendation,
            confidence=confidence,
            risk_factors=risk_factors,
            key_metrics=key_metrics,
        )

    def _compute_simulation_score(self, sim_result: dict) -> float:
        prob_positive = sim_result.get("probability_positive_npv", 0.5)
        expected_npv = sim_result.get("expected_npv", 0)
        var_95 = sim_result.get("var_95", 0)
        npv_std = sim_result.get("npv_std", 1)

        prob_component = prob_positive
        value_component = 0.5 + 0.5 * (expected_npv / (abs(expected_npv) + npv_std + 1))
        risk_component = 0.5 + 0.5 * (var_95 / (abs(var_95) + npv_std + 1)) if var_95 > 0 else 0.3

        return (prob_component * 0.5 + value_component * 0.3 + risk_component * 0.2)

    def _get_recommendation(self, score: float, sim_result: dict) -> tuple[str, str]:
        prob_positive = sim_result.get("probability_positive_npv", 0.5)
        var_95 = sim_result.get("var_95", 0)

        if score >= 0.75 and prob_positive >= 0.70 and var_95 > -deal_value_usd * 0.15:
            return "PROCEED", "HIGH"
        elif score >= 0.55:
            return "PROCEED", "MEDIUM"
        elif score >= 0.40:
            return "NEGOTIATE", "MEDIUM"
        elif score >= 0.25:
            return "NEGOTIATE", "LOW"
        else:
            return "REJECT", "HIGH"

    def _identify_risk_factors(
        self,
        ml_prob: float,
        sentiment: float,
        sim_result: dict,
        deal_value: int,
    ) -> list[str]:
        risks = []

        if ml_prob < 0.50:
            risks.append("Low historical success rate for similar deals")
        if sentiment < 0.30:
            risks.append("Negative or neutral market sentiment")
        if sim_result.get("probability_positive_npv", 1.0) < 0.50:
            risks.append("More likely to destroy value than create it")
        if sim_result.get("var_95", 0) < -deal_value * 0.10:
            risks.append("Significant downside risk (VaR above threshold)")
        if sim_result.get("irr_median", 0) < 0.10:
            risks.append("Internal rate of return below cost of capital")
        if deal_value > 10_000_000_000:
            risks.append("Large deal size increases integration complexity")
        if sim_result.get("percentiles", {}).get("p10", 0) < 0:
            risks.append("10th percentile NPV is negative (downside scenario)")

        return risks[:5]

    def _build_key_metrics(
        self,
        ml_prob: float,
        sentiment: float,
        sim_result: dict,
        deal_value: int,
        industry: str | None,
    ) -> dict:
        percentiles = sim_result.get("percentiles", {})
        return {
            "deal_value_usd": deal_value,
            "industry": industry,
            "ml_success_probability": round(ml_prob, 3),
            "sentiment_score": round(sentiment, 3),
            "expected_npv": sim_result.get("expected_npv", 0),
            "irr_median": round(sim_result.get("irr_median", 0), 3),
            "var_95": sim_result.get("var_95", 0),
            "prob_npv_positive": round(sim_result.get("probability_positive_npv", 0), 3),
            "npv_p50": percentiles.get("p50", 0),
            "upside_p90": percentiles.get("p90", 0),
            "downside_p10": percentiles.get("p10", 0),
            "confidence_band_p25_p75": percentiles.get("p75", 0) - percentiles.get("p25", 0),
        }