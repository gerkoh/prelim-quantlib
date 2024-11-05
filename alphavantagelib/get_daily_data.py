import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
REQUIRED_FUNCTION = "TIME_SERIES_DAILY"
REQUIRED_SYMBOL = "NVDA"
OPTIONAL_OUTPUTSIZE = "full"

url = f'https://www.alphavantage.co/query?outputsize={OPTIONAL_OUTPUTSIZE}&function={REQUIRED_FUNCTION}&symbol={REQUIRED_SYMBOL}&datatype=json&apikey={API_KEY}'
r = requests.get(url)
data = r.json()

save_path = Path(__file__).parent / f'{REQUIRED_SYMBOL}.json'

with open(save_path, 'w') as f:
    f.write(str(data))