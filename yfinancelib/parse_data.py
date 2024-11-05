import json
from datetime import datetime, timezone

def convert_timestamp_to_date_string(timestamp_ms: str | int) -> str:
    """
    Convert a Unix timestamp in milliseconds to a date string in YYYYMMDD format.
    """
    timestamp_ms = int(timestamp_ms)
    timestamp_s = timestamp_ms / 1000
    date = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
    date_str = date.strftime('%Y%m%d')
    return date_str

TICKER = 'NVDA'

json_data = {}

with open(f'yfinancelib/data/{TICKER}.json') as f:
    data = json.load(f)
    
# keep only data from 10 Oct 2022, and closed, volume
for date_in_unix, close_price in data['Close'].items():
    date_in_YYYY_MM_DD = convert_timestamp_to_date_string(date_in_unix)
    
    if date_in_YYYY_MM_DD >= '20221010':
        json_data[date_in_YYYY_MM_DD] = {"close": close_price,
                                         "volume": data['Volume'][date_in_unix]}

with open(f'yfinancelib/cleaned_data/{TICKER}.json', 'w') as f:
    f.write(json.dumps(json_data, indent=4))