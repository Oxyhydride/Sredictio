"""
Main.py

Created on 2019-12-04
Updated on 2019-12-17

Copyright Ryan Kan 2019

Description: The main file. Used to predict actions to take.
"""

# IMPORTS
import argparse
import datetime

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn import preprocessing
from stable_baselines import A2C
from statsmodels.tsa.statespace.sarimax import SARIMAX

from lib.deployment.obtainData import get_model_file, get_lookback_window, get_obs_data
from lib.utils.dataUtils import add_technical_indicators

# SETUP
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)  # Remove ugly tensorflow warnings

# ARGUMENTS
parser = argparse.ArgumentParser(description="A program which helps generate actions for the current day.")

parser.add_argument("stock_history_file", type=str, help="The stock history file, usually saved as a .csv.")
parser.add_argument("model_dir", type=str, help="The model directory, which contains all the model files.")
parser.add_argument("stock_name", type=str, help="The stock's name. E.G. Amazon, Apple, Google/Alphabet, Tesla")
parser.add_argument("stock_symbol", type=str,
                    help="The stock's symbol. Also known as the ticker. E.G. AMZN, AAPL, GOOGL, TSLA")

parser.add_argument("-d", "--days_to_scrape_data", type=int, default=100,
                    help="The number of days to scrape the stock and sentiment data. Note that days_to_scrape_data "
                         "has to be larger than 2.5 times the look_back_window. If a model file is "
                         "\"Model_LBW-7_NOI-1000\", then the look_back_window is 7 (as LBW = 7).")
parser.add_argument("-p", "--no_predictions", type=int,
                    help="Number of predictions to run when choosing the action to take", default=1000)
parser.add_argument("-r", "--retry_count", type=int,
                    help="Number of attempts to get data from Yahoo Finance if it fails", default=3)

args = parser.parse_args()

STOCK_NAME = args.stock_name
STOCK_SYMBOL = args.stock_symbol
STOCK_HISTORY_FILE = args.stock_history_file

DAYS_TO_SCRAPE = int(args.days_to_scrape_data)

MODEL_DIRECTORY = args.model_dir if args.model_dir[-1] == "/" else args.model_dir + "/"
NO_PREDICTIONS = int(args.no_predictions)

RETRY_COUNT = args.retry_count

# OBTAINING DATA
# Get the model file from the model directory
modelFile = get_model_file(MODEL_DIRECTORY)

# Get the value for the lookback window from the model file
lookbackWindow = get_lookback_window(modelFile)

# Get the data for the observation array
stockDataframe, sentimentDataframe, ownedStockArr = get_obs_data(STOCK_NAME, STOCK_SYMBOL, STOCK_HISTORY_FILE,
                                                                 lookbackWindow, days_to_scrape=DAYS_TO_SCRAPE,
                                                                 retry_count=RETRY_COUNT)

# PREPROCESSING
# 1. OHLCV data
ohlcvData = np.array([[-2] * 5] * lookbackWindow, dtype=np.float64)  # OHLCV values, using -2 as a placeholder
ohlcvDataIndex = 0  # The index for the `ohlcvData` array
dataframeIndex = 0

while True:
    # Find out what the current entry of the stock data is
    dataframeDate = stockDataframe.index[-(dataframeIndex + 1)].date()  # This is the current date

    # If the `dataframeDate` is not current date, then find out how many days differ
    if dataframeDate != datetime.date.today() - datetime.timedelta(days=ohlcvDataIndex):
        daysDifference = (datetime.date.today() - datetime.timedelta(days=ohlcvDataIndex) - dataframeDate).days

        # TODO(Ryan-Kan): REPLACE CODE BELOW WITH LINEAR FIT DATA
        # Get SARIMAX values
        sarimaxValues = [[-2] * daysDifference] * 5

        for i in range(5):  # First 5 columns
            currDataSeries = stockDataframe.iloc[:, i]
            forecastModel = SARIMAX(np.array(currDataSeries), enforce_stationarity=False)  # Only want OHLC values
            modelFit = forecastModel.fit(method='bfgs', disp=False)
            forecast = modelFit.forecast(steps=daysDifference)  # Definitely an `np.ndarray`

            assert isinstance(forecast, np.ndarray), "This error will never appear, this is just to pacify the IDEs!"

            sarimaxValues[i] = list(forecast)

        # Fill in SARIMAX values
        for i in range(ohlcvDataIndex, min(ohlcvDataIndex + daysDifference, lookbackWindow)):
            for j in range(5):  # 5 columns of data, so iterate 5 times
                ohlcvData[i][j] = sarimaxValues[j][i - ohlcvDataIndex]

        ohlcvDataIndex += daysDifference

    else:
        # Fill in entry with the current day's OHLCV data
        ohlcvData[ohlcvDataIndex] = list(stockDataframe.iloc[-(dataframeIndex + 1)])[:5]  # We want OHLCV values only
        dataframeIndex += 1

    # Check if there are any entries left unfilled
    if [-2, -2, -2, -2, -2] not in ohlcvData.tolist():
        break

    else:
        # Since there are still entries to fill, find the next instance
        convertedList = ohlcvData.tolist()

        assert isinstance(convertedList, list), "This error will never appear, this is just to pacify the IDEs!"

        ohlcvDataIndex = convertedList.index([-2, -2, -2, -2, -2])  # This finds the next unfilled entry

# 2. Sentiment data
sentimentData = [-2] * lookbackWindow  # -2 cannot appear in the list, therefore use it as a placeholder

sentimentDataIndex = 0  # The index for the `sentimentData` array
dataframeIndex = 0

