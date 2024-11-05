from datetime import datetime, timedelta
from pathlib import Path
import logging
from scraper import get_daily_chart_eod, get_intraday_data
import json
from instrument_lookup import INSTRUMENT_TYPE_LOOKUP

DATA_ROOT = Path("data")

logging.basicConfig(
    format = "%(levelname)s:%(name)s:%(message)s",
    level = logging.INFO,
    filename = DATA_ROOT / "scraper.log"
)

yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
date_to_scrape = "2024-11-01" # yesterday # "YYYY-MM-DD" format; run daily on tues - sat

def data_in_correct_format(timeframe: str, data: list[dict[str, float | str]]) -> bool:
    """
    Verify that the data is in the correct format for the given timeframe.
    """
    if data == []:
        return False
    if len(data) != 1:
        return False
    else:
        data = data[0]  # take first element
        match timeframe:
            case "1d":
                # date, open, high, low, close, adjClose, volume, unadjustedVolume, change, changePercent, vwap, label, changeOverTime
                if (
                    "date" in data and
                    "open" in data and
                    "high" in data and
                    "low" in data and
                    "close" in data and
                    "adjClose" in data and
                    "volume" in data and
                    "unadjustedVolume" in data and
                    "change" in data and
                    "changePercent" in data and
                    "vwap" in data and
                    "label" in data and
                    "changeOverTime" in data
                ):
                    return True
            case "4h":
                # date, open, low, high, close, volume
                if (
                    "date" in data and
                    "open" in data and
                    "low" in data and
                    "high" in data and
                    "close" in data
                ):
                    return True
            case _:
                print("not supported")

TIMEFRAMES = ["1d"]
#! TIMEFRAMES = ["1d", "4h"] - add support for 4h, and for more tickers
TICKERS = ["SPY", "QQQ", "IWM", "TLT", "AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "TSLA"]
PORTFOLIO = ["CLSK", "MARA", "IREN", "CIFR", "COIN", "WULF", "RIOT", "BITF", "PYPL"]

for timeframe in TIMEFRAMES:
    logging.info(f"Downloading {timeframe} data for {TICKERS} from {date_to_scrape}.")
    for ticker in TICKERS:
        if timeframe == "1d":
            data: list[dict] = get_daily_chart_eod(ticker, date_to_scrape, date_to_scrape)
        elif timeframe == "4h":
            data: list[dict] = get_intraday_data(ticker, date_to_scrape)
        if data:
            if data_in_correct_format(timeframe, data):
                try:
                    with open(DATA_ROOT / INSTRUMENT_TYPE_LOOKUP[ticker] / timeframe / f"{ticker}.json", "r") as f:
                        original_file_data = json.load(f)
                    original_file_data.append(data[0])  # unpack first and only element
                    with open(DATA_ROOT / INSTRUMENT_TYPE_LOOKUP[ticker] / timeframe / f"{ticker}.json", "w") as f:
                        json.dump(original_file_data, f)
                except Exception as e:
                    logging.error(f"Error writing {ticker} data to file. Data: {data}. Caught exception: {e}")
            else:
                logging.error(f"{ticker} has an incorrect data format for the {timeframe} timeframe on {date_to_scrape}. Error: {data}")
        else:
            logging.error(f"{ticker} has no data for the {timeframe} timeframe on {date_to_scrape}. Error: data == {data}")
    logging.info(f"{timeframe} data downloaded.")