"""
Sample FRED API responses for testing.
"""
import pandas as pd
from datetime import datetime

# Sample GDP data
SAMPLE_GDP_DATA = pd.Series({
    pd.Timestamp('2020-01-01'): 21734.843,
    pd.Timestamp('2020-04-01'): 19520.114,
    pd.Timestamp('2020-07-01'): 21170.252,
    pd.Timestamp('2020-10-01'): 21494.731,
})

# Sample unemployment rate data
SAMPLE_UNRATE_DATA = pd.Series({
    pd.Timestamp('2020-01-01'): 3.6,
    pd.Timestamp('2020-02-01'): 3.5,
    pd.Timestamp('2020-03-01'): 4.4,
    pd.Timestamp('2020-04-01'): 14.7,
})

# Expected JSON response structure
EXPECTED_RESPONSE_STRUCTURE = {
    "tool": str,
    "series_id": str,
    "data": list,
    "metadata": {
        "fetch_date": str,
        "observation_start": str,
        "observation_end": str,
        "total_count": int,
        "date_range": {
            "start": str,
            "end": str
        }
    }
}