while True:
    # Find out what the current entry of the sentiment data is
    dataframeDate = sentimentDataframe["Date"][dataframeIndex]

    # If not current date, then find out how many days differ
    if dataframeDate != (datetime.datetime.today() - datetime.timedelta(days=sentimentDataIndex)).strftime("%Y-%m-%d"):
        daysDifference = (datetime.datetime.today() - datetime.timedelta(days=sentimentDataIndex) - dataframeDate).days

        # Fill in next (daysDifference + 1) days with the current entry's sentiment
        for i in range(sentimentDataIndex, min(sentimentDataIndex + daysDifference + 1, lookbackWindow)):
            sentimentData[i] = sentimentDataframe["Sentiment"][dataframeIndex]

    else:  # If not, fill in the sentiment of the current day
        sentimentData[sentimentDataIndex] = sentimentDataframe["Sentiment"][dataframeIndex]

    # If there are still entries to fill, move on
    if -2 in sentimentData:
        sentimentDataIndex = sentimentData.index(-2)  # This finds the next unfilled entry
        dataframeIndex += 1

    else:
        break

# 3. Stock History data
# Obtain the stock history for the current stock
relevantHist = []
for entry in ownedStockArr[::-1]:
    if entry[2] == STOCK_SYMBOL:
        relevantHist.append(entry)

# Check if there is enough data in `relevantHist`
ownedData = [0] * lookbackWindow

ownedHistIndex = 0  # The index for the `ownedData` array
dataIndex = 0  # The index for the `np.ndarray`

# Fill in missing `ownedData` entries
try:
    while True:
        dataDate = relevantHist[dataIndex][0]  # This is the recorded date in the `np.ndarray`

        # If not current date, then find out how many days differ
        if datetime.datetime.strptime(dataDate, "%Y-%m-%d") != datetime.datetime.today() - datetime.timedelta(
                days=ownedHistIndex):
            daysDifference = (datetime.datetime.today() - datetime.timedelta(
                days=ownedHistIndex) - datetime.datetime.strptime(dataDate, "%Y-%m-%d")).days

            # Fill in next `(daysDifference + 1)` days with the current entry's data
            for i in range(ownedHistIndex, min(ownedHistIndex + daysDifference + 1, lookbackWindow)):
                ownedData[i] = relevantHist[dataIndex][1]

        else:
            # Fill in current day's "owned stocks" data
            ownedData[ownedHistIndex] = relevantHist[dataIndex][1]

        # If there are empty entries, continue filling in data
        if 0 in ownedData:
            ownedHistIndex = ownedData.index(0)  # This finds the next unfilled entry
            dataIndex += 1

        else:
            break

except IndexError:
    # This means that, before today, nothing was recorded.
    # So leave the list as 0's
    pass

# Reverse all arrays, and cast lists to `np.ndarray`
ohlcvData = ohlcvData[::-1]
sentimentData = np.array(sentimentData[::-1])
ownedData = np.array(ownedData[::-1])

# Make a dataframe with the `stockData` and `sentimentData` arrays
dataframe = pd.DataFrame({"Open": ohlcvData[:, 0], "High": ohlcvData[:, 1], "Low": ohlcvData[:, 2],
                          "Close": ohlcvData[:, 3], "Volume": ohlcvData[:, 4], "Sentiment": sentimentData})

# Add technical indicators to the dataframe
dataframe = add_technical_indicators(dataframe)

# Add the owned stocks history to the dataframe
dataframe["Owned Stocks"] = ownedData

# Convert the dataframe to a `np.ndarray`
observation = dataframe.transpose().values

# Normalise the observation array
minMaxScaler = preprocessing.MinMaxScaler()
observationScaled = minMaxScaler.fit_transform(observation.astype("float32"))

print("Generated the observation array.")

# MODEL PREDICTION
# Load the A2C model
model = A2C.load(MODEL_DIRECTORY + modelFile)

# Generate possible actions
suggestedActionsCount = {"Sell": 0, "Hold": 0, "Buy": 0}  # Tally the number of times the model suggests each action
suggestedAmounts = {"Sell": [], "Hold": [], "Buy": []}  # Tally the amount for each action type

# Run the prediction algorithm `NO_PREDICTIONS` times to see which action appears the most
for _ in range(NO_PREDICTIONS):
    action, _ = model.predict([observationScaled])
    suggestedAction = action[0]

    if suggestedAction[0] == 0:  # Sell
        suggestedActionsCount["Sell"] += 1
        suggestedAmounts["Sell"].append(suggestedAction[1] + 1)  # The amount ranges from 0 to 4, so increment by 1

    elif suggestedAction[0] == 1:  # Hold
        suggestedActionsCount["Hold"] += 1
        suggestedAmounts["Hold"].append(suggestedAction[1] + 1)

    else:  # Buy
        suggestedActionsCount["Buy"] += 1
        suggestedAmounts["Buy"].append(suggestedAction[1] + 1)

# Find mode of the `suggestedActionsCount` set
highestCount = max(list(suggestedActionsCount.values()))
bestAction = list(suggestedActionsCount.keys())[list(suggestedActionsCount.values()).index(highestCount)]

# Get mode of the `suggestedAmounts` for that action
possibleAmounts = sorted(suggestedAmounts[bestAction])
bestAmount = max(set(possibleAmounts), key=possibleAmounts.count)

# Output the action & amount
print(f"\nThe current stock price is at ${observation[3][-1]:.2f}")
if bestAction == "Hold":
    print("HOLD the stocks.")

elif bestAction == "Sell":
    print(f"If possible, SELL {bestAmount}/5 of owned stocks.")

else:  # Buy
    print(f"If possible, BUY stocks using {bestAmount}/5 of total balance (if possible).")
