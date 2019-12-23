"""
preprocessing.py

Created on 2019-12-23
Updated on 2019-12-23

Copyright Ryan Kan 2019

Description: A program which contains the functions needed to format the data for the observation list.
"""

import datetime

# IMPORTS
import numpy as np


# FUNCTIONS
def preprocess_ohlcv_data(ohlcv_dataframe, lookback_window):
    """
    The function to preprocess the OHLCV data needed for the observation array.

    Args:
        ohlcv_dataframe (pd.DataFrame): The OHLCV dataframe, which contains the OHLCV data.

                                        Note that the dataframe has to be the one returned by the
                                        `get_obs_data()` function in `lib/execution/obtainData.py`.

        lookback_window (int): The lookback window.

    Returns:
        np.ndarray: The preprocessed OHLCV array.

    """
    ohlcv_data = np.array([[-2] * 5] * lookback_window, dtype=float)  # OHLCV values, using -2 as a placeholder
    ohlcv_data_index = 0  # The index for the `ohlcv_data` array
    df_index = 0  # The index of the OHLCV dataframe

    while True:
        # Find out what the current entry of the stock data is
        df_date = ohlcv_dataframe.index[-(df_index + 1)].date()  # This is the current date

        # If the `df_date` is not current date, then find out how many days differ
        if df_date != datetime.date.today() - datetime.timedelta(days=(ohlcv_data_index + 1)):
            days_difference = (datetime.date.today() - datetime.timedelta(days=(ohlcv_data_index + 1)) - df_date).days

            # Fill in data linearly
            generated_values = []

            for i in range(5):  # The 5 columns
                # Find out the difference in values
                diff_val = (ohlcv_dataframe.iloc[-df_index, i] - ohlcv_dataframe.iloc[-(df_index + 1), i]) / (
                        days_difference + 1)

                # Fill in missing data
                temp = []  # Will be used to place the values which have been linearly fit
                for j in range(days_difference):
                    # Fill in this column's data linearly
                    generated_value = ohlcv_dataframe.iloc[-df_index, i] - diff_val * (j + 1)

                    # Make sure that the Volume is an integer
                    if i == 4:  # Volume column
                        generated_value = int(generated_value)

                    # Append this generated value to `temp`
                    temp.append(generated_value)

                # Append the `temp` list to the `generated_values` list
                generated_values.append(temp)

            # Only keep the relevant values
            if ohlcv_data_index + len(generated_values[0]) > lookback_window:  # Too many entries
                # First change `generated_values` into a `np.ndarray`
                generated_values = np.array(generated_values)

                # Then restrict the `generated_values` array
                generated_values = generated_values[:, :lookback_window - ohlcv_data_index]

                # Lastly, convert the array back into a list
                generated_values = list(generated_values.tolist())

            # Fill in the values
            for i in range(5):  # 5 columns of data, so iterate 5 times
                for j in range(len(generated_values[0])):  # This is how many entries to fill in
                    ohlcv_data[j + ohlcv_data_index][i] = generated_values[i][j]

        else:
            # Fill in entry with the current day's OHLCV data
            ohlcv_data[ohlcv_data_index] = list(ohlcv_dataframe.iloc[-(df_index + 1)])  # We want OHLCV values only
            df_index += 1

        # Check if there are any entries left unfilled
        if [-2, -2, -2, -2, -2] not in ohlcv_data.tolist():
            break

        else:
            # Since there are still entries to fill, find the next instance
            converted_list = ohlcv_data.tolist()

            assert isinstance(converted_list, list), "This error will never appear, this is just to pacify the IDEs!"

            ohlcv_data_index = converted_list.index([-2, -2, -2, -2, -2])  # This finds the next unfilled entry

    return ohlcv_data


