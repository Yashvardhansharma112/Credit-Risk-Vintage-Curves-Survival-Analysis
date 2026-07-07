-- =============================================================================
-- grade_risk_summary.sql
-- Default rate, loss rate, and interest rate adequacy by loan grade
-- =============================================================================
-- Use this query to assess whether interest rate pricing is sufficient
-- to cover expected losses for each grade bucket.
-- =============================================================================

SELECT
    grade,
    sub_grade,
    COUNT(*)                                            AS total_loans,
    SUM(funded_amnt)                                    AS total_funded,
    AVG(int_rate)                                       AS avg_interest_rate,
    AVG(fico_score)                                     AS avg_fico_score,
    AVG(dti)                                            AS avg_dti,
    AVG(annual_inc)                                     AS avg_annual_income,
    SUM(is_default)                                     AS total_defaults,
    ROUND(100.0 * AVG(is_default), 2)                   AS default_rate_pct,
    SUM(loss_amount)                                    AS total_loss,
    ROUND(100.0 * SUM(loss_amount) /
          NULLIF(SUM(funded_amnt), 0), 2)               AS loss_rate_pct,
    -- Interest rate adequacy: avg rate vs loss rate
    ROUND(AVG(int_rate) -
          100.0 * SUM(loss_amount) /
          NULLIF(SUM(funded_amnt), 0), 2)               AS rate_adequacy_bps
FROM clean_loans
WHERE grade IS NOT NULL
GROUP BY grade, sub_grade
ORDER BY grade, sub_grade;
