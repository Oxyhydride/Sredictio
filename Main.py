"""
Main.py

Created on 2019-12-04
Updated on 2019-12-14

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
from lib.utils.trainingDataUtils import add_technical_indicators

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

# Get the lookback window from the model file
lookbackWindow = get_lookback_window(modelFile)

# Get the data for the observation array
stockDataframe, sentimentDataframe, ownedStockArr = get_obs_data(STOCK_NAME, STOCK_SYMBOL, STOCK_HISTORY_FILE,
                                                                 lookbackWindow, days_to_scrape=DAYS_TO_SCRAPE,
                                                                 retry_count=RETRY_COUNT)

# PREPROCESSING
# 1. Stock (OHLCV) data
stockData = np.array([[-2] * 5] * lookbackWindow, dtype=np.float64)  # OHLC values, using -2 as a placeholder
stockDataIndex = 0  # The index for the stockData array
dataframeIndex = 0  # The index for the dataframe

while True:
    # Find out what the current entry of the stock data is
    dataframeDate = stockDataframe.index[-(dataframeIndex + 1)].date()  # This is the current date

    # If not current date, then find out how many days before it is
    if dataframeDate != datetime.date.today() - datetime.timedelta(days=stockDataIndex):
        daysDifference = (datetime.date.today() - datetime.timedelta(days=stockDataIndex) - dataframeDate).days

        # TODO: REPLACE CODE BELOW WITH LINEAR FIT DATA
        # Get SARIMAX values
        sarimaxValues = [[-2] * daysDifference] * 5

        for i in range(5):  # First 5 columns
            currDataSeries = stockDataframe.iloc[:, i]
            forecastModel = SARIMAX(np.array(currDataSeries), enforce_stationarity=False)  # Only want OHLC values
            modelFit = forecastModel.fit(method='bfgs', disp=False)
            forecast = modelFit.forecast(steps=daysDifference)  # Definitely an np.array

            assert isinstance(forecast, np.ndarray), "This error will never appear, this is just to pacify the IDEs!"

            sarimaxValues[i] = list(forecast)

        # Fill in SARIMAX values
        for i in range(stockDataIndex, min(stockDataIndex + daysDifference, lookbackWindow)):
            for j in range(5):  # 5 Columns
                stockData[i][j] = sarimaxValues[j][i - stockDataIndex]

        stockDataIndex += daysDifference

    else:
        # Fill in entry with current day's OHLC data
        stockData[stockDataIndex] = list(stockDataframe.iloc[-(dataframeIndex + 1)])[:5]  # OHLC values only
        dataframeIndex += 1  # Simply increment this by 1

    # Check if there are any entries left
    if [-2, -2, -2, -2, -2] not in stockData.tolist():
        break
    else:
        convertedList = stockData.tolist()

        assert isinstance(convertedList, list), type(convertedList)  # Check if list

        stockDataIndex = convertedList.index([-2, -2, -2, -2, -2])

# 2. Sentiment data
sentimentData = [-2] * lookbackWindow  # -2 cannot appear, therefore use it

sentimentDataIndex = 0  # The index for the sentimentData array
dataframeIndex = 0  # The index for the dataframe

while True:
    # Find out what the current entry of the sentiment data is
    dataframeDate = sentimentDataframe["Date"][dataframeIndex]  # This is the date obtained from the dataframe

    # If not current date, then find out how many days before it is
    if dataframeDate != (datetime.datetime.today() - datetime.timedelta(days=sentimentDataIndex)).strftime("%Y-%m-%d"):
        daysDifference = (datetime.datetime.today() - datetime.timedelta(
            days=sentimentDataIndex) - dataframeDate).days

        # Fill in next (daysDifference + 1) days with the current entry's sentiment data
        for i in range(sentimentDataIndex, min(sentimentDataIndex + daysDifference + 1, lookbackWindow)):
            sentimentData[i] = sentimentDataframe["Sentiment"][dataframeIndex]

    else:  # If not, fill in current day's sentiment
        sentimentData[sentimentDataIndex] = sentimentDataframe["Sentiment"][dataframeIndex]

    # If there are still entries to fill, continue
    if -2 in sentimentData:
        sentimentDataIndex = sentimentData.index(-2)  # Next index to work on
        dataframeIndex += 1  # Increment this by 1

    else:
        break

# 3. Stock History data
"""
NOTE:
- Assume the stock history is arranged in CHRONOLOGICAL order, from EARLIEST to LATEST.
- Assume dates are written in YYYY-MM-DD format.
"""
# Obtain data which is relevant
relevantHist = []
for entry in ownedStockArr[::-1]:
    if entry[2] == STOCK_SYMBOL:
        relevantHist.append(entry)

# Check if relevantHist is sufficient
ownedData = [0] * lookbackWindow

ownedHistIndex = 0  # The index for the ownedData array
dataIndex = 0  # The index for the np.array

# Fill in missing stock_owned data
try:
    while True:
        dataDate = relevantHist[dataIndex][0]  # This is the recorded date

        if datetime.datetime.strptime(dataDate, "%Y-%m-%d") != datetime.datetime.today() - datetime.timedelta(
                days=ownedHistIndex):
            # If not current date, then find out how many days before it is
            daysDifference = (datetime.datetime.today() - datetime.timedelta(
                days=ownedHistIndex) - datetime.datetime.strptime(dataDate, "%Y-%m-%d")).days

            # Fill in next (daysDifference + 1) days with the current entry's data
            for i in range(ownedHistIndex, min(ownedHistIndex + daysDifference + 1, lookbackWindow)):
                ownedData[i] = relevantHist[dataIndex][1]

        else:
            # Fill in current day's data
            ownedData[ownedHistIndex] = relevantHist[dataIndex][1]

        # If there are empty entries, continue
        if 0 in ownedData:
            ownedHistIndex = ownedData.index(0)  # Next index to work on is this
            dataIndex += 1  # Increment this by 1

        else:
            break

except IndexError:  # Before this, nothing was recorded
    # So leave it as 0's
    pass

# Reverse all arrays & cast some to np.ndarray
stockData = stockData[::-1]
sentimentData = np.array(sentimentData[::-1])
ownedData = np.array(ownedData[::-1])

# Convert to dataframe
dataframe = pd.DataFrame({"Open": stockData[:, 0], "High": stockData[:, 1], "Low": stockData[:, 2],
                          "Close": stockData[:, 3], "Volume": stockData[:, 4], "Sentiment": sentimentData})

# Add technical indicators
dataframe = add_technical_indicators(dataframe)

# Add owned stocks to dataframe
dataframe["Owned Stocks"] = ownedData

# Convert to np.ndarray
observation = dataframe.transpose().values

# Scale the observation array
minMaxScaler = preprocessing.MinMaxScaler()
observationScaled = minMaxScaler.fit_transform(observation.astype("float32"))

print("Generated the observation array.")

# MODEL PREDICTION
# Load A2C model
model = A2C.load(MODEL_DIRECTORY + modelFile)

# Generate possible actions
suggestedActionsCount = {"Sell": 0, "Hold": 0, "Buy": 0}  # Tally the number of times the model suggests each action
suggestedAmounts = {"Sell": [], "Hold": [], "Buy": []}  # Tally the amount for each action type

for _ in range(NO_PREDICTIONS):
    action, _ = model.predict([observationScaled])
    suggestedAction = action[0]

    if suggestedAction[0] == 0:  # Sell
        suggestedActionsCount["Sell"] += 1
        suggestedAmounts["Sell"].append(suggestedAction[1] + 1)

    elif suggestedAction[0] == 1:  # Hold
        suggestedActionsCount["Hold"] += 1
        suggestedAmounts["Hold"].append(suggestedAction[1] + 1)

    else:  # Buy
        suggestedActionsCount["Buy"] += 1
        suggestedAmounts["Buy"].append(suggestedAction[1] + 1)

# Find most probable action
highestCount = max(list(suggestedActionsCount.values()))
bestAction = list(suggestedActionsCount.keys())[list(suggestedActionsCount.values()).index(highestCount)]

# Get amount
possibleAmounts = sorted(suggestedAmounts[bestAction])
bestAmount = max(set(possibleAmounts), key=possibleAmounts.count)

# Output action & amount
print(f"\nThe current stock price is at ${observation[3][-1]:.2f}")
if bestAction == "Hold":
    print("Hold the stocks.")

elif bestAction == "Sell":
    print(f"Sell {bestAmount}/5 of owned stocks (if possible).")

else:  # Buy
    print(f"Buy stocks using {bestAmount}/5 of total balance (if possible).")
