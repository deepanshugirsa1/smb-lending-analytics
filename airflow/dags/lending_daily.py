"""Airflow DAG stub — Phase A on the roadmap (not wired to a live scheduler yet)."""

# Remaining ~28%: implement extract → dbt → quality → notify on a real Airflow instance.
DAG_ID = "smb_lending_daily"
SCHEDULE = "@daily"
TASKS = ["extract_raw", "dbt_build", "run_quality", "export_looker_kpis", "notify_sla"]
