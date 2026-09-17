-- Loss-adjusted yield by partner / tier (decision metric for offer sizing)
with cashflows as (
  select
    l.partner_id,
    l.underwriting_tier,
    l.loan_id,
    l.approved_amount,
    coalesce(sum(s.principal_paid + s.interest_paid), 0) as total_collected,
    coalesce(sum(s.loss_amount), 0) as total_loss
  from {{ ref('int_loans') }} l
  left join {{ ref('stg_loan_servicing') }} s on l.loan_id = s.loan_id
  where l.is_funded = 1
  group by 1, 2, 3, 4
)
select
  partner_id,
  underwriting_tier,
  count(*) as funded_loans,
  sum(approved_amount) as total_principal,
  sum(total_collected) as total_collected,
  sum(total_loss) as total_loss,
  round(
    100.0 * (sum(total_collected) - sum(total_loss)) / nullif(sum(approved_amount), 0),
    2
  ) as loss_adjusted_yield_pct
from cashflows
group by 1, 2
