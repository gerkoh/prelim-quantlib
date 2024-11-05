import yfinance as yf
import requests_cache

TICKER = 'MSTR'
PATH_TO_SAVE_DATA = f'data/{TICKER}.json'

session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-agent'] = 'my-program/1.0'
ticker = yf.Ticker(ticker=TICKER, session=session)

data = ticker.history(period='max').to_json(path_or_buf=PATH_TO_SAVE_DATA)