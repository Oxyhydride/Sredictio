"""
trainingDataUtils.py

Created on 2019-05-21
Updated on 2019-12-16

Copyright Ryan Kan 2019

Description: The utilities required to process the data.
"""
# IMPORTS
import datetime

import numpy as np
import pandas as pd
import ta
from pandas import read_csv

from lib.utils.miscUtils import moving_average


# FUNCTIONS
def obtain_data(data_directory, stock_symbol):
    """
    Gets the training data from the data directory.

    Args:
        data_directory (str): The directory which contains the OHLCV data file (a.k.a. stocks
                              file) and the sentiment data file.

        stock_symbol (str): The stock symbol. Also known as the stock ticker.
                            For example, "AAPL", "GOOGL" and "TSLA" are all valid stock symbols.

    Returns:
        - np.ndarray: Array containing all the relevant values for the environment

    """
    # Generate the full path to the files
    full_path = data_directory + stock_symbol + "/" + stock_symbol

    # Load OHLCV values from the CSV file
    ohlcv_data = read_csv(full_path + "_stocks.csv", header=0, squeeze=True)

    # Remove the "Adj Close" column (which is the 6th column)
    ohlcv_data = ohlcv_data.drop(ohlcv_data.columns[5], axis=1)

    # Convert stock data to `np.ndarray`
    ohlcv_arr = ohlcv_data.values

    # Load sentiment data
    sentiment_data = read_csv(full_path + "_sentiments.csv", header=0, squeeze=True)

    # Convert sentiment data to `np.ndarray`
    sentiment_arr = sentiment_data.values[::-1]

    # Fill in missing values for sentiment data
    sentiment_arr_new = sentiment_arr.copy()

    i = 0
    first_date = sentiment_arr_new[0][0]  # The first date of the sentiment data

    while i < sentiment_arr_new.shape[0] - 1:
        # Obtain current date and next date
        curr_date = datetime.datetime.strptime(sentiment_arr_new[i][0], "%Y-%m-%d")
        next_date = datetime.datetime.strptime(sentiment_arr_new[i + 1][0], "%Y-%m-%d")

        # Check if the date difference is more than one day
        if (next_date - curr_date).days > 1:
            # Get the difference in days
            days_difference = int((next_date - curr_date).days)

            # Estimate the sentiment increase/decrease in that period using linear fitting
            difference_per_day = (sentiment_arr_new[i + 1][1] - sentiment_arr_new[i][1]) / days_difference

            # Use that value to fill in the missing data
            for day in range(1, days_difference):
                sentiment_arr_new = np.insert(sentiment_arr_new, i + day, [
                    datetime.datetime.strftime(curr_date + datetime.timedelta(days=day), "%Y-%m-%d"),
                    sentiment_arr_new[i][1] + day * difference_per_day], axis=0)

            i += days_difference - 1
        i += 1

    # Reverse the array
    sentiment_arr = sentiment_arr_new[:-1]

    # Fill in missing values for OHLCV data
    ohlcv_arr_new = list(ohlcv_arr)

    i = 0
    first_date_processed = datetime.datetime.strptime(first_date, "%Y-%m-%d")
    first_surpassed_index = -1

    while i < len(ohlcv_arr_new[:-1]):
        curr_date = datetime.datetime.strptime(ohlcv_arr_new[i][0], "%Y-%m-%d")

        if curr_date >= first_date_processed:
            if first_surpassed_index == -1:
                first_surpassed_index = i

            next_date = datetime.datetime.strptime(ohlcv_arr_new[i + 1][0], "%Y-%m-%d")

            if (next_date - curr_date).days > 1:  # If it is more than 1 day
                # Calculate how many days differ between entries
                days_difference = int((next_date - curr_date).days)

                # Calculate differences
                difference_open = (ohlcv_arr_new[i + 1][1] - ohlcv_arr_new[i][1]) / days_difference
                difference_high = (ohlcv_arr_new[i + 1][2] - ohlcv_arr_new[i][2]) / days_difference
                difference_low = (ohlcv_arr_new[i + 1][3] - ohlcv_arr_new[i][3]) / days_difference
                difference_close = (ohlcv_arr_new[i + 1][4] - ohlcv_arr_new[i][4]) / days_difference
                difference_volume = (ohlcv_arr_new[i + 1][5] - ohlcv_arr_new[i][5]) / days_difference

                # Use the values to fill in the missing data
                for day in range(1, days_difference):
                    ohlcv_arr_new.insert(i + day,
                                         [datetime.datetime.strftime(curr_date + datetime.timedelta(days=day),
                                                                     "%Y-%m-%d"),
                                          ohlcv_arr_new[i][1] + day * difference_open,
                                          ohlcv_arr_new[i][2] + day * difference_high,
                                          ohlcv_arr_new[i][3] + day * difference_low,
                                          ohlcv_arr_new[i][4] + day * difference_close,
                                          int(ohlcv_arr_new[i][5] + day * difference_volume)])

                i += days_difference - 1
        i += 1

    # Leave only relevant values
    ohlcv_arr = np.array(ohlcv_arr_new[first_surpassed_index:-1], dtype=object)

    # Make both sentiment and OHLCV values start on the same day
    if sentiment_arr[0][0] != ohlcv_arr[0][0]:
        if sentiment_arr[0][0] < ohlcv_arr[0][0]:  # If smaller
            while True:
                sentiment_arr = np.delete(sentiment_arr, 0, axis=0)

                if sentiment_arr[0][0] == ohlcv_arr[0][0]:
                    break

        else:
            while True:
                ohlcv_arr = np.delete(ohlcv_arr, 0, axis=0)

                if sentiment_arr[0][0] == ohlcv_arr[0][0]:
                    break

    # Make both sentiment and OHLCV values end on same day
    if sentiment_arr[-1][0] != ohlcv_arr[-1][0]:
        if sentiment_arr[-1][0] < ohlcv_arr[-1][0]:
            while True:
                ohlcv_arr = np.delete(ohlcv_arr, ohlcv_arr.shape[0] - 1, axis=0)
                if sentiment_arr[sentiment_arr.shape[0] - 1][0] == ohlcv_arr[ohlcv_arr.shape[0] - 1][0]:
                    break

        else:
            while True:
                sentiment_arr = np.delete(sentiment_arr, sentiment_arr.shape[0] - 1, axis=0)
                if sentiment_arr[sentiment_arr.shape[0] - 1][0] == ohlcv_arr[ohlcv_arr.shape[0] - 1][0]:
                    break

    # Merge both arrays into a single list
    data_arr = []

    for i in range(ohlcv_arr.shape[0]):  # Should have the same shape
        # The format for `data_arr` is: [DATE, OPEN, HIGH, LOW, CLOSE, SENTIMENT, VOLUME]
        data_arr.append([ohlcv_arr[i][0],
                         ohlcv_arr[i][1],
                         ohlcv_arr[i][2],
                         ohlcv_arr[i][3],
                         ohlcv_arr[i][4],
                         sentiment_arr[i][1],
                         ohlcv_arr[i][5]])

    # Return `data_arr` as a `np.ndarray`
    return np.array(data_arr, dtype=object)


