"""
obtainData.py

Created on 2019-12-12
Updated on 2019-12-12

Copyright Ryan Kan 2019

Description: A function which obtains the data needed for the full observation list.
"""

# IMPORTS
from datetime import datetime, timedelta, date
import os

import pandas as pd

from lib.utils.miscUtils import natural_sort
from lib.utils.sentimentUtils import get_sentiment_data
from lib.utils.stockUtils import get_stock_data, process_stock_data


# FUNCTIONS
def get_model_file(model_dir: str):
    """
    Gets the latest model file from the model directory.

    Keyword arguments:
    - model_dir, str: The model directory.

    Returns:
    - The latest model's file name (String)
    """
    # List all files in the model_dir
    all_model_files = natural_sort(os.listdir(model_dir))

    # Get latest model
    model_file_name = "NO_FILE_FOUND!"
    for file_name in all_model_files:
        if file_name[:7] == "LATEST=":
            model_file_name = file_name
            break

    # Check if the latest model was found
    assert model_file_name != "NO_FILE_FOUND!", "A model with the prefix 'LATEST=' was not found. Please append that " \
                                                "prefix to the latest model file. "

    # Return model file
    return model_file_name


def get_lookback_window(model_file_name: str):
    """
    Gets the needed lookback window from the model file name.

    Keyword arguments:
    - model_file_name, str: The latest model's file name

    Returns:
    - The lookback window for that model (Integer)
    """
    # Get Look Back Window
    return int(model_file_name.split("_")[1][4:])  # Obtains the look back window from the model file


def get_obs_data(stock_name: str, stock_symbol: str, stock_history_file: str, lookback_window: int,
                 days_to_scrape: int = 100, retry_count: int = 3):
    """
    Gets the data needed to generate the observation array.

    Keyword arguments:
    - stock_name, str: The stock name.
    - stock_symbol, str: The stock symbol. (aka ticker)
    - lookback_window, int: The lookback window.
    - stock_history_file, str: The file which contains all the stock transaction histories.
    - days_to_scrape, int: The number of days to scrape the data. (Default = 100)
    - retry_count, int: The number of attempts to get the stock data from yahoo before failing. (Default = 3)

    Returns:
    - The stock dataframe
    - The sentiment dataframe
    - The "owned stock history" array
    - The look back window.
    """
    # Check if look back window is sufficient
    assert int(2.5 * lookback_window) < days_to_scrape, "Days to scrape data has to be larger than 2.5 times the look" \
                                                        " back window. "

    # Get stock data
    # First get the historical data
    historical_data = get_stock_data(stock_symbol,
                                     (datetime.today() - timedelta(days=days_to_scrape)).strftime("%Y-%m-%d"),
                                     datetime.today().strftime("%Y-%m-%d"),
                                     retry_count=retry_count)

    # Then process it as a pandas dataframe
    stock_dataframe = process_stock_data(historical_data)

    # Get sentiment data
    print(f"Obtaining {stock_name} sentiment data...")

    sentiment_dataframe = get_sentiment_data(stock_symbol, stock_name,
                                             (date.today() - timedelta(days=days_to_scrape)).strftime("%Y-%m-%d"),
                                             date.today().strftime("%Y-%m-%d"), verbose=False, to_csv=False)

    # Get owned stock history
    print(f"Obtaining owned stock history...")

    owned_stock_array = pd.read_csv(stock_history_file).to_numpy()

    print("Done!")

    # Return the dataframes
    return stock_dataframe, sentiment_dataframe, owned_stock_array


# DEBUG CODE
if __name__ == "__main__":
    # First, get the lookback window
    lookbackWindow = get_lookback_window(get_model_file("../../Models"))

    # Next, get the needed data
    stockDataframe, sentimentDataframe, ownedStockArray = get_obs_data("Facebook", "FB", "../../Stock History.csv",
                                                                       lookbackWindow)

    # Output them
    print(lookbackWindow)
    print(stockDataframe)
    print(sentimentDataframe)
    print(ownedStockArray)
