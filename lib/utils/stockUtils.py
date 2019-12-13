"""
stockUtils.py

Created on 2019-12-11
Updated on 2019-12-13

Copyright Ryan Kan 2019

Description: The utilities required to obtain the stock data from Yahoo Finance.
"""

# IMPORTS
from datetime import datetime
from urllib import request

import pandas as pd
from bs4 import BeautifulSoup


# FUNCTIONS
def get_html_rows(symbol: str, start_date: str, end_date: str):
    """
    Gets the HTML rows data of the stock symbol.

    Keyword arguments:
    - symbol, str: The stock symbol. E.G. AMZN, TSLA, BA
    - start_date, str: The start date, in the form YYYY-MM-DD
    - end_date, str: The end date, in the form YYYY-MM-DD

    Returns:
    - The HTML rows parameter, which is needed for the function `get_historical_data`.
    """
    # Get dates' epoch timestamps
    start_epoch = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
    end_epoch = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())

    # Generate URL
    url = f"https://finance.yahoo.com/quote/{symbol}/history?period1={start_epoch}&period2={end_epoch}&interval=1d" \
          f"&frequency=1d/ "
    print(url)
    # Check the HTML of that web page
    try:
        rows = BeautifulSoup(request.urlopen(url).read(), features="lxml").findAll("table")[0].tbody.findAll("tr")

        # Check if is right page
        if rows[0].findAll("td")[1].span.text is None:  # That means that the page has no "Dividend" attribute
            # Which means the page is wrong
            raise IndexError

    except IndexError:
        raise NameError(f"Stock symbol not found! Please check the entered stock symbol. (ENTERED: '{symbol}')")

    return rows


def get_historical_data(symbol: str, start_date: str, end_date: str):
    """
    Obtains the historical data of a stock from Yahoo Finance.

    Keyword arguments:
    - symbol, str: The stock symbol. E.G. AMZN, TSLA, BA
    - start_date, str: The start date, in the form YYYY-MM-DD
    - end_date, str: The end date, in the form YYYY-MM-DD

    Returns:
    - The stock data for that number of days
    """
    data = []  # Where all the stock data will be housed

    # Obtain HTML data
    rows = get_html_rows(symbol, start_date, end_date)

    # Process HTML data
    for row in rows:
        possible_stock_entry = row.findAll("td")

        try:
            if possible_stock_entry[1].span.text != "Dividend":  # Ignore dividend
                # Append HTML data to the data array
                data.append({"date": possible_stock_entry[0].span.text,  # This is in YYYY-MM-DD format
                             "open": float(possible_stock_entry[1].span.text.replace(",", "")),
                             "high": float(possible_stock_entry[2].span.text.replace(",", "")),
                             "low": float(possible_stock_entry[3].span.text.replace(",", "")),
                             "close": float(possible_stock_entry[4].span.text.replace(",", "")),
                             "volume": int(possible_stock_entry[6].span.text.replace(",", ""))})
        except AttributeError:
            # This means that that day might not have any data, so skip
            print(row)
            pass

    return data


def process_historical_data(data: list):
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


def save_stocks_as_csv(stock_df: pd.DataFrame):
    """
    Saves the stocks dataframe as a .csv file.

    Keyword arguments:
    - stock_df, pd.DataFrame: The stocks dataframe.
    """
    # Rename dataframe columns
    print(stock_df)


# DEBUG CODE
if __name__ == "__main__":
    stockSymbol = input("Please enter the stock symbol: ")
    outputAsFile = input("Should the output be a .csv file? [Y]es or [N]o: ") == ("Y" or "Yes")

    print("\nFor the ENDING date, ensure that it is MORE RECENT than the STARTING date.")
    startDate = input("Please enter the starting date in the form YYYY-MM-DD: ")
    endDate = input("Please enter the ending date in the form YYYY-MM-DD:  ")

    histData = get_historical_data(stockSymbol, startDate, endDate)
    dataframe = process_historical_data(histData)

    # Output generated dataframe
    if outputAsFile:
        save_stocks_as_csv(dataframe)

    else:
        print(dataframe)
