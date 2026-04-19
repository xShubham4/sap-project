import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple

@dataclass
class QualityReport:
    total_rows: int
    issues: List[Dict[str, Any]] = field(default_factory=list)

def check_missing_values(df: pd.DataFrame) -> List[Dict[str, Any]]:
    missing_counts = df.isnull().sum()
    issues = []
    for col, count in missing_counts.items():
        if count > 0:
            pct = (count / len(df)) * 100
            severity = "HIGH" if pct > 10 else ("MEDIUM" if pct > 2 else "LOW")
            issues.append({
                "check_name": "Missing Values",
                "column_name": col,
                "issue_count": int(count),
                "severity": severity,
                "details": f"{pct:.2f}% missing"
            })
    return issues

def check_duplicates(df: pd.DataFrame) -> List[Dict[str, Any]]:
    dupes = df.duplicated().sum()
    if dupes > 0:
        pct = (dupes / len(df)) * 100
        severity = "HIGH" if pct > 5 else "MEDIUM"
        return [{
            "check_name": "Duplicate Rows",
            "column_name": "ALL",
            "issue_count": int(dupes),
            "severity": severity,
            "details": f"{pct:.2f}% duplicate rows"
        }]
    return []

def check_data_types(df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
    issues = []
    for col, expected_type in schema.items():
        if col in df.columns:
            actual_type = str(df[col].dtype)
            # basic check, assumes schema maps to pandas dtypes loosely
            if expected_type not in actual_type:
                issues.append({
                    "check_name": "Data Type Mismatch",
                    "column_name": col,
                    "issue_count": len(df),
                    "severity": "HIGH",
                    "details": f"Expected {expected_type}, got {actual_type}"
                })
    return issues

def check_value_ranges(df: pd.DataFrame, rules: Dict[str, Tuple[float, float]]) -> List[Dict[str, Any]]:
    issues = []
    for col, (min_val, max_val) in rules.items():
        if col in df.columns:
            out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]
            if not out_of_range.empty:
                count = len(out_of_range)
                pct = (count / len(df)) * 100
                severity = "HIGH" if pct > 5 else "MEDIUM"
                issues.append({
                    "check_name": "Value Range Check",
                    "column_name": col,
                    "issue_count": int(count),
                    "severity": severity,
                    "details": f"{count} values outside [{min_val}, {max_val}]"
                })
    return issues

def check_referential_integrity(df: pd.DataFrame, column: str, valid_values: List[Any]) -> List[Dict[str, Any]]:
    issues = []
    if column in df.columns:
        invalid = df[~df[column].isin(valid_values) & df[column].notnull()]
        if not invalid.empty:
            count = len(invalid)
            issues.append({
                "check_name": "Referential Integrity",
                "column_name": column,
                "issue_count": int(count),
                "severity": "HIGH",
                "details": f"{count} invalid values found"
            })
    return issues

def run_all_checks(df: pd.DataFrame, schema: Dict=None, rules: Dict=None, refs: Dict=None) -> QualityReport:
    report = QualityReport(total_rows=len(df))
    report.issues.extend(check_missing_values(df))
    report.issues.extend(check_duplicates(df))
    if schema: report.issues.extend(check_data_types(df, schema))
    if rules: report.issues.extend(check_value_ranges(df, rules))
    if refs:
        for col, valid_vals in refs.items():
            report.issues.extend(check_referential_integrity(df, col, valid_vals))
    return report
