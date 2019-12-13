import re
from time import sleep
from io import StringIO
from datetime import datetime

import requests
from requests.exceptions import HTTPError
import pandas as pd


def get_quote(stock_symbol, start_date, end_date, timeout=3, retry_count=5, retry_delay=1.0):
    curr_retry_count = 0  # Will stop trying if this ever exceeds retry_count

    while True:
        print(f"Attempting to get data from Yahoo Finance... (Attempt {curr_retry_count + 1} of {retry_count})")
        try:
            session = requests.Session()

            # Get crumb form yahoo finance
            response = session.get(f"https://finance.yahoo.com/quote/{stock_symbol}/history?p={stock_symbol}",
                                   timeout=timeout)
            response.raise_for_status()

            match = re.search(r'"CrumbStore":{"crumb":"(.*?)"}', response.text)

            if not match:
                raise ValueError('Could not get crumb from Yahoo Finance')

            else:
                crumb = match.group(1)

            # Get dates
            date_from = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            date_to = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

            # Parse the URL
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_symbol}?period1={date_from}" \
                  f"&period2={date_to}&interval=1d&events=history&crumb={crumb} "

            # Try to get a response
            response = session.get(url)  # This is very finicky, so we might need to run this multiple times
            response.raise_for_status()  # Check if authorised, and if we got the data

            # If succeeded, then we can output the data
            print("Success!")
            break

        except HTTPError:
            if curr_retry_count < retry_count:
                print(f"Failed to obtain data. Trying again in {retry_delay}s.")
                curr_retry_count += 1

                sleep(retry_delay)
            else:
                raise HTTPError("Cannot get Yahoo Finance data at this time. Try again later.")

    return pd.read_csv(StringIO(response.text), parse_dates=['Date'])


df = get_quote("005930.KS", "2018-01-01", "2019-12-13")
print(df)
