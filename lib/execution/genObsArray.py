"""
genObsArray.py

Created on 2019-12-23
Updated on 2019-12-23

Copyright Ryan Kan 2019

Description: The file which contains the function needed to generate the observation array.
"""
# IMPORTS
import pandas as pd
from sklearn import preprocessing

from lib.utils.dataUtils import add_technical_indicators


# FUNCTIONS
def gen_obs_array(ohlcv_data, sentiment_data, owned_stock_data):
    # Make a dataframe with the `ohlcv_data` and `sentiment_data` arrays
    dataframe = pd.DataFrame({"Open": ohlcv_data[:, 0], "High": ohlcv_data[:, 1], "Low": ohlcv_data[:, 2],
                              "Close": ohlcv_data[:, 3], "Volume": ohlcv_data[:, 4], "Sentiment": sentiment_data})

    # Add technical indicators to the dataframe
    dataframe = add_technical_indicators(dataframe)

    # Add the owned stocks history to the dataframe
    dataframe["Owned Stocks"] = owned_stock_data

    # Convert the dataframe to a `np.ndarray`
    observation = dataframe.transpose().values

    # Normalise the observation array
    min_max_scaler = preprocessing.MinMaxScaler()
    observation_scaled = min_max_scaler.fit_transform(observation.astype("float32"))

    return observation_scaled
