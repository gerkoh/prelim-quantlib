import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
from typing import Iterator
import random
from tqdm import tqdm

load_dotenv()
FMP_API_KEY = os.getenv("FMP_API_KEY")

USER_AGENTS = [
    'Windows 10; Edge', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Chrome OS; Chrome', 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mac OS X; Safari', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Linux; Firefox', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
]
HEADERS = {
    'User-Agent': random.choice(USER_AGENTS)
}

def get_intraday_data(ticker: str, timeframe: str, start_date: str, end_date: str) -> list[dict]:
    """
    Fetches intraday data for a given stock ticker and time range from the Financial Modeling Prep API.

    Args:
        ticker: The stock ticker symbol (NYSE: likely 3 letters, Nasdaq: likely 4 letters).
        timeframe: The timeframe of the data ("1min", "5min", "15min", "30min", "1hour", "4hour").
        start_date: The start date to start scraping from in YYYY-MM-DD format.
        end_date: The end date  to start scraping from in YYYY-MM-DD format.

    Returns:
        A list of dictionaries (JSON response) containing the intraday data if successful, otherwise None.
    """
    collated_data = []
    date_range = _generate_date_range(start_date, end_date, timeframe)
    for generator_start_date, generator_end_date in tqdm(date_range, desc="Scraping data", unit="iteration"):
        url = f"https://financialmodelingprep.com/api/v3/historical-chart/{timeframe}/{ticker}?from={generator_start_date}&to={generator_end_date}&apikey={FMP_API_KEY}"
        data = requests.get(url, headers=HEADERS).json()
        if data: # if response is not [] empty list
            data = reversed(data)
            collated_data.extend(data)
    return collated_data

def get_daily_chart_eod(ticker: str, start_date: str, end_date: str) -> list[dict]:
    """
    Fetches DAILY end-of-day data for a given stock ticker and time range from the Financial Modeling Prep API.

    Args:
        ticker: The stock ticker symbol (NYSE: likely 3 letters, Nasdaq: likely 4 letters).
        start_date: The start date to start scraping from in YYYY-MM-DD format.
        end_date: The end date to start scraping from in YYYY-MM-DD format.

    Returns:
        A list of dictionaries (JSON response) containing the end-of-day data if successful, otherwise None.
    """
    collated_data = []
    date_range = list(_generate_date_range(start_date, end_date, "1day"))
    for generator_start_date, generator_end_date in tqdm(date_range, desc="Scraping data", unit="iteration"):
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={generator_start_date}&to={generator_end_date}&apikey={FMP_API_KEY}"
        data = requests.get(url, headers=HEADERS).json()
        if data: # if response is not [] empty list
            data = reversed(data["historical"])
            collated_data.extend(data)
    return collated_data

def _generate_date_range(start_date: str, end_date: str, timeframe: str) -> Iterator[list[str]]:
    """
    Yields 60-day intervals between start_date and end_date.
    """
    if timeframe == "4hour":
        INTERVAL = 60
    elif timeframe == "1day":
        INTERVAL = 360*5 # ~5 years
    
    if start_date == end_date:
        yield [start_date, end_date]
        return
    else:
        while start_date < end_date:
            # add INTERVAL days to start_date until it reaches end_date
            intermediate_end_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=INTERVAL)
            if intermediate_end_date > datetime.strptime(end_date, "%Y-%m-%d"):
                intermediate_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            yield [start_date, intermediate_end_date.strftime("%Y-%m-%d")]
            start_date = (intermediate_end_date + timedelta(days=1)).strftime("%Y-%m-%d")

if __name__ == "__main__":
    """
    to collect: 
    STOCKS: [NVDA, META, AAPL, GOOGL, TSLA, AMZN, MSFT]
        FB: Listed on 2012-05-18, changed name to Meta on 2021-10-28
    ETFS: [SPY, QQQ, IWM]
    INDEX: [^DJI, ^IXIC]
    """
    today = datetime.today().strftime("%Y-%m-%d")

    #! Get intraday data
    TICKER = "META"
    TIMEFRAME = "4hour" # OPTIONS FOR INTERVAL: 1min, 5min, 15min, 30min, 1hour, 4hour
    START_DATE = "2005-01-01" # define the start, took the first day of 2009, the year after the 2008 financial crisis
    END_DATE = today
    data = get_intraday_data(TICKER, TIMEFRAME, START_DATE, END_DATE)
    with open(f"{TICKER}_{TIMEFRAME}.json", "w") as f:
        json.dump(data, f)

    #! Get daily data
    # TICKER = "META"
    # START_DATE = "2022-06-08" # define the start, took the first day of 2009, the year after the 2008 financial crisis
    # END_DATE = today
    # data = get_daily_chart_eod(TICKER, START_DATE, END_DATE)
    # with open(f"{TICKER}_daily.json", "w") as f:
    #     json.dump(data, f)