def process_data(data_directory, stock_symbol, entries_taking_avg=10):
    """
    Processes the dataframe generated by `obtain_data`

    Args:
        data_directory (str): The directory which contains the OHLCV data file (a.k.a. stocks
                              file) and the sentiment data file.

        stock_symbol (str): The stock symbol. Also known as the stock ticker.
                            For example, "AAPL", "BA" and "S63.SI" are all valid stock symbols.

        entries_taking_avg (int): The number of entries to consider when taking the average.
                                  (Default = 10)

                                  This parameter is used for the `moving_average` function defined
                                  in `miscUtils.py`. For its use case, consult that file.

    Returns:
        pd.DataFrame: The processed dataframe, which can be used for training/testing.

    """

    # Get the data
    stock_data = obtain_data(data_directory, stock_symbol)

    # Take the moving average of both the OHLCV values and the sentiment values
    averaged_values = []

    for i in range(entries_taking_avg, len(stock_data)):  # Remove `entries_taking_avg` entries from the list
        averaged_values.append([moving_average(stock_data, 1, i, entries_taking_avg),
                                moving_average(stock_data, 2, i, entries_taking_avg),
                                moving_average(stock_data, 3, i, entries_taking_avg),
                                moving_average(stock_data, 4, i, entries_taking_avg),
                                moving_average(stock_data, 5, i, entries_taking_avg),
                                moving_average(stock_data, 6, i, entries_taking_avg)])

    # Convert `averaged_values` to a dictionary
    df_dict = {"Open": [], "High": [], "Low": [], "Close": [], "Sentiment": [], "Volume": []}

    for i in range(len(averaged_values)):
        df_dict["Open"].append(averaged_values[i][0])
        df_dict["High"].append(averaged_values[i][1])
        df_dict["Low"].append(averaged_values[i][2])
        df_dict["Close"].append(averaged_values[i][3])
        df_dict["Sentiment"].append(averaged_values[i][4])
        df_dict["Volume"].append(int(averaged_values[i][5]))

    # Convert the dictionary to a `pd.DataFrame`
    df = pd.DataFrame(df_dict)

    return df


