"""
dataUtils.py
Version 1.4.3

Created on 2019-05-21
Updated on 2019-12-03

Copyright Ryan Kan 2019

Description: The utilities required to process the data.
"""
# IMPORTS
import datetime

import numpy as np
import pandas as pd
from pandas import read_csv


# FUNCTIONS
def get_data(stock_directory: str, stock_symbol: str):
    """
    Processes data from one subdirectory in the root directory to be parsed later for data training.

    Keyword Arguments:
     - stock_directory, str: Directory which contains the stock values file and the sentiment scores file
     - stock_symbol, str: The stock symbol
    """
    full_path = stock_directory + stock_symbol + "/" + stock_symbol

    # Load stock prices from the CSV file
    stock_data = read_csv(full_path + "_stocks.csv", header=0, squeeze=True)

    # Remove the "Adj Close" and "Volume" column
    stock_data = stock_data.drop(stock_data.columns[list(range(5, 7))], axis=1)

    # Convert stock data to np.array
    stock_arr = stock_data.values

    # Load sentiment data
    sentiment_data = read_csv(full_path + "_sentiments.csv", header=0, squeeze=True)

    # Convert sentiment data to np.array
    sentiment_arr = sentiment_data.values[::-1]

    # Fill in missing values for sentiment data
    sentiment_arr_new = sentiment_arr.copy()

    i = 0
    first_date = sentiment_arr_new[0][0]  # The literal first date

    while i < sentiment_arr_new.shape[0] - 1:
        date1 = datetime.datetime.strptime(sentiment_arr_new[i][0], "%Y-%m-%d")
        date2 = datetime.datetime.strptime(sentiment_arr_new[i + 1][0], "%Y-%m-%d")

        if (date2 - date1).total_seconds() > 60 * 60 * 24:  # More than 1 day
            no_days_separation = int((date2 - date1).total_seconds() / (60 * 60 * 24))
            difference_per_day = (sentiment_arr_new[i + 1][1] - sentiment_arr_new[i][1]) / no_days_separation

            for day in range(1, no_days_separation):
                sentiment_arr_new = np.insert(sentiment_arr_new, i + day, [
                    datetime.datetime.strftime(date1 + datetime.timedelta(days=day), "%Y-%m-%d"),
                    sentiment_arr_new[i][1] + day * difference_per_day], axis=0)

            i += no_days_separation - 1
        i += 1

    sentiment_arr = sentiment_arr_new[:-1]

    # Fill in missing values for stock data
    stock_arr_new = list(stock_arr)

    i = 0
    first_date_processed = datetime.datetime.strptime(first_date, "%Y-%m-%d")
    first_surpassed_index = -1
    while i < len(stock_arr_new[:-1]):
        date1 = datetime.datetime.strptime(stock_arr_new[i][0], "%Y-%m-%d")

        if date1 >= first_date_processed:
            if first_surpassed_index == -1:
                first_surpassed_index = i

            date2 = datetime.datetime.strptime(stock_arr_new[i + 1][0], "%Y-%m-%d")

            if (date2 - date1).total_seconds() > 60 * 60 * 24:  # If it is more than 1 day
                no_days_separation = int((date2 - date1).total_seconds() / (60 * 60 * 24))

                difference_open = (stock_arr_new[i + 1][1] - stock_arr_new[i][1]) / no_days_separation
                difference_high = (stock_arr_new[i + 1][2] - stock_arr_new[i][2]) / no_days_separation
                difference_low = (stock_arr_new[i + 1][3] - stock_arr_new[i][3]) / no_days_separation
                difference_close = (stock_arr_new[i + 1][4] - stock_arr_new[i][4]) / no_days_separation

                for day in range(1, no_days_separation):
                    stock_arr_new.insert(i + day,
                                         [datetime.datetime.strftime(date1 + datetime.timedelta(days=day), "%Y-%m-%d"),
                                          stock_arr_new[i][1] + day * difference_open,
                                          stock_arr_new[i][2] + day * difference_high,
                                          stock_arr_new[i][3] + day * difference_low,
                                          stock_arr_new[i][4] + day * difference_close])

                i += no_days_separation - 1
        i += 1

    stock_arr = np.array(stock_arr_new[first_surpassed_index:-1], dtype=object)

    # Make both start on same day
    if sentiment_arr[0][0] != stock_arr[0][0]:
        if sentiment_arr[0][0] < stock_arr[0][0]:
            while True:
                sentiment_arr = np.delete(sentiment_arr, 0, axis=0)

                if sentiment_arr[0][0] == stock_arr[0][0]:
                    break

        else:  # Must be larger
            while True:
                stock_arr = np.delete(stock_arr, 0, axis=0)

                if sentiment_arr[0][0] == stock_arr[0][0]:
                    break

    # Make both end on same day
    if sentiment_arr[-1][0] != stock_arr[-1][0]:
        if sentiment_arr[-1][0] < stock_arr[-1][0]:
            while True:
                stock_arr = np.delete(stock_arr, stock_arr.shape[0] - 1, axis=0)
                if sentiment_arr[sentiment_arr.shape[0] - 1][0] == stock_arr[stock_arr.shape[0] - 1][0]:
                    break

        else:  # Must be larger
            while True:
                sentiment_arr = np.delete(sentiment_arr, sentiment_arr.shape[0] - 1, axis=0)
                if sentiment_arr[sentiment_arr.shape[0] - 1][0] == stock_arr[stock_arr.shape[0] - 1][0]:
                    break

    # Join the two separate arrays into one single array
    data_arr = []
    for i in range(stock_arr.shape[0]):  # Should have same shape
        data_arr.append([stock_arr[i][0], stock_arr[i][1], stock_arr[i][2], stock_arr[i][3], stock_arr[i][4],
                         sentiment_arr[i][1]])  # The format is: DATE, OPEN, HIGH, LOW, CLOSE, SENTIMENT_VAL

    return np.array(data_arr, dtype=object)


