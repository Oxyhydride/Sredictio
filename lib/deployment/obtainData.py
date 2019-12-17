"""
obtainData.py

Created on 2019-12-12
Updated on 2019-12-14

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
def get_model_file(model_dir):
    """
    Gets the latest model file from the model directory.

    Args:
        model_dir (str): The model directory.

                         The model directory is the directory where all the models, current and previous,
                         are stored. By default, the model directory for Sredictio is `Models`, in the
                         main directory. This makes obtaining the model file easier.

    Returns:
        str: The latest model's file name.
             The latest model file will be in the `model_dir`, and its name will follow this format:
             "LATEST={Model Prefix}_LBW-{Lookback Window}_NOI-{Number of Iterations}.zip".

    Raises:
        AssertionError: If no file with the prefix "LATEST=" is found.

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
    assert model_file_name != "NO_FILE_FOUND!", "A model with the prefix 'LATEST=' was not found. Please append that" \
                                                + " prefix to the latest model file. "

    # Return model file
    return model_file_name


def get_lookback_window(model_file_name):
    """
    Gets the needed lookback window from the model's filename.

    Args:
        model_file_name (str): The latest model's filename.

    Returns:
        int: The lookback window for that particular model

    Examples:
        >>> LBW = get_lookback_window("LATEST=MyPrefix_LBW-7_NOI-9.zip")  # This may be a real model file
        >>> print(LBW)
        7

    """
    # Get Lookback Window
    return int(model_file_name.split("_")[1][4:])  # Obtains the look back window from the model file


def get_obs_data(stock_name, stock_symbol, stock_history_file, lookback_window, days_to_scrape=100, retry_count=5):
    """
    Gets the data needed to generate the observation array.

    Args:
        stock_name (str): The stock name.
                          For example, "Apple", "Tesla", "Boeing", "Disney".

        stock_symbol (str): The stock symbol. Also known as the stock ticker.
                            For example, "AAPL", "TSLA", "BA", "DIS".

        stock_history_file (str): The file which contains all the stock transaction histories.

                                  By default, this file would've been named `Stock History.csv`. However,
                                  some may choose to rename this file. Hence, remember to specify the
                                  renamed `stock_history_file` correctly.

        lookback_window (int): The lookback window for the model.

                               The lookback window can be obtained by passing the model's filename as an
                               argument in the `get_lookback_window` function. This will return an
                               integer, which is the lookback_window.

        days_to_scrape (int): The number of days to scrape the data. (Default = 100)

                              When scraping OHLCV data and the Sentiment data, the program needs to know
                              how many days of data to scrape. This argument specifies that number of
                              days to scrape data.

        retry_count (int): The number of attempts to get the stock data from Yahoo Finance before giving
                           up. (Default = 3)

    Returns:
        pd.DataFrame: The OHLCV dataframe.
        pd.Dataframe: The sentiment dataframe, which contains all the sentiment data from that range of
                      days.
        np.ndarray: The "owned stock history" array, which lists the number of stocks you own for every
                    stock.

    """
    # Check if look back window is sufficient
    assert int(2.5 * lookback_window) < days_to_scrape, "Days to scrape data has to be larger than 2.5 times the look" \
                                                        " back window. "

    # Get the historical OHLCV data
    historical_data = get_stock_data(stock_symbol,
                                     (datetime.today() - timedelta(days=days_to_scrape)).strftime("%Y-%m-%d"),
                                     datetime.today().strftime("%Y-%m-%d"),
                                     retry_count=retry_count)

    # Process the OHLCV data as a pandas dataframe
    stock_dataframe = process_stock_data(historical_data)

    # Get the sentiment data
    print(f"Obtaining {stock_name} sentiment data...")

    sentiment_dataframe = get_sentiment_data(stock_symbol, stock_name,
                                             (date.today() - timedelta(days=days_to_scrape)).strftime("%Y-%m-%d"),
                                             date.today().strftime("%Y-%m-%d"), verbose=False, to_csv=False)

    # Get the owned stock history
    print(f"Obtaining owned stock history...")

    owned_stock_array = pd.read_csv(stock_history_file).to_numpy()

    print("Done!")

    # Return the obtained dataframes (and the np.ndarray)
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
