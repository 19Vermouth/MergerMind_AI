# DealSense AI — Agent Instructions

> This file is the authoritative guide for any AI agent (human or autonomous) working on this project.

---

## Project Overview

**DealSense AI** is a production-grade, end-to-end M&A Intelligence Platform that automates due diligence through data engineering, ML, NLP, financial simulation, and LLM intelligence.

**Tech Stack:** Python 3.12, Docker, PostgreSQL, MinIO (S3), Apache Airflow, dbt Core, scikit-learn, XGBoost, FinBERT, NumPy, FastAPI, Streamlit, MLflow, Great Expectations.

**LLM Providers:** Groq (primary), OpenRouter (fallback), Gemini (fallback). Set `LLM_PRIMARY_PROVIDER` and the corresponding API key in `.env`.

---

## Repository Structure

```
dealsense-ai/
├── docker-compose.yml          # Full stack: Postgres, MinIO, Airflow, MLflow, FastAPI, Streamlit
├── Makefile                    # make up, down, test, lint, init-db, seed-db, dbt-run, etc.
├── .env.example                # All environment variables — copy to .env and fill in API keys
├── .gitignore
│
├── docker/                     # Dockerfiles and DB init scripts
│   ├── Dockerfile.api          # FastAPI container
│   ├── Dockerfile.dashboard     # Streamlit container
│   ├── Dockerfile.scraper      # Scrapy container
│   ├── Dockerfile.dbt          # dbt container
│   ├── Dockerfile.airflow       # Airflow container
│   └── init-scripts/
│       ├── init.sql            # Schema: raw, staging, mart, ml, metadata (15 tables)
│       └── seed.sql            # 50 sample deals + 30 news articles
│
├── src/                        # Python source code
│   ├── ingestion/               # MinIO bronze loader + Postgres silver loader
│   │   ├── loader.py            # MinIOClient (upload/download), PostgresLoader (load/fetch)
│   │   └── schemas.py          # Pydantic models: MADeal, NewsArticle, DealFeatures, MonteCarloResult
│   ├── features/               # Feature engineering for ML pipeline
│   │   └── feature_engineering.py  # compute_all_features(), industry similarity, premium score, etc.
│   ├── models/                 # ML training and prediction
│   │   ├── train.py            # MATrainingPipeline (sklearn + MLflow tracking)
│   │   └── predict.py          # DealPredictor (industry baseline + feature-based probability)
│   ├── simulation/             # Monte Carlo engine
│   │   └── monte_carlo.py      # MonteCarloEngine (50k sims), SimulationParams, run_monte_carlo()
│   ├── scoring/                # Deal scoring engine
│   │   └── deal_scorer.py      # DealScorer, ScoringWeights, combine ML + sentiment + simulation
│   ├── llm/                    # LLM integration
│   │   ├── providers.py        # GroqProvider, OpenRouterProvider, GeminiProvider, LLMManager
│   │   └── recommendation_engine.py  # RecommendationEngine, build_recommendation_prompt()
│   ├── api/                    # FastAPI application
│   │   ├── main.py             # App entry, CORS, router registration
│   │   ├── models.py           # Pydantic request/response schemas
│   │   └── routes/
│   │       ├── deals.py        # POST /api/v1/analyze-deal, GET /api/v1/deal/{id}
│   │       └── health.py       # GET /health
│   └── dashboard/              # Streamlit dashboard
│       └── app.py              # 6 pages: Overview, Explorer, Intelligence, Risk, AI Report, Performance
│
├── dags/                       # Airflow DAGs
│   └── ma_ingestion_dag.py     # scrape → bronze (MinIO) → silver (Postgres) → dbt → quality
│
├── dbt/                        # dbt Core project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── raw/sources.yml     # raw.ma_deals, raw.news_articles sources
│       ├── staging/            # stg_ma_deals.sql, stg_news_sentiment.sql (views)
│       ├── mart/               # fact_ma_deals.sql, fact_ma_deals_enriched.sql
│       └── ml/                 # feature_deal_model.sql (ML features table)
│
├── scraping/
│   └── spiders/
│       └── ma_deals_spider.py  # Scrapy spider for M&A deal scraping
│
├── tests/                      # pytest + coverage (target: 80%)
│   ├── conftest.py             # Shared fixtures: sample_monte_carlo_result, sample_simulation_params
│   ├── test_monte_carlo.py     # Monte Carlo engine tests (reproducibility, bounds, percentiles)
│   ├── test_scorer.py          # Deal scorer tests (recommendations, risk factors, metrics)
│   ├── test_features.py        # Feature engineering tests
│   └── test_api.py             # FastAPI endpoint tests
│
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions: lint, typecheck, pytest, dbt tests, docker build
│
├── requirements/
│   ├── base.txt                # All production dependencies
│   ├── dev.txt                 # Testing + linting (pytest, ruff, black, mypy)
│   └── prod.txt                # Production (gunicorn)
│
└── .pre-commit-config.yaml     # pre-commit hooks: ruff, black, isort, pytest
```