def prep_data(stock_directory: str, stock_symbol: str, entries_taking_avg: int = 10):
    """
    Preprocesses data from the directory for training.

    Keyword Arguments:
     - stock_directory, str: Directory which contains the stock values file and the sentiment scores file
     - stock_symbol, str: The stock symbol
     - entries_taking_avg, int: The number of entries to consider when taking the average
    """

    def normalise(x_i, x_min, x_max, min_value=0, max_value=1):
        """
        Normalises the data to be in the range `min_value` to `max_value`.
        """
        return (((max_value - min_value) * (x_i - x_min)) / (x_max - x_min)) + min_value

    def moving_avg(arr, index, i_val, no_entries_taking_avg):
        """
        Computes the moving average list given an array `arr`.
        """
        return sum([x[index] for x in arr[i_val - no_entries_taking_avg:i_val]]) / no_entries_taking_avg

    # Get the data
    stock_data = get_data(stock_directory, stock_symbol)

    # Take moving average of both the stock values and the sentiment values
    averaged = []

    for i in range(entries_taking_avg, len(stock_data)):  # Remove `entries_taking_avg` entries from the datalist
        averaged.append([moving_avg(stock_data, 1, i, entries_taking_avg),
                         moving_avg(stock_data, 2, i, entries_taking_avg),
                         moving_avg(stock_data, 3, i, entries_taking_avg),
                         moving_avg(stock_data, 4, i, entries_taking_avg),
                         moving_avg(stock_data, 5, i, entries_taking_avg),
                         ])

    # Find min and max from stocks
    min_val = float("inf")
    max_val = -float("inf")

    for entry in averaged:
        # Check for stock values only
        min_val = min(min_val, min(entry[0], min(entry[1], min(entry[2], entry[3]))))
        max_val = max(max_val, max(entry[0], max(entry[1], max(entry[2], entry[3]))))

    # Normalise the stocks' values
    normed = []

    for entry in averaged:
        normed.append([normalise(entry[0], min_val, max_val, min_value=1, max_value=10),
                       normalise(entry[1], min_val, max_val, min_value=1, max_value=10),
                       normalise(entry[2], min_val, max_val, min_value=1, max_value=10),
                       normalise(entry[3], min_val, max_val, min_value=1, max_value=10),
                       entry[4]])

    # Convert `normed` to a pandas dataframe
    df_dict = {"Open": [], "High": [], "Low": [], "Close": [], "Sentiment": []}

    for i in range(len(averaged)):
        df_dict["Open"].append(normed[i][0])
        df_dict["High"].append(normed[i][1])
        df_dict["Low"].append(normed[i][2])
        df_dict["Close"].append(normed[i][3])
        df_dict["Sentiment"].append(normed[i][4])

    df = pd.DataFrame(df_dict)

    return df
