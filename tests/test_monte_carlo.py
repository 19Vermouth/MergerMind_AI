import pytest
import numpy as np
from src.simulation.monte_carlo import MonteCarloEngine, SimulationParams, run_monte_carlo


class TestMonteCarloEngine:
    def test_engine_initialization(self):
        engine = MonteCarloEngine(n_simulations=10_000, seed=42)
        assert engine.n_simulations == 10_000
        assert engine.seed == 42
        assert engine.rng is not None

    def test_run_returns_all_required_fields(self, sample_simulation_params):
        engine = MonteCarloEngine(n_simulations=1_000, seed=42)
        result = engine.run(sample_simulation_params)

        assert "expected_npv" in result
        assert "irr_median" in result
        assert "probability_positive_npv" in result
        assert "var_95" in result
        assert "percentiles" in result
        assert "simulation_count" in result
        assert result["simulation_count"] == 1_000

    def test_run_produces_finite_values(self, sample_simulation_params):
        engine = MonteCarloEngine(n_simulations=1_000, seed=42)
        result = engine.run(sample_simulation_params)

        assert np.isfinite(result["expected_npv"])
        assert np.isfinite(result["irr_median"])
        assert np.isfinite(result["probability_positive_npv"])
        assert np.isfinite(result["var_95"])
        assert -1 <= result["probability_positive_npv"] <= 1

    def test_percentiles_contain_all_keys(self, sample_simulation_params):
        engine = MonteCarloEngine(n_simulations=1_000, seed=42)
        result = engine.run(sample_simulation_params)

        assert set(result["percentiles"].keys()) == {"p10", "p25", "p50", "p75", "p90"}
        assert result["percentiles"]["p10"] <= result["percentiles"]["p25"]
        assert result["percentiles"]["p25"] <= result["percentiles"]["p50"]
        assert result["percentiles"]["p50"] <= result["percentiles"]["p75"]
        assert result["percentiles"]["p75"] <= result["percentiles"]["p90"]

    def test_run_monte_carlo_function(self):
        result = run_monte_carlo(deal_value_usd=5_000_000_000, n_simulations=1_000)
        assert result["simulation_count"] == 1_000
        assert "expected_npv" in result
        assert "irr_median" in result

    def test_reproducibility_with_same_seed(self):
        params = SimulationParams(deal_value_usd=10_000_000_000)
        engine1 = MonteCarloEngine(n_simulations=100, seed=42)
        engine2 = MonteCarloEngine(n_simulations=100, seed=42)

        result1 = engine1.run(params)
        result2 = engine2.run(params)

        assert result1["expected_npv"] == result2["expected_npv"]

    def test_larger_deal_value_increases_npv(self):
        params_small = SimulationParams(deal_value_usd=1_000_000_000)
        params_large = SimulationParams(deal_value_usd=10_000_000_000)

        engine = MonteCarloEngine(n_simulations=500, seed=42)
        result_small = engine.run(params_small)
        result_large = engine.run(params_large)

        assert result_large["expected_npv"] > result_small["expected_npv"]

    def test_probability_bounds(self, sample_simulation_params):
        engine = MonteCarloEngine(n_simulations=500, seed=42)
        result = engine.run(sample_simulation_params)
        assert 0.0 <= result["probability_positive_npv"] <= 1.0

    def test_var_95_less_than_mean(self, sample_simulation_params):
        engine = MonteCarloEngine(n_simulations=500, seed=42)
        result = engine.run(sample_simulation_params)
        assert result["var_95"] <= result["expected_npv"]


class TestSimulationParams:
    def test_default_values(self):
        params = SimulationParams(deal_value_usd=5_000_000_000)
        assert params.deal_value_usd == 5_000_000_000
        assert params.revenue_synergies_mean == 0.10
        assert params.projection_years == 5
        assert params.risk_free_rate == 0.04

    def test_custom_params(self):
        params = SimulationParams(
            deal_value_usd=1_000_000_000,
            revenue_synergies_mean=0.15,
            discount_rate_mean=0.12,
        )
        assert params.revenue_synergies_mean == 0.15
        assert params.discount_rate_mean == 0.12