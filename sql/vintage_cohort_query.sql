-- =============================================================================
-- vintage_cohort_query.sql
-- Cumulative default rates by vintage quarter and Months on Book (MOB)
-- =============================================================================
-- This query powers the Vintage Curve Analysis in the Power BI dashboard.
-- It calculates running cumulative default rates at each monthly age
-- for each origination cohort (vintage).
-- =============================================================================

WITH loan_with_mob AS (
    SELECT
        id,
        DATE_TRUNC('quarter', issue_date)   AS vintage_quarter,
        EXTRACT(YEAR FROM issue_date)        AS issue_year,
        grade,
        is_default,
        EXTRACT(MONTH FROM AGE(last_pymnt_date, issue_date)) AS mob,
        funded_amnt,
        loss_amount
    FROM clean_loans
    WHERE issue_date IS NOT NULL
),

vintage_summary AS (
    SELECT
        vintage_quarter,
        COUNT(*)            AS total_loans,
        SUM(funded_amnt)    AS total_funded
    FROM clean_loans
    WHERE issue_date IS NOT NULL
    GROUP BY vintage_quarter
)

SELECT
    l.vintage_quarter,
    l.mob,
    v.total_loans,
    v.total_funded,
    SUM(l.is_default)                                                   AS cumulative_defaults,
    SUM(l.loss_amount)                                                  AS cumulative_loss,
    ROUND(100.0 * SUM(l.is_default) / v.total_loans, 4)                AS cumulative_default_rate_pct,
    ROUND(100.0 * SUM(l.loss_amount) / NULLIF(v.total_funded, 0), 4)   AS cumulative_loss_rate_pct
FROM loan_with_mob l
JOIN vintage_summary v ON l.vintage_quarter = v.vintage_quarter
WHERE l.mob BETWEEN 1 AND 36
GROUP BY l.vintage_quarter, l.mob, v.total_loans, v.total_funded
ORDER BY l.vintage_quarter, l.mob;
