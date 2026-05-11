import pytest
from src.features.feature_engineering import (
    compute_industry_similarity,
    compute_premium_score,
    compute_regulatory_complexity,
    compute_market_volatility,
    compute_all_features,
)


class TestFeatureEngineering:
    def test_industry_similarity_match(self):
        result = compute_industry_similarity("Software", ["Software", "SaaS", "Enterprise"])
        assert result == 1.0

    def test_industry_similarity_partial(self):
        result = compute_industry_similarity("Design Software", ["Software", "SaaS"])
        assert 0.0 <= result <= 1.0

    def test_industry_similarity_empty_list(self):
        result = compute_industry_similarity("Software", [])
        assert result == 0.5

    def test_premium_score_fair(self):
        result = compute_premium_score(0.35, 0.32)
        assert 0.0 <= result <= 1.0

    def test_premium_score_overpriced(self):
        result = compute_premium_score(0.70, 0.32)
        assert result < 0.5

    def test_regulatory_complexity_scaled(self):
        result = compute_regulatory_complexity(10_000_000_000, "Biotech", True)
        assert 0.0 <= result <= 1.0

    def test_market_volatility_bounds(self):
        result = compute_market_volatility(vix=40.0)
        assert result == 1.0

        result = compute_market_volatility(vix=10.0)
        assert result == 0.25

    def test_compute_all_features_returns_all_keys(self):
        result = compute_all_features(
            deal_value_usd=7_500_000_000,
            industry="Software",
            premium_paid=0.35,
            sector_avg_premium=0.32,
            historical_success={"software": 0.72},
            articles=[{"sentiment_score": 0.65}],
        )
        expected_keys = [
            "log_deal_size", "industry_similarity", "premium_score",
            "regulatory_complexity", "market_volatility",
            "historical_success_rate", "news_sentiment_score",
            "synergy_ratio", "deal_size_percentile",
            "acquirer_track_record", "target_financial_health",
        ]
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], float)