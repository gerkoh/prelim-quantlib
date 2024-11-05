Collected information from FMP historical-chart API, containing the intraday data
https://site.financialmodelingprep.com/developer/docs#charts
https://site.financialmodelingprep.com/developer/docs#technicals

## How to use the API
### Daily
- Make request to `https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={generator_start_date}&to={generator_end_date}&apikey={FMP_API_KEY}`

### Intraday
- Make request to `https://financialmodelingprep.com/api/v3/historical-chart/{timeframe}/{ticker}?from={generator_start_date}&to={generator_end_date}&apikey={FMP_API_KEY}`

# Set up cron
Auto downloader runs every Tuesday to Saturday at 5pm
```
0 17 * * 2-6 * cd {root} && source venv/bin/activate && cd fmplib && source .env && ../venv/bin/python3.12 download_daily.py &>fmplib/cronjob.log
```