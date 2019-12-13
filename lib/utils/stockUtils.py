"""
stockUtils.py

Created on 2019-12-11
Updated on 2019-12-13

Copyright Ryan Kan 2019

Description: The functions required to obtain the stock data from Yahoo Finance.
"""

# IMPORTS
import re
from datetime import datetime
from io import StringIO
from time import sleep

import pandas as pd
import requests
from requests.exceptions import HTTPError


# FUNCTIONS
def get_stock_data(stock_symbol: str, start_date: str, end_date: str, timeout: int = 3, retry_count: int = 5,
                   retry_delay: float = 1.0, save_as_csv: bool = False, file_location: str = None,
                   verbose: bool = True):
    """
    Obtains the historical data of a stock from Yahoo Finance.

    Keyword arguments:
    - stock_symbol, str: The stock symbol. E.G. AMZN, TSLA, BA
    - start_date, str: The first date to scrape the data. Note that the start date has to be OLDER than the end date.
                       The date has to also be in the form YYYY-MM-DD.
    - end_date, str: The last date to scrape the data. Note that the end date has to be MORE RECENT than the start
                     date. The end date has to also be in the form YYYY-MM-DD.
    - timeout, int: The duration to wait for, in seconds, before the web page request will raise a timeout error.
                    (Default = 3)
    - retry_count, int: The number of times to attempt to get the Yahoo Finance data before failing. (Default = 5)
    - retry_delay, float: The duration to wait, in seconds, between attempts if the attempt fails. (Default = 1.0)
    - save_as_csv, bool: Should the pandas dataframe be saved as a .csv file? (Default = False)
    - file_location, str: If `save_as_csv` is True, then this parameter MUST also be filled. Where should the .csv
                          file be placed? What should the .csv file be named as? (Default = None)
    - verbose, bool: The value to this parameter is the answer to the statement "The program outputs messages".
                     (Default = True)

    Returns:
    - The stock data for that number of days (if `save_as_csv` is False)
    """
    curr_retry_count = 0  # Will stop trying if this ever exceeds retry_count

    while True:
        if verbose:
            print(f"Attempting to get {stock_symbol} data from Yahoo Finance... (Attempt {curr_retry_count + 1} of " +
                  f"{retry_count})")
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
            if verbose:
                print("Success!")

            break

        except HTTPError:
            if curr_retry_count <= retry_count:
                if verbose:
                    print(f"Failed to obtain data. Trying again in {retry_delay}s.")

                curr_retry_count += 1

                sleep(retry_delay)
            else:
                raise HTTPError("Cannot get Yahoo Finance data at this time. Try again later.")

    # Save the response as a dataframe
    stock_df = pd.read_csv(StringIO(response.text), parse_dates=['Date'])

    # Drop null values
    stock_df.dropna(inplace=True)

    # Set the volume column to integers
    stock_df["Volume"] = stock_df["Volume"].astype(int)

    # Output
    if not save_as_csv:
        return stock_df

    else:
        # Save the dataframe as a csv file
        stock_df.to_csv(file_location, index=False)


def process_stock_data(df: pd.DataFrame):
    """
    Processes the raw data to be placed in a pandas Dataframe.

    Keyword arguments:
    - data, pd.DataFrame: The dataframe which has been returned by the `get_historical_data` function.

    Returns:
    - The processed pandas dataframe.
    """
    # Rename columns
    df = df.rename(columns={"Date": "date",
                            "Open": "open",
                            "High": "high",
                            "Low": "low",
                            "Close": "close",
                            "Volume": "volume"})

    # Remove "Adj Close" column
    df = df.drop(df.columns[5], axis=1)

    # Set date as index
    df = df.set_index("date")

    # Return processed dataframe
    return df


# DEBUG CODE
if __name__ == "__main__":
    stockSymbol = input("Please enter the stock symbol: ")
    outputAsFile = input("Should the output be a .csv file? [Y]es or [N]o: ") == ("Y" or "Yes")

    print("\nFor the ENDING date, ensure that it is MORE RECENT than the STARTING date.")
    startDate = input("Please enter the starting date in the form YYYY-MM-DD: ")
    endDate = input("Please enter the ending date in the form YYYY-MM-DD:   ")

    stockDF = get_stock_data(stockSymbol, startDate, endDate, save_as_csv=outputAsFile,
                             file_location="../../Training Data/" + stockSymbol + "/" + stockSymbol + "_stocks.csv")

    # Output generated dataframe
    if not outputAsFile:
        print(stockDF)

    else:
        print("Done!")
