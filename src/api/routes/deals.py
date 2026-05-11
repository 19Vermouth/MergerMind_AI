import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlalchemy import create_engine, text

from ..models import AnalyzeDealRequest, AnalyzeDealResponse

logger = logging.getLogger(__name__)
router = APIRouter()

host = os.getenv("POSTGRES_HOST", "localhost")
db = os.getenv("POSTGRES_DB", "dealsense")
user = os.getenv("POSTGRES_USER", "dealsense_user")
pw = os.getenv("POSTGRES_PASSWORD", "changeme")


def compute_sentiment(acquirer: str, target: str) -> float:
    try:
        engine = create_engine(f"postgresql+psycopg2://{user}:{pw}@{host}:5432/{db}")
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT AVG(sentiment_score) FROM staging.stg_news_sentiment
                    WHERE company_tag IN (:acquirer, :target)
                """),
                {"acquirer": acquirer, "target": target}
            ).fetchone()
            score = result[0] if result and result[0] is not None else 0.5
            return float(score)
    except Exception:
        return 0.5


def store_analysis_result(result: dict) -> None:
    try:
        engine = create_engine(f"postgresql+psycopg2://{user}:{pw}@{host}:5432/{db}")
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO mart.deal_analysis_results (
                        deal_id, acquirer, target, industry, deal_value_usd,
                        success_probability, sentiment_score, expected_npv,
                        probability_positive_npv, var_95, irr_median,
                        recommendation, confidence, executive_summary,
                        risk_factors, key_metrics, simulation_results
                    ) VALUES (
                        :deal_id, :acquirer, :target, :industry, :deal_value_usd,
                        :success_probability, :sentiment_score, :expected_npv,
                        :probability_positive_npv, :var_95, :irr_median,
                        :recommendation, :confidence, :executive_summary,
                        :risk_factors, :key_metrics, :simulation_results
                    )
                """),
                {
                    "deal_id": result["deal_id"],
                    "acquirer": result["acquirer"],
                    "target": result["target"],
                    "industry": result.get("industry", "Unknown"),
                    "deal_value_usd": result["deal_value_usd"],
                    "success_probability": result["success_probability"],
                    "sentiment_score": result["sentiment_score"],
                    "expected_npv": result["expected_npv"],
                    "probability_positive_npv": result["probability_positive_npv"],
                    "var_95": result["var_95"],
                    "irr_median": result["irr_median"],
                    "recommendation": result["recommendation"],
                    "confidence": result["confidence"],
                    "executive_summary": result["executive_summary"],
                    "risk_factors": result["risk_factors"],
                    "key_metrics": result["key_metrics"],
                    "simulation_results": result.get("simulation_results", {}),
                }
            )
            conn.commit()
            logger.info(f"Stored analysis result for deal {result['deal_id']}")
    except Exception as e:
        logger.error(f"Failed to store analysis result: {e}")


async def run_analysis(request: AnalyzeDealRequest) -> dict:
    from ...simulation.monte_carlo import run_monte_carlo
    from ...scoring.deal_scorer import DealScorer, ScoringWeights
    from ...llm.recommendation_engine import RecommendationEngine

    logger.info(f"Analyzing deal: {request.acquirer} -> {request.target}")

    ml_probability = 0.65
    sentiment_score = compute_sentiment(request.acquirer, request.target)
    simulation = run_monte_carlo(request.deal_value_usd, request.industry)

    weights = ScoringWeights(
        ml=float(os.getenv("MODEL_WEIGHT_ML", "0.35")),
        sentiment=float(os.getenv("MODEL_WEIGHT_SENTIMENT", "0.25")),
        simulation=float(os.getenv("MODEL_WEIGHT_SIMULATION", "0.40")),
    )
    scorer = DealScorer(weights=weights)
    score = scorer.score(
        ml_probability=ml_probability,
        sentiment_score=sentiment_score,
        simulation_result=simulation,
        deal_value_usd=request.deal_value_usd,
        industry=request.industry,
    )

    llm_engine = RecommendationEngine()
    executive_summary = await llm_engine.generate(
        acquirer=request.acquirer,
        target=request.target,
        industry=request.industry,
        deal_value_usd=request.deal_value_usd,
        ml_probability=ml_probability,
        sentiment_score=sentiment_score,
        expected_npv=simulation["expected_npv"],
        prob_npv=simulation["probability_positive_npv"],
        var_95=simulation["var_95"],
        irr_median=simulation["irr_median"],
        recommendation=score.recommendation,
        risk_factors=score.risk_factors,
        key_metrics=score.key_metrics,
    )

    return {
        "deal_id": uuid4(),
        "acquirer": request.acquirer,
        "target": request.target,
        "deal_value_usd": request.deal_value_usd,
        "industry": request.industry,
        "success_probability": ml_probability,
        "sentiment_score": round(sentiment_score, 3),
        "expected_npv": simulation["expected_npv"],
        "probability_positive_npv": round(simulation["probability_positive_npv"], 3),
        "var_95": simulation["var_95"],
        "irr_median": round(simulation["irr_median"], 3),
        "recommendation": score.recommendation,
        "confidence": score.confidence,
        "executive_summary": executive_summary,
        "risk_factors": score.risk_factors,
        "key_metrics": score.key_metrics,
        "simulation_percentiles": simulation["percentiles"],
        "simulation_results": simulation,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/analyze-deal", response_model=AnalyzeDealResponse)
async def analyze_deal(request: AnalyzeDealRequest, background_tasks: BackgroundTasks):
    try:
        result = await run_analysis(request)
        background_tasks.add_task(store_analysis_result, result)
        return result
    except Exception as e:
        logger.error(f"Deal analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/deal/{deal_id}")
async def get_deal(deal_id: str):
    try:
        from uuid import UUID
        uuid_id = UUID(deal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid deal_id format")

    try:
        engine = create_engine(f"postgresql+psycopg2://{user}:{pw}@{host}:5432/{db}")
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM mart.deal_analysis_results WHERE deal_id = :deal_id"),
                {"deal_id": str(uuid_id)}
            ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Deal not found")

        row = dict(result._mapping)
        return row
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch deal {deal_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")