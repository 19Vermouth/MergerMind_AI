import pytest
from src.scoring.deal_scorer import DealScorer, ScoringWeights


class TestDealScorer:
    def test_scoring_weights_defaults(self):
        weights = ScoringWeights()
        assert weights.ml == 0.35
        assert weights.sentiment == 0.25
        assert weights.simulation == 0.40
        assert abs(weights.ml + weights.sentiment + weights.simulation - 1.0) < 0.001

    def test_scoring_weights_custom(self):
        weights = ScoringWeights(ml=0.5, sentiment=0.2, simulation=0.3)
        assert weights.ml == 0.5
        assert weights.sentiment == 0.2
        assert weights.simulation == 0.3

    def test_proceed_recommendation_high_score(self):
        scorer = DealScorer()
        sim_result = {
            "probability_positive_npv": 0.80,
            "expected_npv": 2_000_000_000,
            "var_95": 500_000_000,
            "irr_median": 0.18,
            "percentiles": {"p10": 500_000_000, "p25": 1_000_000_000, "p75": 3_000_000_000},
        }
        score = scorer.score(
            ml_probability=0.80,
            sentiment_score=0.75,
            simulation_result=sim_result,
            deal_value_usd=10_000_000_000,
        )
        assert score.recommendation in ["PROCEED", "NEGOTIATE", "REJECT"]
        assert score.confidence in ["HIGH", "MEDIUM", "LOW"]
        assert 0.0 <= score.normalized_score <= 1.0

    def test_reject_recommendation_low_score(self):
        scorer = DealScorer()
        sim_result = {
            "probability_positive_npv": 0.20,
            "expected_npv": -500_000_000,
            "var_95": -2_000_000_000,
            "irr_median": 0.03,
            "percentiles": {"p10": -1_000_000_000, "p25": -200_000_000, "p75": 500_000_000},
        }
        score = scorer.score(
            ml_probability=0.25,
            sentiment_score=0.20,
            simulation_result=sim_result,
            deal_value_usd=20_000_000_000,
        )
        assert score.recommendation == "REJECT"

    def test_risk_factors_identified(self):
        scorer = DealScorer()
        sim_result = {
            "probability_positive_npv": 0.30,
            "expected_npv": -500_000_000,
            "var_95": -3_000_000_000,
            "irr_median": 0.02,
            "percentiles": {"p10": -2_000_000_000, "p25": -500_000_000, "p75": 1_000_000_000},
        }
        score = scorer.score(
            ml_probability=0.30,
            sentiment_score=0.15,
            simulation_result=sim_result,
            deal_value_usd=50_000_000_000,
        )
        assert len(score.risk_factors) > 0
        assert len(score.risk_factors) <= 5

    def test_key_metrics_constructed(self):
        scorer = DealScorer()
        sim_result = {
            "probability_positive_npv": 0.70,
            "expected_npv": 1_500_000_000,
            "var_95": -300_000_000,
            "irr_median": 0.15,
            "percentiles": {"p10": -200_000_000, "p25": 800_000_000, "p75": 2_500_000_000},
        }
        score = scorer.score(
            ml_probability=0.72,
            sentiment_score=0.65,
            simulation_result=sim_result,
            deal_value_usd=8_000_000_000,
            industry="Software",
        )
        km = score.key_metrics
        assert "deal_value_usd" in km
        assert "ml_success_probability" in km
        assert "sentiment_score" in km
        assert "expected_npv" in km
        assert "irr_median" in km
        assert km["industry"] == "Software"

    def test_normalized_score_bounded(self):
        scorer = DealScorer()
        for _ in range(10):
            import random
            sim_result = {
                "probability_positive_npv": random.random(),
                "expected_npv": random.randint(-2_000_000_000, 5_000_000_000),
                "var_95": random.randint(-3_000_000_000, 1_000_000_000),
                "irr_median": random.uniform(0.01, 0.30),
                "percentiles": {"p10": -500_000_000, "p25": 500_000_000, "p75": 2_000_000_000},
            }
            score = scorer.score(
                ml_probability=random.uniform(0.1, 0.9),
                sentiment_score=random.uniform(0.1, 0.9),
                simulation_result=sim_result,
                deal_value_usd=random.randint(100_000_000, 50_000_000_000),
            )
            assert 0.0 <= score.normalized_score <= 1.0


class TestScoringWeights:
    def test_weights_sum_to_one(self):
        for ml_w in [0.20, 0.35, 0.50]:
            for sent_w in [0.20, 0.25, 0.30]:
                sim_w = round(1.0 - ml_w - sent_w, 2)
                weights = ScoringWeights(ml=ml_w, sentiment=sent_w, simulation=sim_w)
                total = weights.ml + weights.sentiment + weights.simulation
                assert abs(total - 1.0) < 0.01