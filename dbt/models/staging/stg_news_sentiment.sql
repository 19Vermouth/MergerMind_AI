{{ config(schema='staging', materialized='view') }}

SELECT
    'ART_' || CAST(id AS VARCHAR)                              AS stg_article_id,
    TRIM(title)                                               AS title,
    TRIM(content)                                             AS content,
    TRIM(source)                                              AS source,
    TRIM(author)                                              AS author,
    published_at,
    url,
    company_tag,
    industry_tag,
    COALESCE(sentiment_score, 0)                              AS sentiment_score,
    CASE
        WHEN sentiment_score > 0.1 THEN 'positive'
        WHEN sentiment_score < -0.1 THEN 'negative'
        ELSE 'neutral'
    END                                                        AS sentiment_label,
    NOW()                                                      AS ingested_at,
    id                                                         AS raw_id
FROM {{ source('dealsense', 'news_articles') }}
WHERE title IS NOT NULL
  AND url IS NOT NULL
  AND published_at IS NOT NULL