{{ config(schema='staging', materialized='view') }}

SELECT
    'DEAL_' || CAST(id AS VARCHAR) AS stg_deal_id,
    TRIM(acquirer)                                             AS acquirer,
    TRIM(target)                                               AS target,
    TRIM(industry)                                             AS industry,
    deal_value_usd,
    announcement_date,
    closing_date,
    LOWER(deal_status)                                        AS deal_status,
    ev_revenue,
    ev_ebitda,
    COALESCE(premium_paid, 0)                                 AS premium_paid,
    revenue_usd,
    ebitda_usd,
    COALESCE(synergy_revenue_usd, 0)                          AS synergy_revenue_usd,
    COALESCE(synergy_cost_usd, 0)                             AS synergy_cost_usd,
    COALESCE(integration_cost_usd, 0)                         AS integration_cost_usd,
    deal_success,
    post_merger_performance,
    source_url,
    NOW()                                                      AS ingested_at,
    id                                                         AS raw_id
FROM {{ source('dealsense', 'ma_deals') }}
WHERE acquirer IS NOT NULL
  AND target IS NOT NULL
  AND deal_value_usd > 0