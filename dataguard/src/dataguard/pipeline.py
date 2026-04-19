import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Any

from .config import config
from .database import setup_db, save_run_summary, save_quality_issues, save_anomaly_flags
from .quality_checks import run_all_checks
from .anomaly_detector import detect_all_anomalies

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def run_pipeline(input_file: str, run_name: str, schema: Dict=None, rules: Dict=None, refs: Dict=None) -> Dict[str, Any]:
    setup_db()
    path = Path(input_file)
    if not path.exists():
        logging.error(f"Input file {input_file} not found.")
        return {}

    logging.info(f"Starting DataGuard run '{run_name}' for file {input_file}")
    df = pd.read_csv(input_file)
    total_rows = len(df)

    logging.info("Running Data Quality Checks...")
    quality_report = run_all_checks(df, schema, rules, refs)
    issues_found = len(quality_report.issues)
    pass_rate = 100.0 if not quality_report.issues else (1 - (issues_found / total_rows)) * 100.0

    logging.info("Running Anomaly Detection...")
    anomaly_report = detect_all_anomalies(df)
    anomalies_found = len(anomaly_report.flags)

    logging.info("Saving results to database...")
    run_id = save_run_summary(run_name, input_file, total_rows, pass_rate, issues_found, anomalies_found)
    if quality_report.issues:
        save_quality_issues(run_id, quality_report.issues)
    if anomaly_report.flags:
        save_anomaly_flags(run_id, anomaly_report.flags)

    logging.info(f"Pipeline complete. Issues found: {issues_found}, Anomalies found: {anomalies_found}")
    return {
        "run_id": run_id,
        "total_rows": total_rows,
        "pass_rate": pass_rate,
        "issues": issues_found,
        "anomalies": anomalies_found
    }