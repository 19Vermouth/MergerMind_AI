{{ config(schema='mart', materialized='table') }}

SELECT
    d.deal_id,
    d.acquirer                                                 AS acquirer,
    d.target                                                   AS target,
    d.industry,
    d.deal_value_usd,
    d.announcement_date,
    d.closing_date,
    d.deal_status,
    d.ev_revenue,
    d.ev_ebitda,
    d.premium_paid,
    d.deal_success,
    d.post_merger_performance,
    COALESCE(avg_sector_premium, 0)                           AS sector_avg_premium,
    COALESCE(sector_success_rate, 0)                           AS sector_success_rate,
    COALESCE(industry_premium_vs_sector, 0)                   AS industry_premium_vs_sector,
    n.avg_sentiment                                            AS avg_news_sentiment,
    n.article_count,
    CASE
        WHEN d.deal_value_usd >= 10000000000 THEN 'large'
        WHEN d.deal_value_usd >= 1000000000 THEN 'medium'
        ELSE 'small'
    END                                                        AS deal_size_category,
    CASE
        WHEN d.ev_revenue IS NOT NULL THEN d.ev_revenue
        ELSE (SELECT AVG(ev_revenue) FROM staging.stg_ma_deals WHERE industry = d.industry AND ev_revenue IS NOT NULL)
    END                                                        AS industry_avg_ev_rev,
    CASE
        WHEN d.premium_paid > COALESCE(avg_sector_premium, 0) * 1.5 THEN 'high_premium'
        WHEN d.premium_paid < COALESCE(avg_sector_premium, 0) * 0.5 THEN 'low_premium'
        ELSE 'fair_premium'
    END                                                        AS premium_category
FROM staging.stg_ma_deals d
LEFT JOIN (
    SELECT industry, AVG(premium_paid) AS avg_sector_premium, AVG(CASE WHEN deal_success THEN 1.0 ELSE 0.0 END) AS sector_success_rate
    FROM staging.stg_ma_deals
    GROUP BY industry
) sector ON d.industry = sector.industry
LEFT JOIN (
    SELECT industry, premium_paid - AVG(premium_paid) OVER (PARTITION BY industry) AS industry_premium_vs_sector
    FROM staging.stg_ma_deals
) ip ON d.industry = ip.industry AND d.premium_paid = ip.premium_paid
LEFT JOIN (
    SELECT
        company_tag,
        AVG(sentiment_score) AS avg_sentiment,
        COUNT(*) AS article_count
    FROM staging.stg_news_sentiment
    WHERE company_tag IS NOT NULL
    GROUP BY company_tag
) n ON d.acquirer = n.company_tag OR d.target = n.company_tag