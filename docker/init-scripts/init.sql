-- =============================================================================
-- DealSense AI — PostgreSQL Schema Initialization
-- Creates: raw, staging, mart, ml, metadata schemas and all core tables
-- =============================================================================

-- Create schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF EXISTS mart;
CREATE SCHEMA IF NOT EXISTS ml;
CREATE SCHEMA IF NOT EXISTS metadata;

-- =============================================================================
-- RAW SCHEMA — Bronze layer (ingested from scrapers / APIs)
-- =============================================================================

CREATE TABLE IF NOT EXISTS raw.ma_deals (
    id              SERIAL PRIMARY KEY,
    deal_id         UUID DEFAULT gen_random_uuid(),
    acquirer        VARCHAR(255) NOT NULL,
    target          VARCHAR(255) NOT NULL,
    industry        VARCHAR(100),
    deal_value_usd  BIGINT,
    announcement_date DATE,
    closing_date    DATE,
    deal_status     VARCHAR(50),
    ev_revenue      DECIMAL(8,2),
    ev_ebitda       DECIMAL(8,2),
    premium_paid    DECIMAL(6,2),
    revenue_usd     BIGINT,
    ebitda_usd      BIGINT,
    synergy_revenue_usd BIGINT,
    synergy_cost_usd    BIGINT,
    integration_cost_usd BIGINT,
    regulatory_approval VARCHAR(50),
    deal_success    BOOLEAN,
    post_merger_performance DECIMAL(5,2),
    source_url      TEXT,
    scraped_at      TIMESTAMP DEFAULT NOW(),
    raw_json        JSONB
);

CREATE TABLE IF NOT EXISTS raw.news_articles (
    id              SERIAL PRIMARY KEY,
    article_id      UUID DEFAULT gen_random_uuid(),
    title           VARCHAR(500),
    content         TEXT,
    source          VARCHAR(100),
    author          VARCHAR(200),
    published_at    TIMESTAMP,
    url             TEXT UNIQUE,
    sentiment_score DECIMAL(4,3),
    sentiment_label VARCHAR(20),
    company_tag     VARCHAR(255),
    industry_tag    VARCHAR(100),
    scraped_at      TIMESTAMP DEFAULT NOW(),
    raw_json        JSONB
);