---

## How Everything Connects

```
Scrapy → MinIO (Bronze) → Airflow → PostgreSQL (Silver) → dbt (Gold) → Features → ML → Prediction
                                                                                    ↓
NewsAPI → FinBERT Sentiment ─────────────────────────────────────────────────→ Scorer → LLM
                                                                                    ↓
                                                                    Monte Carlo (50k) → Scorer → API Response
                                                                                    ↓
                                                                    FastAPI → Streamlit Dashboard
```

---

## Key Interfaces

### `POST /api/v1/analyze-deal`
```python
# Request
{
    "acquirer": "Microsoft",
    "target": "GitHub",
    "industry": "Software",
    "deal_value_usd": 7500000000,
    "premium_paid": 0.35,        # optional, default 0.35
    "cross_border": False         # optional, default False
}

# Response
{
    "deal_id": "uuid",
    "acquirer", "target", "deal_value_usd",
    "success_probability": 0.82,        # ML model output
    "sentiment_score": 0.64,             # FinBERT/news average
    "expected_npv": 2400000000,          # Monte Carlo mean
    "probability_positive_npv": 0.78,     # P(NPV > 0) from simulation
    "var_95": -850000000,
    "irr_median": 0.18,
    "recommendation": "PROCEED",          # PROCEED / NEGOTIATE / REJECT
    "confidence": "HIGH",
    "executive_summary": "...",
    "risk_factors": ["...", ...],
    "key_metrics": {...},
    "simulation_percentiles": {"p10": 800, "p25": 1.5B, "p50": 2.4B, "p75": 3.5B, "p90": 4.8B}
}
```

### `GET /health`
```python
{"status": "healthy|degraded", "version": "1.0.0", "services": {"postgres": "up|down", "minio": "up|down"}}
```

---

## Important Classes and Functions

