"""
stockUtils.py

Created on 2019-12-11
Updated on 2019-12-12

Copyright Ryan Kan 2019

Description: The utilities required to obtain the stock data from Yahoo Finance.
"""
# IMPORTS
from urllib import request
from bs4 import BeautifulSoup

import pandas as pd


# FUNCTIONS
def get_html_rows(symbol: str):
    """
    Gets the HTML rows data of the stock symbol.

    Keyword arguments:
    - symbol, str: The stock symbol. E.G. AMZN, TSLA, BA

    Returns:
    - The HTML rows parameter, which is needed for the function `get_historical_data`.
    """
    url = "https://finance.yahoo.com/quote/" + symbol + "/history/"

    try:
        rows = BeautifulSoup(request.urlopen(url).read(), features="lxml").findAll("table")[0].tbody.findAll("tr")

    except IndexError:
        raise NameError(f"Stock symbol not found! Please check the entered stock symbol. (ENTERED: '{symbol}')")

    return rows


def get_historical_data(symbol: str, number_of_days: int = 10):
    """
    Obtains the historical data of a stock from Yahoo Finance.

    Keyword arguments:
    - symbol, str: The stock symbol. E.G. AMZN, TSLA, BA
    - number_of_days, int: The number of days to obtain the data for. (Default = 10)

    Returns:
    - The stock data for that number of days
    """
    data = []  # Where all the stock data will be housed

    # Obtain HTML data
    rows = get_html_rows(symbol)

    # Process HTML data
    for row in rows:
        possible_stock_entry = row.findAll('td')
        if possible_stock_entry[1].span.text != 'Dividend':  # Ignore dividend
            # Append HTML data to the data array
            data.append({"date": possible_stock_entry[0].span.text,  # This is in YYYY-MM-DD format
                         "open": float(possible_stock_entry[1].span.text.replace(",", "")),
                         "high": float(possible_stock_entry[2].span.text.replace(",", "")),
                         "low": float(possible_stock_entry[3].span.text.replace(",", "")),
                         "close": float(possible_stock_entry[4].span.text.replace(",", "")),
                         "volume": int(possible_stock_entry[6].span.text.replace(",", ""))})

    return data[:number_of_days]


def process_historical_data(data):
    """
    Processes the raw data to be placed in a pandas Dataframe.

    Keyword arguments:
    - data, list: The data list, which will be returned by the `get_historical_data` function.

    Returns:
    - Pandas DataFrame with the processed data.
    """
    # Reformat dates into a datetime object
    for row in data:
        row["date"] = pd.to_datetime(row["date"]).date()

    # Reformat into pandas dataframe
    df = pd.DataFrame(data)

    # Set date column as index
    df = df.set_index("date")

    # Return processed dataframe
    return df


# DEBUG CODE
if __name__ == "__main__":
    histData = get_historical_data("BA", 15)
    dataframe = process_historical_data(histData)

    print(dataframe)