CREATE TABLE IF NOT EXISTS raw.sector_metrics (
    id              SERIAL PRIMARY KEY,
    sector          VARCHAR(100),
    date            DATE,
    avg_deal_size   BIGINT,
    deal_count      INTEGER,
    avg_premium     DECIMAL(5,2),
    success_rate   DECIMAL(4,3),
    avg_ev_revenue  DECIMAL(6,2),
    avg_ev_ebitda   DECIMAL(6,2),
    scraped_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.market_indicators (
    id              SERIAL PRIMARY KEY,
    date            DATE,
    index_name      VARCHAR(50),
    volatility_vix  DECIMAL(6,3),
    risk_free_rate  DECIMAL(5,3),
    credit_spread   DECIMAL(6,3),
    m&a_volume_b    BIGINT,
    scraped_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for raw tables
CREATE INDEX IF NOT EXISTS idx_raw_deals_acquirer ON raw.ma_deals(acquirer);
CREATE INDEX IF NOT EXISTS idx_raw_deals_target ON raw.ma_deals(target);
CREATE INDEX IF NOT EXISTS idx_raw_deals_industry ON raw.ma_deals(industry);
CREATE INDEX IF NOT EXISTS idx_raw_deals_announcement ON raw.ma_deals(announcement_date);
CREATE INDEX IF NOT EXISTS idx_raw_deals_status ON raw.ma_deals(deal_status);
CREATE INDEX IF NOT EXISTS idx_raw_news_company ON raw.news_articles(company_tag);
CREATE INDEX IF NOT EXISTS idx_raw_news_published ON raw.news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_news_sentiment ON raw.news_articles(sentiment_label);

-- =============================================================================
-- STAGING SCHEMA — Silver layer (cleaned, typed, validated)
-- =============================================================================

CREATE TABLE IF NOT EXISTS staging.stg_ma_deals (
    stg_deal_id     VARCHAR(50) PRIMARY KEY,
    acquirer        VARCHAR(255) NOT NULL,
    target          VARCHAR(255) NOT NULL,
    industry        VARCHAR(100),
    deal_value_usd  BIGINT CHECK (deal_value_usd > 0),
    announcement_date DATE NOT NULL,
    closing_date    DATE,
    deal_status     VARCHAR(50) CHECK (deal_status IN ('completed', 'failed', 'pending', 'withdrawn')),
    ev_revenue      DECIMAL(8,2) CHECK (ev_revenue > 0),
    ev_ebitda       DECIMAL(8,2) CHECK (ev_ebitda > 0),
    premium_paid    DECIMAL(6,2) CHECK (premium_paid BETWEEN 0 AND 5),
    revenue_usd     BIGINT,
    ebitda_usd      BIGINT,
    synergy_revenue_usd BIGINT,
    synergy_cost_usd BIGINT,
    integration_cost_usd BIGINT,
    deal_success    BOOLEAN,
    post_merger_performance DECIMAL(5,2),
    source_url      TEXT,
    ingested_at     TIMESTAMP DEFAULT NOW(),
    raw_id          INTEGER REFERENCES raw.ma_deals(id)
);

CREATE TABLE IF NOT EXISTS staging.stg_news_articles (
    stg_article_id  VARCHAR(50) PRIMARY KEY,
    title           VARCHAR(500) NOT NULL,
    content         TEXT,
    source          VARCHAR(100),
    author          VARCHAR(200),
    published_at    TIMESTAMP NOT NULL,
    url             TEXT UNIQUE NOT NULL,
    company_tag     VARCHAR(255),
    industry_tag    VARCHAR(100),
    sentiment_score DECIMAL(4,3) CHECK (sentiment_score BETWEEN -1 AND 1),
    sentiment_label  VARCHAR(20) CHECK (sentiment_label IN ('positive', 'negative', 'neutral')),
    ingested_at      TIMESTAMP DEFAULT NOW(),
    raw_id          INTEGER REFERENCES raw.news_articles(id)
);

CREATE INDEX IF NOT EXISTS idx_stg_deals_announcement ON staging.stg_ma_deals(announcement_date);
CREATE INDEX IF NOT EXISTS idx_stg_deals_industry ON staging.stg_ma_deals(industry);
CREATE INDEX IF NOT EXISTS idx_stg_deals_success ON staging.stg_ma_deals(deal_success);
CREATE INDEX IF NOT EXISTS idx_stg_news_published ON staging.stg_news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_stg_news_company ON staging.stg_news_articles(company_tag);

-- =============================================================================
-- MART SCHEMA — Gold layer (business-ready, star-schema)
-- =============================================================================

-- Dimension: Companies
CREATE TABLE IF NOT EXISTS mart.dim_companies (
    company_key     SERIAL PRIMARY KEY,
    company_name    VARCHAR(255) NOT NULL,
    ticker          VARCHAR(10),
    sector          VARCHAR(100),
    industry        VARCHAR(100),
    country         VARCHAR(100),
    founded_year    INTEGER,
    is_acquirer     BOOLEAN DEFAULT FALSE,
    is_target       BOOLEAN DEFAULT FALSE,
    total_deals     INTEGER DEFAULT 0,
    total_deal_value BIGINT DEFAULT 0,
    success_rate    DECIMAL(4,3),
    updated_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_name, ticker)
);

-- Dimension: Industries
CREATE TABLE IF NOT EXISTS mart.dim_industries (
    industry_key    SERIAL PRIMARY KEY,
    industry_name    VARCHAR(100) NOT NULL UNIQUE,
    sector          VARCHAR(100),
    avg_deal_size   BIGINT,
    avg_premium     DECIMAL(5,2),
    historical_count INTEGER,
    success_rate    DECIMAL(4,3),
    avg_ev_revenue  DECIMAL(6,2),
    avg_ev_ebitda   DECIMAL(6,2),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Dimension: Time
CREATE TABLE IF NOT EXISTS mart.dim_date (
    date_key        INTEGER PRIMARY KEY,
    full_date       DATE NOT NULL UNIQUE,
    year            INTEGER,
    quarter         INTEGER,
    month           INTEGER,
    month_name      VARCHAR(20),
    day_of_week     INTEGER,
    day_name        VARCHAR(20),
    is_weekend      BOOLEAN,
    fiscal_year     INTEGER,
    fiscal_quarter  INTEGER
);

-- Fact: M&A Deals
CREATE TABLE IF NOT EXISTS mart.fact_ma_deals (
    fact_deal_key   BIGINT IDENTITY(1,1) PRIMARY KEY,
    deal_id         UUID NOT NULL,
    acquirer_key    INTEGER REFERENCES mart.dim_companies(company_key),
    target_key      INTEGER REFERENCES mart.dim_companies(company_key),
    industry_key    INTEGER REFERENCES mart.dim_industries(industry_key),
    date_key        INTEGER REFERENCES mart.dim_date(date_key),
    deal_value_usd  BIGINT NOT NULL,
    announcement_date DATE NOT NULL,
    closing_date    DATE,
    deal_status     VARCHAR(50),
    ev_revenue      DECIMAL(8,2),
    ev_ebitda       DECIMAL(8,2),
    premium_paid    DECIMAL(6,2),
    revenue_usd     BIGINT,
    ebitda_usd      BIGINT,
    synergy_revenue_usd BIGINT,
    synergy_cost_usd BIGINT,
    integration_cost_usd BIGINT,
    deal_success    BOOLEAN,
    post_merger_performance DECIMAL(5,2),
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(deal_id)
);

-- Fact: News Sentiment
CREATE TABLE IF NOT EXISTS mart.fact_news_sentiment (
    fact_sentiment_key BIGINT IDENTITY(1,1) PRIMARY KEY,
    article_id      UUID NOT NULL,
    company_key      INTEGER REFERENCES mart.dim_companies(company_key),
    industry_key     INTEGER REFERENCES mart.dim_industries(industry_key),
    date_key         INTEGER REFERENCES mart.dim_date(date_key),
    title            VARCHAR(500),
    content_preview  TEXT,
    source           VARCHAR(100),
    published_at     TIMESTAMP,
    sentiment_score  DECIMAL(4,3),
    sentiment_label  VARCHAR(20),
    created_at       TIMESTAMP DEFAULT NOW(),
    UNIQUE(article_id)
);

-- Fact: Deal Analysis Results
CREATE TABLE IF NOT EXISTS mart.deal_analysis_results (
    analysis_id     UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id         UUID,
    acquirer        VARCHAR(255) NOT NULL,
    target          VARCHAR(255) NOT NULL,
    industry        VARCHAR(100),
    deal_value_usd  BIGINT,
    success_probability DECIMAL(4,3),
    sentiment_score DECIMAL(4,3),
    expected_npv    BIGINT,
    probability_positive_npv DECIMAL(4,3),
    var_95          BIGINT,
    irr_median      DECIMAL(5,3),
    recommendation  VARCHAR(20) CHECK (recommendation IN ('PROCEED', 'NEGOTIATE', 'REJECT')),
    confidence      VARCHAR(20),
    executive_summary TEXT,
    risk_factors    TEXT[],
    key_metrics     JSONB,
    simulation_results JSONB,
    analyzed_at     TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- ML SCHEMA — Machine Learning features and predictions
-- =============================================================================

CREATE TABLE IF NOT EXISTS ml.feature_deal_model (
    feature_id      BIGINT IDENTITY(1,1) PRIMARY KEY,
    deal_id         UUID NOT NULL,
    industry_similarity DECIMAL(5,3),
    log_deal_size   DECIMAL(8,3),
    premium_paid    DECIMAL(6,2),
    ev_revenue      DECIMAL(8,2),
    ev_ebitda       DECIMAL(8,2),
    regulatory_complexity DECIMAL(3,2),
    market_volatility DECIMAL(5,3),
    historical_success_rate DECIMAL(4,3),
    news_sentiment_score DECIMAL(4,3),
    synergy_ratio   DECIMAL(5,3),
    deal_size_percentile DECIMAL(5,3),
    acquirer_track_record DECIMAL(4,3),
    target_financial_health DECIMAL(4,3),
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(deal_id)
);

CREATE TABLE IF NOT EXISTS ml.model_predictions (
    prediction_id   BIGINT IDENTITY(1,1) PRIMARY KEY,
    deal_id         UUID NOT NULL,
    model_name      VARCHAR(100) NOT NULL,
    probability_success DECIMAL(4,3),
    confidence_lower DECIMAL(4,3),
    confidence_upper DECIMAL(4,3),
    feature_importance JSONB,
    prediction_date TIMESTAMP DEFAULT NOW(),
    UNIQUE(deal_id, model_name)
);

CREATE TABLE IF NOT EXISTS ml.model_metadata (
    model_id        BIGINT IDENTITY(1,1) PRIMARY KEY,
    model_name      VARCHAR(100) NOT NULL,
    model_type      VARCHAR(50),
    version         VARCHAR(20),
    trained_at      TIMESTAMP DEFAULT NOW(),
    metrics         JSONB,
    hyperparameters JSONB,
    feature_names   TEXT[],
    is_active       BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS ml.training_runs (
    run_id          BIGINT IDENTITY(1,1) PRIMARY KEY,
    model_name      VARCHAR(100) NOT NULL,
    experiment_name VARCHAR(200),
    run_timestamp   TIMESTAMP DEFAULT NOW(),
    training_rows   INTEGER,
    test_rows       INTEGER,
    roc_auc         DECIMAL(5,4),
    precision       DECIMAL(5,4),
    recall          DECIMAL(5,4),
    f1_score        DECIMAL(5,4),
    logloss         DECIMAL(6,4),
    mlflow_run_id   VARCHAR(100),
    status          VARCHAR(20) DEFAULT 'pending'
);

-- =============================================================================
-- METADATA SCHEMA — Data quality, run logs, operational metadata
-- =============================================================================

CREATE TABLE IF NOT EXISTS metadata.run_logs (
    run_id          SERIAL PRIMARY KEY,
    dag_name        VARCHAR(200),
    task_name       VARCHAR(200),
    run_timestamp   TIMESTAMP DEFAULT NOW(),
    status          VARCHAR(20),
    rows_processed  INTEGER,
    error_message   TEXT,
    duration_seconds INTEGER
);

CREATE TABLE IF NOT EXISTS metadata.data_quality_checks (
    check_id        SERIAL PRIMARY KEY,
    check_name      VARCHAR(200),
    table_name      VARCHAR(100),
    schema_name     VARCHAR(50),
    check_type      VARCHAR(50),
    expected_value  TEXT,
    actual_value    TEXT,
    passed          BOOLEAN,
    checked_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metadata.pipeline_config (
    config_id       SERIAL PRIMARY KEY,
    pipeline_name   VARCHAR(200),
    config_key      VARCHAR(100),
    config_value    TEXT,
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- Seed date dimension for recent years
-- =============================================================================

INSERT INTO mart.dim_date (date_key, full_date, year, quarter, month, month_name, day_of_week, day_name, is_weekend, fiscal_year, fiscal_quarter)
SELECT
    CAST(TO_CHAR(d, 'YYYYMMDD') AS INTEGER) AS date_key,
    d::DATE AS full_date,
    EXTRACT(YEAR FROM d)::INTEGER AS year,
    EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
    EXTRACT(MONTH FROM d)::INTEGER AS month,
    TO_CHAR(d, 'Month') AS month_name,
    EXTRACT(DOW FROM d)::INTEGER AS day_of_week,
    TO_CHAR(d, 'Day') AS day_name,
    EXTRACT(DOW FROM d) IN (0, 6) AS is_weekend,
    CASE WHEN EXTRACT(MONTH FROM d) >= 7 THEN EXTRACT(YEAR FROM d)::INTEGER + 1 ELSE EXTRACT(YEAR FROM d)::INTEGER END AS fiscal_year,
    CASE
        WHEN EXTRACT(MONTH FROM d) BETWEEN 7 AND 9 THEN 1
        WHEN EXTRACT(MONTH FROM d) BETWEEN 10 AND 12 THEN 2
        WHEN EXTRACT(MONTH FROM d) BETWEEN 1 AND 3 THEN 3
        ELSE 4
    END AS fiscal_quarter
FROM generate_series('2018-01-01', '2027-12-31', INTERVAL '1 day') AS t(d)
ON CONFLICT (full_date) DO NOTHING;

COMMENT ON TABLE raw.ma_deals IS 'Bronze layer: raw scraped M&A deal data';
COMMENT ON TABLE staging.stg_ma_deals IS 'Silver layer: cleaned and validated deal data';
COMMENT ON TABLE mart.fact_ma_deals IS 'Gold layer: business-ready deal facts';
COMMENT ON TABLE ml.feature_deal_model IS 'ML features for deal success prediction';
COMMENT ON TABLE mart.deal_analysis_results IS 'AI-generated deal analysis and recommendations';