def add_technical_indicators(df):
    """
    Args:
        df (pd.DataFrame): The processed dataframe returned by `process_data`.

    Returns:
        pd.DataFrame: The updated dataframe with the technical indicators inside.

    Acknowledgements:
        - Thanks for Adam King for this compilation of technical indicators!
          The original file and code can be found here:
          https://github.com/notadamking/RLTrader/blob/e5b83b1571f9fcfa6a67a2a810222f1f1751996c/util/indicators.py

    """

    # Add momentum indicators
    df["AO"] = ta.ao(df["High"], df["Low"])
    df["MFI"] = ta.money_flow_index(df["High"], df["Low"], df["Close"], df["Volume"])
    df["RSI"] = ta.rsi(df["Close"])
    df["TSI"] = ta.tsi(df["Close"])
    df["UO"] = ta.uo(df["High"], df["Low"], df["Close"])

    # Add trend indicators
    df["Aroon_up"] = ta.aroon_up(df["Close"])
    df["Aroon_down"] = ta.aroon_down(df["Close"])
    df["Aroon_ind"] = (df["Aroon_up"] - df["Aroon_down"])
    df["CCI"] = ta.cci(df["High"], df["Low"], df["Close"])
    df["DPO"] = ta.dpo(df["Close"])
    df["KST"] = ta.kst(df["Close"])
    df["KST_sig"] = ta.kst_sig(df["Close"])
    df["KST_diff"] = (df["KST"] - df["KST_sig"])
    df["MACD_diff"] = ta.macd_diff(df["Close"])
    df["Mass_index"] = ta.mass_index(df["High"], df["Low"])
    df["Trix"] = ta.trix(df["Close"])
    df["Vortex_pos"] = ta.vortex_indicator_pos(df["High"], df["Low"], df["Close"])
    df["Vortex_neg"] = ta.vortex_indicator_neg(df["High"], df["Low"], df["Close"])
    df["Vortex_diff"] = abs(df["Vortex_pos"] - df["Vortex_neg"])

    # Add volatility indicators
    df["BBH"] = ta.bollinger_hband(df["Close"])
    df["BBL"] = ta.bollinger_lband(df["Close"])
    df["BBM"] = ta.bollinger_mavg(df["Close"])
    df["BBHI"] = ta.bollinger_hband_indicator(df["Close"])
    df["BBLI"] = ta.bollinger_lband_indicator(df["Close"])
    df["KCHI"] = ta.keltner_channel_hband_indicator(df["High"], df["Low"], df["Close"])
    df["KCLI"] = ta.keltner_channel_lband_indicator(df["High"], df["Low"], df["Close"])
    df["DCHI"] = ta.donchian_channel_hband_indicator(df["Close"])
    df["DCLI"] = ta.donchian_channel_lband_indicator(df["Close"])

    # Volume indicators
    df["ADI"] = ta.acc_dist_index(df["High"], df["Low"], df["Close"], df["Volume"])
    df["CMF"] = ta.chaikin_money_flow(df["High"], df["Low"], df["Close"], df["Volume"])
    df["EM"] = ta.ease_of_movement(df["High"], df["Low"], df["Close"], df["Volume"])
    df["FI"] = ta.force_index(df["Close"], df["Volume"])
    df["NVI"] = ta.negative_volume_index(df["Close"], df["Volume"])
    df["OBV"] = ta.on_balance_volume(df["Close"], df["Volume"])
    df["VPT"] = ta.volume_price_trend(df["Close"], df["Volume"])

    # Add miscellaneous indicators
    df["DR"] = ta.daily_return(df["Close"])
    df["DLR"] = ta.daily_log_return(df["Close"])

    # Fill in NaN values
    df.fillna(method="bfill", inplace=True)  # First try `bfill`
    df.fillna(value=0, inplace=True)  # Then replace the rest of the NANs with 0s

    return df


# DEBUG CODE
if __name__ == "__main__":
    print(obtain_data("../trainingData/", "FB"))
    origDF = process_data("../trainingData/", "FB")
    print(origDF)

    modifiedDF = add_technical_indicators(origDF)

    print(modifiedDF)
