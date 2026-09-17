# Small-Business Lending Underwriting & Servicing Analytics Platform

Canonical analytics layer for **SMB lending**: loan origination → underwriting → servicing events into governed metrics for **loss-adjusted yield**, **funding-eligibility rate**, and portfolio risk — the decision metrics capital-markets and risk teams use to size offers.

> **Status: ~72% complete.** Local warehouse (DuckDB stand-in for Snowflake), dbt staging → marts, signature decision metrics, dbt-style tests, Looker-ready KPI export, and a runnable demo all work end-to-end. Live Snowflake + Airflow production wiring, Looker explores, and cohort offer-sizing dashboards are the remaining ~28%.

## Why this exists

Embedded lenders and capital partners need a single source of truth for underwriting outcomes and servicing performance. This project models merchant-by-loan events into **canonical datasets** and surfaces decision-grade metrics so risk and capital-markets teams can reshape offer sizing across cohorts — not just report defaults after the fact.

## Architecture (current)

```
raw CSV events  →  DuckDB load  →  dbt staging → intermediate → marts
                                         │
                                         ├─ fct_loan_origination / fct_servicing
                                         ├─ mart_funding_eligibility
                                         ├─ mart_loss_adjusted_yield
                                         └─ quality gates + Looker KPI export
```

## Quickstart

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python data/generate_lending_events.py
python run_demo.py
```

`run_demo.py` loads synthetic events into DuckDB, builds marts via SQL, runs quality checks, and writes Looker-ready KPI CSVs to `output/`.

## What's done (~72%)

| Component | Status |
|-----------|--------|
| Synthetic origination / underwriting / servicing event generator (~2M+ scale via config) | Done |
| DuckDB warehouse load (Snowflake stand-in) | Done |
| dbt-style staging → intermediate → marts SQL | Done |
| Signature metrics: loss-adjusted yield, funding-eligibility rate | Done |
| Data quality checks (nulls, uniqueness, freshness, range) | Done |
| Looker-ready KPI export | Done |
| Local demo + docs + roadmap | Done |

## Remaining ~28% → 100%

See [docs/ROADMAP.md](docs/ROADMAP.md) for the path to production Snowflake, Airflow DAGs, Looker explores, and cohort offer-sizing dashboards.

## Stack

Python, SQL, dbt (DuckDB adapter locally), DuckDB (Snowflake stand-in), Airflow DAG stubs, Looker-ready exports.
