"""Lightweight quality gates (dbt-test stand-ins for local demo)."""
from __future__ import annotations

import duckdb


def run(con: duckdb.DuckDBPyConnection) -> list[str]:
    failures: list[str] = []
    checks = [
        ("loan_id unique", "select count(*) - count(distinct loan_id) from stg_loan_origination"),
        ("loan_id not null", "select count(*) from stg_loan_origination where loan_id is null"),
        ("funding rate in range", "select count(*) from mart_funding_eligibility where funding_eligibility_rate_pct < 0 or funding_eligibility_rate_pct > 100"),
        ("yield present", "select count(*) from mart_loss_adjusted_yield where loss_adjusted_yield_pct is null"),
    ]
    for name, sql in checks:
        n = con.execute(sql).fetchone()[0]
        if n:
            failures.append(f"{name}: {n} bad rows")
    return failures
