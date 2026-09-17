-- Staging: servicing events
select
  event_id,
  loan_id,
  cast(event_at as timestamp) as event_at,
  principal_paid,
  interest_paid,
  charge_off,
  loss_amount
from {{ source('raw', 'loan_servicing') }}
