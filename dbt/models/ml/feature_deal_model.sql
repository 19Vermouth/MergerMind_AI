{{ config(schema='ml', materialized='table') }}

WITH deal_features AS (
    SELECT
        deal_id,
        deal_value_usd,
        industry,
        premium_paid,
        ev_revenue,
        ev_ebitda,
        deal_success,
        synergy_revenue_usd,
        synergy_cost_usd,
        integration_cost_usd,
        post_merger_performance
    FROM mart.fact_ma_deals
),
sector_stats AS (
    SELECT
        industry,
        AVG(deal_value_usd)         AS avg_deal_size,
        AVG(premium_paid)          AS avg_premium,
        AVG(CASE WHEN deal_success THEN 1.0 ELSE 0.0 END) AS success_rate,
        STDDEV(deal_value_usd)     AS stddev_deal_size
    FROM deal_features
    GROUP BY industry
)
SELECT
    df.deal_id,
    s.success_rate                                       AS historical_success_rate,
    LN(df.deal_value_usd)                               AS log_deal_size,
    df.premium_paid,
    df.ev_revenue,
    df.ev_ebitda,
    CASE
        WHEN df.premium_paid > s.avg_premium * 1.5 THEN 0.8
        WHEN df.premium_paid < s.avg_premium * 0.5 THEN 0.4
        ELSE 0.6
    END                                                  AS premium_score,
    df.deal_value_usd / NULLIF(s.avg_deal_size, 0)      AS relative_deal_size,
    PERCENT_RANK() OVER (PARTITION BY df.industry ORDER BY df.deal_value_usd) AS deal_size_percentile,
    CASE
        WHEN df.synergy_revenue_usd > 0 THEN df.synergy_revenue_usd::FLOAT / NULLIF(df.deal_value_usd, 0)
        ELSE 0
    END                                                  AS synergy_ratio,
    CASE
        WHEN df.synergy_cost_usd > 0 THEN df.synergy_cost_usd::FLOAT / NULLIF(df.deal_value_usd, 0)
        ELSE 0
    END                                                  AS cost_synergy_ratio,
    CASE
        WHEN df.integration_cost_usd > 0 THEN df.integration_cost_usd::FLOAT / NULLIF(df.deal_value_usd, 0)
        ELSE 0
    END                                                  AS integration_cost_ratio,
    COALESCE(df.post_merger_performance, 0)             AS post_merger_score,
    ROW_NUMBER() OVER (PARTITION BY df.industry ORDER BY df.announcement_date DESC) AS recency_within_sector,
    CASE WHEN df.deal_success IS NOT NULL THEN 1 ELSE 0 END AS has_outcome
FROM deal_features df
JOIN sector_stats s ON df.industry = s.industry