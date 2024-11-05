import requests
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
TICKER = "NVDA"

# for getting stock splits
url = f'https://api.polygon.io/v3/reference/splits?ticker={TICKER}&order=desc&limit=1000&sort=execution_date&apiKey={API_KEY}'

r = requests.get(url)
data = r.json()

save_path = Path('json_data/nvda.json')

with open(save_path, 'w') as f:
    f.write(str(data))