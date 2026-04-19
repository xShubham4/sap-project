import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from dataclasses import dataclass, field
from typing import List, Dict, Any
from .config import config

@dataclass
class AnomalyReport:
    flags: List[Dict[str, Any]] = field(default_factory=list)

def detect_zscore_anomalies(df: pd.DataFrame, column: str, threshold: float = config.zscore_threshold) -> List[Dict[str, Any]]:
    flags = []
    if column in df.select_dtypes(include=[np.number]).columns:
        mean = df[column].mean()
        std = df[column].std()
        z_scores = (df[column] - mean) / std
        anomalies = df[np.abs(z_scores) > threshold]
        
        for idx, row in anomalies.iterrows():
            flags.append({
                "row_index": idx,
                "detection_method": "Z-Score",
                "column_name": column,
                "anomaly_score": abs(z_scores[idx]),
                "severity": "HIGH" if abs(z_scores[idx]) > (threshold * 1.5) else "MEDIUM"
            })
    return flags

def detect_iqr_anomalies(df: pd.DataFrame, column: str, multiplier: float = config.iqr_multiplier) -> List[Dict[str, Any]]:
    flags = []
    if column in df.select_dtypes(include=[np.number]).columns:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (multiplier * iqr)
        upper_bound = q3 + (multiplier * iqr)
        anomalies = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        
        for idx, row in anomalies.iterrows():
            dist = max(lower_bound - row[column], row[column] - upper_bound)
            flags.append({
                "row_index": idx,
                "detection_method": "IQR",
                "column_name": column,
                "anomaly_score": float(dist / iqr) if iqr > 0 else float('inf'),
                "severity": "MEDIUM"
            })
    return flags

def detect_time_series_anomalies(df: pd.DataFrame, time_col: str, value_col: str, window: int = 7) -> List[Dict[str, Any]]:
    flags = []
    if time_col in df.columns and value_col in df.columns:
        # Sort and ensure time is datetime
        try:
            df_ts = df.copy()
            df_ts[time_col] = pd.to_datetime(df_ts[time_col])
            df_ts = df_ts.sort_values(by=time_col)
            
            # Calculate rolling mean and std
            rolling_mean = df_ts[value_col].rolling(window=window, min_periods=1).mean()
            rolling_std = df_ts[value_col].rolling(window=window, min_periods=1).std().fillna(0)
            
            # Values that are > 3 moving standard deviations away
            upper_bound = rolling_mean + (3 * rolling_std)
            lower_bound = rolling_mean - (3 * rolling_std)
            
            # Avoid divide by zero error if std is 0
            safe_std = rolling_std.replace(0, 1)
            
            anomalies = df_ts[(df_ts[value_col] > upper_bound) | (df_ts[value_col] < lower_bound)]
            
            for idx, row in anomalies.iterrows():
                # Avoid dividing by zero if safe_std is zero for some reason (which we replaced above)
                dev = abs(row[value_col] - rolling_mean[idx])
                score = dev / safe_std[idx] if safe_std[idx] > 0 else 0
                # only report true anomalies
                if score > 3:
                     flags.append({
                         "row_index": idx,
                         "detection_method": "TimeSeries-RollingZ",
                         "column_name": value_col,
                         "anomaly_score": float(score),
                         "severity": "HIGH"
                     })
        except Exception as e:
            # Silently pass if time format is wrong to avoid pipeline crashing
            pass
    return flags

def detect_isolation_forest(df: pd.DataFrame, columns: List[str], contamination: float = config.contamination) -> List[Dict[str, Any]]:
    flags = []
    numeric_cols = [col for col in columns if col in df.select_dtypes(include=[np.number]).columns]
    if len(numeric_cols) > 0:
        # Impute missing before IF
        data = df[numeric_cols].fillna(df[numeric_cols].median())
        clf = IsolationForest(contamination=contamination, random_state=config.random_state)
        preds = clf.fit_predict(data)
        # Decision function returns average anomaly score, negative is anomalous
        scores = clf.decision_function(data)
        
        anomalies_idx = np.where(preds == -1)[0]
        for i in anomalies_idx:
            flags.append({
                "row_index": int(data.index[i]),
                "detection_method": "IsolationForest",
                "column_name": "MULTIVARIATE",
                "anomaly_score": float(-scores[i]), # higher positive score = more anomalous
                "severity": "HIGH"
            })
    return flags

def detect_all_anomalies(df: pd.DataFrame, columns: List[str] = None) -> AnomalyReport:
    report = AnomalyReport()
    numeric_cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        report.flags.extend(detect_zscore_anomalies(df, col))
        report.flags.extend(detect_iqr_anomalies(df, col))
    
    if len(numeric_cols) > 1:
        report.flags.extend(detect_isolation_forest(df, numeric_cols))
        
    if 'timestamp' in df.columns:
        for col in numeric_cols:
             report.flags.extend(detect_time_series_anomalies(df, 'timestamp', col))
    
    return report