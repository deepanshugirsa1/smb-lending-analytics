# Roadmap to 100%

Current status: **~72%**. Local end-to-end demo (generate → load → marts → quality → Looker KPIs) ships. Below is the path to production parity with the resume claims.

## Phase A — Warehouse & orchestration (→ ~85%)

- [ ] Swap DuckDB for a Snowflake trial / local Snowflake-compatible profile
- [ ] Wire `dbt build` against live Snowflake with `profiles.yml` secrets via env
- [ ] Implement Airflow DAG in `airflow/dags/lending_daily.py` (extract → dbt → quality → notify)
- [ ] Add freshness SLA sensors and failure Slack/email stubs

## Phase B — Decision metrics hardening (→ ~93%)

- [ ] Cohort-level **loss-adjusted yield** with recoverable vs charge-off splits
- [ ] **Funding-eligibility rate** by partner channel and underwriting tier
- [ ] Parallel-run validation: mart outputs vs hand-written SQL baseline (±0.5%)
- [ ] Expand dbt tests: accepted_values on status codes, custom row-count vs source

## Phase C — BI & self-serve (→ 100%)

- [ ] Looker explores + dashboards for capital-markets / risk (offer sizing by cohort)
- [ ] Document metric grain, aggregation, and edge cases in `docs/metrics.md`
- [ ] Sample Mode/Sigma alternate views for ops stakeholders
- [ ] CI: GitHub Actions running `dbt build` + quality checks on PR

## Non-goals (intentionally out of scope)

Revenue attribution, live partner API ingestion, and production PII — this repo stays synthetic and reproducible.
