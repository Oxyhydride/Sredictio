"""
stockUtils.py

Created on 2019-12-11
Updated on 2019-12-28

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
def get_ohlcv_crumb(session, stock_symbol, timeout=3):
    """
    Gets the crumb of the Yahoo Finance web page.

    Args:
        session (requests.Session): The `requests.Session` object.

                                    This will be used as a handler to get the crumb data from
                                    Yahoo Finance.

        stock_symbol (str): The stock symbol, also known as the stock ticker.
                            For example, "FB", "TSLA" and "AMZN" are all valid stock symbols.

        timeout (int): The duration to wait for, in seconds, before the web page request will
                       raise a timeout error. (Default = 3)

    Returns:
        str: The Yahoo Finance crumb.

    Yields:
        ValueError: If the crumb of that particular stock could not be obtained.

    """
    # Try to get the crumb
    response = session.get(f"https://finance.yahoo.com/quote/{stock_symbol}/history?p={stock_symbol}",
                           timeout=timeout)
    response.raise_for_status()  # Will return a HTTP error if it is forbidden

    match = re.search(r'"CrumbStore":{"crumb":"(.*?)"}', response.text)  # Get the crumb via a regex search

    # Check if crumb was obtained
    if not match:
        raise ValueError('Could not get crumb from Yahoo Finance')

    else:
        crumb = match.group(1)

    return crumb


def get_ohlcv_data(stock_symbol, start_date, end_date, timeout=3, retry_count=5, retry_delay=1.0, verbose=True,
                   save_as_csv=False, file_location=None):
    """
    Obtains the OHLCV data of a stock from Yahoo Finance.

    Args:
        stock_symbol (str): Stock symbol. Also known as the stock ticker.
                            For example, "FB", "TSLA" and "AMZN" are all valid stock symbols.

        start_date (str): The first date to scrape the data. Note that the start date has to be
                          OLDER than the end date.

                          Note that the date has to be in the form YYYY-MM-DD.

        end_date (str): The last date to scrape the data. Note that the end date has to be MORE
                        RECENT than the start date.

                        The end date has to be in the form YYYY-MM-DD.

        timeout (int): The duration to wait for, in seconds, before the web page request will
                       raise a timeout error. (Default = 3)

        retry_count (int): The number of times to attempt to get the Yahoo Finance data before
                           failing. (Default = 5)

        retry_delay (float): The duration to wait, in seconds, between attempts if the attempt
                             fails. (Default = 1.0)

        verbose (bool): The value to this parameter is the answer to the statement "The program
                        outputs intermediate messages". (Default = True)

        save_as_csv (bool): Should the pandas dataframe be saved as a .csv file? (Default = False)

        file_location (str): Where should the .csv file be placed? What should the .csv file be
                             named as? (Default = None)

                             If `save_as_csv` is True, then this parameter MUST also be filled.

    Returns:
        pd.DataFrame: The stock data for that number of days (if `save_as_csv` is False)

    """

    # Get stock data from Yahoo Finance
    curr_retry_count = 0  # Will stop trying if this ever exceeds `retry_count`

    while True:
        if verbose:
            print(f"Attempting to get {stock_symbol} data from Yahoo Finance... (Attempt {curr_retry_count + 1} of " +
                  f"{retry_count})")
        try:
            session = requests.Session()

            # Get crumb from Yahoo Finance
            crumb = get_ohlcv_crumb(session, stock_symbol, timeout=timeout)

            # Get period to scrape data
            date_from = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
            date_to = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

            # Generate the URL
            url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_symbol}?period1={date_from}" \
                  f"&period2={date_to}&interval=1d&events=history&crumb={crumb} "

            # Try to get a response
            response = session.get(url)  # This is very finicky, so we might need to run this multiple times
            response.raise_for_status()  # Will also return a HTTP error if it is forbidden

            # If it succeeded, then we can output the data
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
    stock_df = pd.read_csv(StringIO(response.text), parse_dates=['Date'])  # Process result as a .csv

    # Drop all null values
    stock_df.dropna(inplace=True)

    # Set the volume column's values to integers
    stock_df["Volume"] = stock_df["Volume"].astype(int)

    # Output the dataframe
    if not save_as_csv:
        # Return the dataframe directly
        return stock_df

    else:
        # Save the dataframe as a csv file
        stock_df.to_csv(file_location, index=False)


def process_ohlcv_data(df):
    """
    Processes converts the scraped dataframe into a more useful dataframe

    Args:
        df (pd.DataFrame): The dataframe which has been returned by the
                           `get_historical_data` function.

    Returns:
        pd.DataFrame: The processed pandas dataframe.

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
    # Ask for user input
    stockSymbol = input("Please enter the stock symbol: ")
    outputAsFile = input("Should the output be a .csv file? [Y]es or [N]o: ") == ("Y" or "Yes")

    print("\nFor the ENDING date, ensure that it is MORE RECENT than the STARTING date.")
    startDate = input("Please enter the starting date in the form YYYY-MM-DD: ")
    endDate = input("Please enter the ending date in the form YYYY-MM-DD:   ")

    # Get the stock data
    ohlcvDF = get_ohlcv_data(stockSymbol, startDate, endDate, save_as_csv=outputAsFile,
                             file_location="../../Training Data/" + stockSymbol + "/" + stockSymbol + "_stocks.csv")

    # Output generated dataframe
    if not outputAsFile:
        print(ohlcvDF)

    else:
        print("Done!")
