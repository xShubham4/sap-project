try:
    from src.dataguard.quality_checks import check_missing_values, check_duplicates
    import pandas as pd
    import numpy as np

    def test_missing_values():
        df = pd.DataFrame({'A': [1, 2, np.nan], 'B': [0, 0, 0]})
        issues = check_missing_values(df)
        assert len(issues) == 1
        assert issues[0]['column_name'] == 'A'
except ImportError:
    pass