import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SimulationParams:
    deal_value_usd: int
    revenue_synergies_mean: float = 0.10
    revenue_synergies_std: float = 0.05
    cost_synergies_mean: float = 0.05
    cost_synergies_std: float = 0.03
    integration_cost_mean: float = 0.08
    integration_cost_std: float = 0.04
    discount_rate_mean: float = 0.10
    discount_rate_std: float = 0.02
    regulatory_delay_months_mean: float = 6.0
    regulatory_delay_months_std: float = 4.0
    market_volatility: float = 0.20
    projection_years: int = 5
    risk_free_rate: float = 0.04


class MonteCarloEngine:
    def __init__(
        self,
        n_simulations: int = 50_000,
        seed: int = 42,
    ) -> None:
        self.n_simulations = n_simulations
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def run(self, params: SimulationParams) -> dict:
        deal_value = params.deal_value_usd

        revenue_synergies = self.rng.lognormal(
            mean=np.log(1 + params.revenue_synergies_mean),
            sigma=params.revenue_synergies_std,
            size=self.n_simulations,
        ) * deal_value

        cost_synergies = self.rng.normal(
            loc=params.cost_synergies_mean,
            scale=params.cost_synergies_std,
            size=self.n_simulations,
        ) * deal_value
        cost_synergies = np.maximum(cost_synergies, 0)

        integration_costs = self.rng.gamma(
            shape=2.0,
            scale=params.integration_cost_mean / 2,
            size=self.n_simulations,
        ) * deal_value

        discount_rates = self.rng.normal(
            loc=params.discount_rate_mean,
            scale=params.discount_rate_std,
            size=self.n_simulations,
        )
        discount_rates = np.clip(discount_rates, 0.03, 0.20)

        regulatory_delays = self.rng.gamma(
            shape=2.0,
            scale=params.regulatory_delay_months_std,
            size=self.n_simulations,
        ) + params.regulatory_delay_months_mean
        regulatory_delays = np.clip(regulatory_delays, 0, 24)

        market_shocks = self.rng.normal(0, params.market_volatility, size=self.n_simulations)

        total_synergies = revenue_synergies + cost_synergies
        net_value = total_synergies - integration_costs - (market_shocks * deal_value * 0.1)

        npv_values = self._calculate_npv(net_value, discount_rates, params.projection_years)

        irr_values = self._calculate_irr(
            -deal_value,
            net_value * 0.2,
            net_value * 0.3,
            net_value * 0.3,
            net_value * 0.2,
        )

        var_95 = float(np.percentile(npv_values, 5))
        prob_positive = float(np.mean(npv_values > 0))

        percentile_labels = ["p10", "p25", "p50", "p75", "p90"]
        percentile_values = [10, 25, 50, 75, 90]
        percentiles = {label: int(np.percentile(npv_values, val)) for label, val in zip(percentile_labels, percentile_values)}

        logger.info(
            f"Monte Carlo complete: {self.n_simulations} sims, "
            f"NPV P50=${percentiles['p50']:,.0f}, P(NPV>0)={prob_positive:.1%}"
        )

        return {
            "expected_npv": int(np.mean(npv_values)),
            "irr_median": float(np.median(irr_values)),
            "irr_mean": float(np.mean(irr_values)),
            "irr_std": float(np.std(irr_values)),
            "probability_positive_npv": prob_positive,
            "var_95": var_95,
            "cvar_95": int(np.mean(npv_values[npv_values <= var_95])) if np.any(npv_values <= var_95) else var_95,
            "percentiles": percentiles,
            "npv_min": int(np.min(npv_values)),
            "npv_max": int(np.max(npv_values)),
            "npv_std": int(np.std(npv_values)),
            "simulation_count": self.n_simulations,
        }

    def _calculate_npv(
        self,
        net_value: NDArray[np.floating],
        discount_rate: NDArray[np.floating],
        years: int,
    ) -> NDArray[np.floating]:
        cash_flows = net_value * self.rng.uniform(0.15, 0.25, size=self.n_simulations)
        discount_factors = 1 / (1 + discount_rate) ** years
        return cash_flows * discount_factors

    def _calculate_irr(
        self,
        initial: float,
        cf1: NDArray[np.floating],
        cf2: NDArray[np.floating],
        cf3: NDArray[np.floating],
        cf4: NDArray[np.floating],
    ) -> NDArray[np.floating]:
        cash_flows = np.column_stack([initial * np.ones(self.n_simulations), cf1, cf2, cf3, cf4])
        rates = np.linspace(-0.5, 1.5, 200)
        npv_matrix = cash_flows[:, np.newaxis, :] * (1 + rates) ** np.arange(5)[:, np.newaxis]
        npv_sums = np.sum(npv_matrix, axis=0)
        closest_idx = np.abs(npv_sums).argmin(axis=1)
        return rates[closest_idx]


def run_monte_carlo(
    deal_value_usd: int,
    industry: str | None = None,
    n_simulations: int = 50_000,
) -> dict:
    params = SimulationParams(deal_value_usd=deal_value_usd)
    engine = MonteCarloEngine(n_simulations=n_simulations, seed=42)
    return engine.run(params)