| Module | Class/Function | Purpose |
|--------|---------------|---------|
| `src/simulation/monte_carlo.py` | `MonteCarloEngine` | Runs 50,000 simulations with vectorized NumPy. Takes `SimulationParams`, returns dict with expected_npv, irr_median, probability_positive_npv, var_95, percentiles |
| `src/simulation/monte_carlo.py` | `run_monte_carlo(deal_value_usd, industry, n_simulations)` | Convenience function wrapping `MonteCarloEngine` |
| `src/simulation/monte_carlo.py` | `SimulationParams` | Dataclass holding all distribution parameters for a deal simulation |
| `src/scoring/deal_scorer.py` | `DealScorer` | Combines ML probability, sentiment score, and simulation results using configurable weights. Returns `DealScore` with recommendation, confidence, risk factors, key metrics |
| `src/scoring/deal_scorer.py` | `ScoringWeights` | Dataclass: `ml=0.35, sentiment=0.25, simulation=0.40`. Override via env vars |
| `src/llm/providers.py` | `LLMManager` | Tries providers in order (Groq → OpenRouter → Gemini) until one succeeds |
| `src/llm/providers.py` | `GroqProvider`, `OpenRouterProvider`, `GeminiProvider` | Each wraps its respective API |
| `src/llm/recommendation_engine.py` | `RecommendationEngine.generate(...)` | Builds prompt from deal data, calls LLM, falls back to text summary if LLM fails |
| `src/llm/recommendation_engine.py` | `build_recommendation_prompt(...)` | Constructs the analyst prompt with deal parameters, risk factors, key metrics |
| `src/models/predict.py` | `DealPredictor` | Predicts deal success probability. Tries to load from `ml.feature_deal_model`, falls back to industry baseline + feature adjustments |
| `src/models/train.py` | `MATrainingPipeline` | Trains sklearn models (LogisticRegression, RandomForest) with MLflow tracking. Loads from `ml.feature_deal_model` |
| `src/ingestion/loader.py` | `MinIOClient` | Uploads raw deal JSON to MinIO bronze layer |
| `src/ingestion/loader.py` | `PostgresLoader` | Loads deals into `raw.ma_deals`, fetches deals for analysis |
| `src/features/feature_engineering.py` | `compute_all_features(...)` | Computes all 11 ML features from deal parameters and historical data |

---

## Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `POSTGRES_HOST` | Yes | `postgres` | PostgreSQL host |
| `POSTGRES_DB` | Yes | `dealsense` | Database name |
| `POSTGRES_USER` | Yes | `dealsense_user` | Database user |
| `POSTGRES_PASSWORD` | Yes | `changeme` | Database password |
| `MINIO_ENDPOINT` | Yes | `minio:9000` | MinIO S3 endpoint |
| `MINIO_BUCKET_RAW` | Yes | `dealsense-raw` | Bronze layer bucket |
| `NEWS_API_KEY` | Yes | — | NewsAPI key (newsapi.org) |
| `GROQ_API_KEY` | Yes* | — | Groq API key (console.groq.com) — primary LLM |
| `OPENROUTER_API_KEY` | No | — | OpenRouter fallback |
| `GEMINI_API_KEY` | No | — | Gemini fallback |
| `MODEL_WEIGHT_ML` | No | `0.35` | ML score weight in scoring |
| `MODEL_WEIGHT_SENTIMENT` | No | `0.25` | Sentiment weight in scoring |
| `MODEL_WEIGHT_SIMULATION` | No | `0.40` | Simulation weight in scoring |
| `LLM_PRIMARY_PROVIDER` | No | `groq` | Primary LLM provider |
| `LLM_TEMPERATURE` | No | `0.3` | LLM sampling temperature |
| `LLM_MAX_TOKENS` | No | `2000` | LLM max output tokens |
| `MONTE_CARLO_SIMULATIONS` | No | `50000` | Number of Monte Carlo iterations |

*At least one LLM API key is required for recommendation generation.

---

## Database Schema

| Schema | Tables | Purpose |
|--------|--------|---------|
| `raw` | `ma_deals`, `news_articles`, `sector_metrics`, `market_indicators` | Bronze layer — scraped/raw data |
| `staging` | `stg_ma_deals`, `stg_news_articles` | Silver layer — cleaned, validated views |
| `mart` | `dim_companies`, `dim_industries`, `dim_date`, `fact_ma_deals`, `fact_news_sentiment`, `deal_analysis_results` | Gold layer — business-ready star schema |
| `ml` | `feature_deal_model`, `model_predictions`, `model_metadata`, `training_runs` | ML features and model tracking |
| `metadata` | `run_logs`, `data_quality_checks`, `pipeline_config` | Operational metadata |

---

## Makefile Targets

```bash
make up              # Start all services
make down            # Stop all services
make build           # Build all Docker images
make init-db         # Run init.sql (schema)
make seed-db         # Run seed.sql (sample data)
make test            # Run pytest with coverage
make lint            # Run ruff linter
make format          # Run ruff + black formatter
make dbt-run         # Run dbt transformations
make dbt-test        # Run dbt tests
make logs            # Tail all logs
make clean           # Remove containers + volumes + __pycache__
make ci-setup        # Install pre-commit hooks
```

