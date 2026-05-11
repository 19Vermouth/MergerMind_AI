import pytest
import numpy as np


@pytest.fixture
def sample_monte_carlo_result():
    return {
        "expected_npv": 2400000000,
        "irr_median": 0.18,
        "probability_positive_npv": 0.78,
        "var_95": -850000000,
        "percentiles": {
            "p10": 800000000,
            "p25": 1500000000,
            "p50": 2400000000,
            "p75": 3500000000,
            "p90": 4800000000,
        },
        "simulation_count": 50000,
    }


@pytest.fixture
def sample_simulation_params():
    from src.simulation.monte_carlo import SimulationParams
    return SimulationParams(deal_value_usd=7_500_000_000)


@pytest.fixture
def sample_deal_data():
    return {
        "acquirer": "Microsoft",
        "target": "GitHub",
        "industry": "Software",
        "deal_value_usd": 7_500_000_000,
        "premium_paid": 0.35,
    }