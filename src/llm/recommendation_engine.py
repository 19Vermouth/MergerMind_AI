import logging
from typing import Any

from .providers import LLMManager, LLMResponse

logger = logging.getLogger(__name__)


def build_recommendation_prompt(
    acquirer: str,
    target: str,
    industry: str,
    deal_value_usd: int,
    ml_probability: float,
    sentiment_score: float,
    expected_npv: int,
    prob_npv: float,
    var_95: int,
    irr_median: float,
    recommendation: str,
    risk_factors: list[str],
    key_metrics: dict[str, Any],
) -> str:
    risks_text = "\n".join(f"  - {r}" for r in risk_factors[:5])
    metrics_lines = "\n".join(f"  - {k}: {v}" for k, v in key_metrics.items())

    prompt = f"""You are a senior M&A analyst at a leading investment bank. Analyze the following deal and generate an executive summary and investment recommendation.

**Deal Parameters:**
- Acquirer: {acquirer}
- Target: {target}
- Industry: {industry}
- Deal Value: ${deal_value_usd:,.0f}
- ML Success Probability: {ml_probability:.1%}
- Sentiment Score: {sentiment_score:.2f}/1.0
- Expected NPV: ${expected_npv:,.0f}
- Probability NPV > 0: {prob_npv:.1%}
- VaR (95%): ${var_95:,.0f}
- IRR Median: {irr_median:.1%}
- Recommendation: {recommendation}

**Risk Factors:**
{risks_text}

**Key Metrics:**
{metrics_lines}

**Instructions:**
1. Provide a 3-4 paragraph executive summary
2. Assess strategic rationale
3. Identify top 3 risks
4. State your investment recommendation with justification
5. Include a brief note on comparable transactions

Be concise, professional, and specific. Use financial terminology appropriate for C-suite executives."""

    return prompt


class RecommendationEngine:
    def __init__(self) -> None:
        self.llm = LLMManager()
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    async def generate(
        self,
        acquirer: str,
        target: str,
        industry: str,
        deal_value_usd: int,
        ml_probability: float,
        sentiment_score: float,
        expected_npv: int,
        prob_npv: float,
        var_95: int,
        irr_median: float,
        recommendation: str,
        risk_factors: list[str],
        key_metrics: dict[str, Any],
    ) -> str:
        prompt = build_recommendation_prompt(
            acquirer=acquirer,
            target=target,
            industry=industry,
            deal_value_usd=deal_value_usd,
            ml_probability=ml_probability,
            sentiment_score=sentiment_score,
            expected_npv=expected_npv,
            prob_npv=prob_npv,
            var_95=var_95,
            irr_median=irr_median,
            recommendation=recommendation,
            risk_factors=risk_factors,
            key_metrics=key_metrics,
        )

        try:
            primary = os.getenv("LLM_PRIMARY_PROVIDER", "groq")
            response = await self.llm.generate(
                prompt,
                provider=primary,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            logger.info(
                f"LLM generated recommendation via {response.provider} "
                f"({response.latency_ms}ms, {response.tokens_used} tokens)"
            )
            return response.content
        except Exception as e:
            logger.error(f"LLM recommendation generation failed: {e}")
            return self._fallback_summary(
                acquirer, target, deal_value_usd, recommendation, expected_npv, prob_npv
            )

    def _fallback_summary(
        self,
        acquirer: str,
        target: str,
        deal_value_usd: int,
        recommendation: str,
        expected_npv: int,
        prob_npv: float,
    ) -> str:
        return (
            f"**Executive Summary — {acquirer} / {target}**\n\n"
            f"Based on our quantitative analysis of this ${deal_value_usd:,.0f} transaction, "
            f"the recommended course of action is **{recommendation}**. "
            f"With an expected NPV of ${expected_npv:,.0f} and a {prob_npv:.1%} probability "
            f"of creating shareholder value, this deal warrants careful consideration. "
            f"The analysis incorporates historical deal patterns, market sentiment, and "
            f"Monte Carlo simulation of 50,000 scenarios. "
            f"Please review the detailed risk factors and comparable transaction analysis "
            f"before proceeding with board-level discussions."
        )


import os