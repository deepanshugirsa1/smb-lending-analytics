-- Merchant-by-loan grain with underwriting outcome
select
  o.loan_id,
  o.merchant_id,
  o.partner_id,
  o.channel,
  o.underwriting_tier,
  o.requested_amount,
  o.approved_amount,
  o.originated_at,
  o.status,
  case when o.approved_amount > 0 and o.status != 'declined' then 1 else 0 end as is_funding_eligible,
  case when o.status in ('funded', 'repaying', 'paid_off', 'defaulted') then 1 else 0 end as is_funded
from {{ ref('stg_loan_origination') }} o
