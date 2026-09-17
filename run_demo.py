"""End-to-end local demo: generate → load → marts → quality → Looker KPI export."""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from data.generate_lending_events import generate  # noqa: E402
from quality.run_checks import run as run_quality  # noqa: E402

OUT = ROOT / "output"
RAW = ROOT / "data" / "raw"


def build_marts(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        create or replace table stg_loan_origination as
        select * from read_csv_auto(?)
        """,
        [str(RAW / "loan_origination.csv")],
    )
    con.execute(
        """
        create or replace table stg_loan_servicing as
        select * from read_csv_auto(?)
        """,
        [str(RAW / "loan_servicing.csv")],
    )
    con.execute(
        """
        create or replace table int_loans as
        select
          loan_id, merchant_id, partner_id, channel, underwriting_tier,
          requested_amount, approved_amount, originated_at, status,
          case when approved_amount > 0 and status != 'declined' then 1 else 0 end as is_funding_eligible,
          case when status in ('funded','repaying','paid_off','defaulted') then 1 else 0 end as is_funded
        from stg_loan_origination
        """
    )
    con.execute(
        """
        create or replace table mart_funding_eligibility as
        select
          partner_id, channel, underwriting_tier,
          count(*) as loan_apps,
          sum(is_funding_eligible) as eligible_loans,
          sum(is_funded) as funded_loans,
          round(100.0 * sum(is_funding_eligible) / nullif(count(*), 0), 2) as funding_eligibility_rate_pct,
          round(100.0 * sum(is_funded) / nullif(sum(is_funding_eligible), 0), 2) as take_up_rate_pct
        from int_loans
        group by 1, 2, 3
        """
    )
    con.execute(
        """
        create or replace table mart_loss_adjusted_yield as
        with cashflows as (
          select
            l.partner_id, l.underwriting_tier, l.loan_id, l.approved_amount,
            coalesce(sum(s.principal_paid + s.interest_paid), 0) as total_collected,
            coalesce(sum(s.loss_amount), 0) as total_loss
          from int_loans l
          left join stg_loan_servicing s on l.loan_id = s.loan_id
          where l.is_funded = 1
          group by 1, 2, 3, 4
        )
        select
          partner_id, underwriting_tier,
          count(*) as funded_loans,
          sum(approved_amount) as total_principal,
          sum(total_collected) as total_collected,
          sum(total_loss) as total_loss,
          round(100.0 * (sum(total_collected) - sum(total_loss)) / nullif(sum(approved_amount), 0), 2)
            as loss_adjusted_yield_pct
        from cashflows
        group by 1, 2
        """
    )


def main() -> None:
    print("== SMB Lending Analytics Demo (~72% complete) ==")
    generate(n_loans=50_000, n_servicing=200_000)
    OUT.mkdir(parents=True, exist_ok=True)
    db_path = ROOT / "smb_lending.duckdb"
    con = duckdb.connect(str(db_path))
    build_marts(con)
    failures = run_quality(con)
    if failures:
        print("QUALITY FAIL:")
        for f in failures:
            print(" -", f)
        raise SystemExit(1)
    print("QUALITY PASS")
    for table in ("mart_funding_eligibility", "mart_loss_adjusted_yield"):
        df = con.execute(f"select * from {table}").df()
        path = OUT / f"{table}.csv"
        df.to_csv(path, index=False)
        print(f"Looker KPI export -> {path} ({len(df)} rows)")
    print("Done. See docs/ROADMAP.md for path to 100%.")


if __name__ == "__main__":
    main()
