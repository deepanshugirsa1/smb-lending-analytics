-- Funding-eligibility rate by partner / tier / channel
select
  partner_id,
  channel,
  underwriting_tier,
  count(*) as loan_apps,
  sum(is_funding_eligible) as eligible_loans,
  sum(is_funded) as funded_loans,
  round(100.0 * sum(is_funding_eligible) / nullif(count(*), 0), 2) as funding_eligibility_rate_pct,
  round(100.0 * sum(is_funded) / nullif(sum(is_funding_eligible), 0), 2) as take_up_rate_pct
from {{ ref('int_loans') }}
group by 1, 2, 3
