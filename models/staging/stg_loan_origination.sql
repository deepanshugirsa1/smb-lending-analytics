-- Staging: loan origination (Snowflake/DuckDB)
select
  loan_id,
  merchant_id,
  partner_id,
  channel,
  underwriting_tier,
  requested_amount,
  approved_amount,
  cast(originated_at as timestamp) as originated_at,
  status
from {{ source('raw', 'loan_origination') }}
