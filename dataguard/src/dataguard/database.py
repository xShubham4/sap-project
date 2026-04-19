import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from .config import config

def get_connection():
    # Ensure parents exist
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(config.db_path)

def setup_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_name TEXT,
            input_file TEXT,
            total_rows INTEGER,
            pass_rate REAL,
            issues_found INTEGER,
            anomalies_found INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            check_name TEXT,
            column_name TEXT,
            issue_count INTEGER,
            severity TEXT,
            details TEXT,
            FOREIGN KEY(run_id) REFERENCES quality_runs(run_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anomaly_flags (
            flag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            row_index INTEGER,
            detection_method TEXT,
            column_name TEXT,
            anomaly_score REAL,
            severity TEXT,
            FOREIGN KEY(run_id) REFERENCES quality_runs(run_id)
        )
    ''')
    conn.commit()
    conn.close()

def save_run_summary(run_name: str, input_file: str, total_rows: int, pass_rate: float, 
                     issues_found: int, anomalies_found: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quality_runs (run_name, input_file, total_rows, pass_rate, issues_found, anomalies_found)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (run_name, input_file, total_rows, pass_rate, issues_found, anomalies_found))
    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id

def save_quality_issues(run_id: int, issues: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    records = [(run_id, issue['check_name'], issue.get('column_name'), issue['issue_count'], 
                issue['severity'], issue.get('details')) for issue in issues]
    cursor.executemany('''
        INSERT INTO quality_issues (run_id, check_name, column_name, issue_count, severity, details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records)
    conn.commit()
    conn.close()

def save_anomaly_flags(run_id: int, anomalies: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    records = [(run_id, anomaly['row_index'], anomaly['detection_method'], anomaly.get('column_name'),
                anomaly['anomaly_score'], anomaly['severity']) for anomaly in anomalies]
    cursor.executemany('''
        INSERT INTO anomaly_flags (run_id, row_index, detection_method, column_name, anomaly_score, severity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', records)
    conn.commit()
    conn.close()
