{{ config(schema='mart', materialized='table') }}

SELECT
    d.deal_id,
    COALESCE(acq.company_key, -1)                              AS acquirer_key,
    COALESCE(tgt.company_key, -1)                              AS target_key,
    COALESCE(ind.industry_key, -1)                              AS industry_key,
    COALESCE(dd.date_key, -1)                                  AS date_key,
    d.deal_value_usd,
    d.announcement_date,
    d.closing_date,
    d.deal_status,
    d.ev_revenue,
    d.ev_ebitda,
    d.premium_paid,
    d.revenue_usd,
    d.ebitda_usd,
    d.synergy_revenue_usd,
    d.synergy_cost_usd,
    d.integration_cost_usd,
    d.deal_success,
    d.post_merger_performance,
    NOW()                                                      AS created_at
FROM staging.stg_ma_deals d
LEFT JOIN mart.dim_companies acq ON d.acquirer = acq.company_name
LEFT JOIN mart.dim_companies tgt ON d.target = tgt.company_name
LEFT JOIN mart.dim_industries ind ON d.industry = ind.industry_name
LEFT JOIN mart.dim_date dd ON d.announcement_date = dd.full_date