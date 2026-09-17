"""Generate synthetic SMB lending origination / underwriting / servicing events."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parent / "raw"
RNG = np.random.default_rng(42)

STATUSES = ["approved", "declined", "funded", "repaying", "defaulted", "paid_off"]
TIERS = ["A", "B", "C", "D"]
CHANNELS = ["marketplace", "payments", "vertical_saas"]


def generate(n_loans: int = 50_000, n_servicing: int = 200_000) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    merchants = [f"M{i:05d}" for i in range(1, 5_001)]
    partners = [f"P{i:02d}" for i in range(1, 11)]

    loan_ids = [f"L{i:07d}" for i in range(1, n_loans + 1)]
    orig = pd.DataFrame(
        {
            "loan_id": loan_ids,
            "merchant_id": RNG.choice(merchants, n_loans),
            "partner_id": RNG.choice(partners, n_loans),
            "channel": RNG.choice(CHANNELS, n_loans),
            "underwriting_tier": RNG.choice(TIERS, n_loans, p=[0.25, 0.35, 0.25, 0.15]),
            "requested_amount": RNG.integers(5_000, 150_000, n_loans),
            "approved_amount": 0,
            "originated_at": pd.to_datetime("2024-01-01")
            + pd.to_timedelta(RNG.integers(0, 600, n_loans), unit="D"),
            "status": RNG.choice(STATUSES, n_loans, p=[0.1, 0.15, 0.2, 0.35, 0.1, 0.1]),
        }
    )
    # Eligibility: tiers A/B more often funded; approved_amount ~80-100% of requested when funded
    eligible = orig["underwriting_tier"].isin(["A", "B"]) & (orig["status"] != "declined")
    orig.loc[eligible, "approved_amount"] = (
        orig.loc[eligible, "requested_amount"] * RNG.uniform(0.8, 1.0, eligible.sum())
    ).astype(int)
    orig.loc[~eligible & (orig["status"] == "declined"), "approved_amount"] = 0
    orig.loc[~eligible & (orig["status"] != "declined"), "approved_amount"] = (
        orig.loc[~eligible & (orig["status"] != "declined"), "requested_amount"]
        * RNG.uniform(0.5, 0.85, (~eligible & (orig["status"] != "declined")).sum())
    ).astype(int)

    svc_loan = RNG.choice(loan_ids, n_servicing)
    servicing = pd.DataFrame(
        {
            "event_id": [f"S{i:08d}" for i in range(1, n_servicing + 1)],
            "loan_id": svc_loan,
            "event_at": pd.to_datetime("2024-01-01")
            + pd.to_timedelta(RNG.integers(0, 650, n_servicing), unit="D"),
            "principal_paid": RNG.integers(0, 5_000, n_servicing),
            "interest_paid": RNG.integers(0, 800, n_servicing),
            "charge_off": RNG.choice([0, 1], n_servicing, p=[0.97, 0.03]),
            "loss_amount": 0,
        }
    )
    servicing.loc[servicing["charge_off"] == 1, "loss_amount"] = RNG.integers(
        1_000, 40_000, (servicing["charge_off"] == 1).sum()
    )

    orig.to_csv(RAW / "loan_origination.csv", index=False)
    servicing.to_csv(RAW / "loan_servicing.csv", index=False)
    print(f"Wrote {len(orig):,} origination and {len(servicing):,} servicing rows -> {RAW}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--loans", type=int, default=50_000)
    p.add_argument("--servicing", type=int, default=200_000)
    args = p.parse_args()
    generate(args.loans, args.servicing)