---

## Common Development Workflows

### Analyze a deal locally (outside Docker)
```python
from src.simulation.monte_carlo import run_monte_carlo
from src.scoring.deal_scorer import DealScorer
from src.models.predict import DealPredictor

predictor = DealPredictor()
result = predictor.predict("Microsoft", "GitHub", "Software", 7_500_000_000)

sim = run_monte_carlo(7_500_000_000)

scorer = DealScorer()
score = scorer.score(result["probability_success"], 0.64, sim, 7_500_000_000, "Software")
print(score.recommendation, score.confidence)
```

### Run Monte Carlo with custom parameters
```python
from src.simulation.monte_carlo import MonteCarloEngine, SimulationParams

params = SimulationParams(
    deal_value_usd=20_000_000_000,
    revenue_synergies_mean=0.15,
    cost_synergies_mean=0.08,
    integration_cost_mean=0.10,
    discount_rate_mean=0.12,
)
engine = MonteCarloEngine(n_simulations=50_000, seed=42)
result = engine.run(params)
```

### Change LLM provider
Set `LLM_PRIMARY_PROVIDER=gemini` in `.env` and ensure `GEMINI_API_KEY` is set.

---

## CI/CD Pipeline

GitHub Actions runs on every push and PR to `main`/`develop`:
1. **Lint** — ruff check + format + black + isort
2. **Type Check** — mypy
3. **Test** — pytest with 80% coverage threshold
4. **dbt Tests** — dbt debug + compile
5. **Docker Build** — Build FastAPI and Streamlit images

---

## Gotchas and Notes

- **Postgres init scripts run only on first startup** — if the volume already exists, `init.sql` won't re-run. Use `make clean && make up` to reset.
- **LLM providers are tried in order** — Groq first, then OpenRouter, then Gemini. If Groq fails, it falls through silently. Set `LLM_PRIMARY_PROVIDER` explicitly.
- **Monte Carlo is NumPy vectorized** — 50,000 simulations run in ~2 seconds. Do NOT use Python loops.
- **Airflow DAG** uses `PostgresOperator` which requires `apache-airflow-providers-postgres` — it's included in the Dockerfile but not in requirements/base.txt. If you pip install from base.txt into Airflow, install the provider separately.
- **dbt profiles.yml** uses Jinja templating for env vars — syntax is `{{ env_var('VAR_NAME', 'default') }}`. Profile is `dealsense_postgres` with targets `dev` and `prod`.
- **Feature table `ml.feature_deal_model`** requires `deal_success` to be non-null. Deals without outcomes (has_outcome=0) are excluded from training but included in feature store.
- **Seed data includes both completed and failed deals** — this is intentional for training the ML model (0.55 success rate overall).

---

## Testing Strategy

- Unit tests in `tests/` — run with `make test`
- Target: 80% coverage
- Key test coverage:
  - Monte Carlo: reproducibility, bounds, percentile ordering, distribution shapes
  - Scorer: recommendation thresholds, risk factor identification, key metrics completeness
  - API: happy path, validation errors, malformed UUID, health checks
  - Features: boundary conditions, empty inputs, all feature keys present

---

## Adding New Features

1. **Data** — Add to `raw.ma_deals` schema in `init.sql`, add staging view in `dbt/models/staging/`, add to `seed.sql`
2. **Transformation** — Add dbt model in `dbt/models/mart/` or `dbt/models/ml/`
3. **ML** — Add to `src/models/train.py` for training, `src/models/predict.py` for inference
4. **API** — Add route in `src/api/routes/deals.py`, add Pydantic model in `src/api/models.py`
5. **Dashboard** — Add page section to `src/dashboard/app.py`
6. **Tests** — Add to `tests/` following existing patterns
7. **CI** — Ensure new tests pass in GitHub Actions before merging