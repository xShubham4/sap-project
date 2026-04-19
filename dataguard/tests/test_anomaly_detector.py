try:
    from src.dataguard.anomaly_detector import detect_zscore_anomalies
    import pandas as pd
    import numpy as np

    def test_zscore():
        df = pd.DataFrame({'A': [1, 2, 3, 4, 1000]})
        flags = detect_zscore_anomalies(df, 'A', threshold=1.5)
        assert len(flags) > 0
        assert flags[0]['row_index'] == 4
except ImportError:
    pass