def preprocess_sentiment_data(sentiment_dataframe, lookback_window):
    """
    The function that preprocesses the sentiment data needed for the observation array.

    Args:
       sentiment_dataframe (pd.DataFrame): The sentiment dataframe, which contains the OHLCV data.

                                           Note that the dataframe has to be the one returned
                                           by the `get_obs_data()` function in `lib/execution/
                                           obtainData.py`.

       lookback_window (int): The lookback window.

    Returns:
       np.ndarray: The preprocessed sentiment array.

    """

    sentiment_data = [-2] * lookback_window  # -2 cannot appear in the list, therefore use it as a placeholder

    sentiment_data_index = 0  # The index for the `sentiment_data` array
    df_index = 0  # The index of the sentiment dataframe

    while True:
        # Find out what the current entry of the sentiment data is
        df_date = sentiment_dataframe["Date"][df_index]

        # If not current date, then find out how many days differ
        if df_date != (datetime.datetime.today() - datetime.timedelta(days=sentiment_data_index)).strftime("%Y-%m-%d"):
            days_difference = (datetime.datetime.today() - datetime.timedelta(days=sentiment_data_index) - df_date).days

            # Fill in next `(days_difference + 1)` days with the current entry's sentiment
            for i in range(sentiment_data_index, min(sentiment_data_index + days_difference + 1, lookback_window)):
                sentiment_data[i] = sentiment_dataframe["Sentiment"][df_index]

        else:  # If not, fill in the sentiment of the current day
            sentiment_data[sentiment_data_index] = sentiment_dataframe["Sentiment"][df_index]

        # If there are still entries to fill, move on
        if -2 in sentiment_data:
            sentiment_data_index = sentiment_data.index(-2)  # This finds the next unfilled entry
            df_index += 1

        else:
            break

    return np.array(sentiment_data)


def preprocess_owned_stock_data(owned_stock_arr, lookback_window, stock_symbol):
    """
    The function which preprocesses the owned stock data into the form needed for the observation
    array.

    Args:
        owned_stock_arr (np.ndarray): The owned stock array.

                                      Note that this has to be the same array which was returned
                                      by the `get_obs_data()` function in `lib/execution/obtain
                                      Data.py`.

        lookback_window (int): The lookback window.

        stock_symbol (str): The stock symbol. It is also known as the stock ticker.
                            For example, "AAPL", "TSLA", "BA", "DIS".

    Returns:
        np.ndarray: The preprocessed "owned stock" array.

    """
    # Obtain the stock history for the current stock
    relevant_hist = []
    for entry in owned_stock_arr[::-1]:
        if entry[2] == stock_symbol:
            relevant_hist.append(entry)

    # Check if there is enough data in `relevant_hist`
    owned_data = [0] * lookback_window

    owned_hist_index = 0  # The index for the `owned_data` array
    data_index = 0  # The index for the `np.ndarray`

    # Fill in missing `owned_data` entries
    try:
        while True:
            data_date = relevant_hist[data_index][0]  # This is the recorded date in the `np.ndarray`

            # If not current date, then find out how many days differ
            if datetime.datetime.strptime(data_date, "%Y-%m-%d") != datetime.datetime.today() - datetime.timedelta(
                    days=owned_hist_index):
                days_difference = (datetime.datetime.today() - datetime.timedelta(
                    days=owned_hist_index) - datetime.datetime.strptime(data_date, "%Y-%m-%d")).days

                # Fill in next `(days_difference + 1)` days with the current entry's data
                for i in range(owned_hist_index, min(owned_hist_index + days_difference + 1, lookback_window)):
                    owned_data[i] = relevant_hist[data_index][1]

            else:
                # Fill in current day's "owned stocks" data
                owned_data[owned_hist_index] = relevant_hist[data_index][1]

            # If there are empty entries, continue filling in data
            if 0 in owned_data:
                owned_hist_index = owned_data.index(0)  # This finds the next unfilled entry
                data_index += 1

            else:
                break

    except IndexError:
        # This means that, before today, nothing was recorded.
        # So leave the list as 0's
        pass

    return np.array(owned_data)
