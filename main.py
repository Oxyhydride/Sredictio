"""
main.py
Version 1.0.0

Created on 2019-12-04
Updated on 2019-12-04

Copyright Ryan Kan 2019

Description: The main file. Used to predict actions to take.
"""

# IMPORTS
import argparse
import datetime

import numpy as np
import pandas as pd
import tensorflow as tf
from stable_baselines import A2C
from statsmodels.tsa.statespace.sarimax import SARIMAX
from yahoo_fin import stock_info as si

from utils.miscUtils import normalise
from utils.sentimentUtils import get_sentiment

# SETUP
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

# ARGUMENTS
parser = argparse.ArgumentParser(description="A program which helps generate actions for the current day.")

parser.add_argument("stock_name", type=str, help="The stock's name. E.G. Amazon, Apple, Alphabet Inc, Tesla")
parser.add_argument("stock_symbol", type=str, help="The stock's symbol. E.G. AMZN, AAPL, GOOGL, TSLA")
parser.add_argument("stock_history_file", type=str, help="The stock history file, usually saved as a .csv.")
parser.add_argument("model_file", type=str, help="The model file")
parser.add_argument("look_back_window", type=int, help="The look back window size. Can be found in the model name, "
                                                       "next to `LBW`. E.G. `LBW-7` means look_back_window = 7. Note "
                                                       "that days_to_scrape_data has to be larger than twice the "
                                                       "look_back_window")

parser.add_argument("-d", "--days_to_scrape_data", type=int, default=60,
                    help="The number of days to scrape the stock and sentiment data. Note that days_to_scrape_data "
                         "has to be larger than twice the look_back_window")
parser.add_argument("-v", "--verbose", choices=["0", "1"],
                    help="Set the verbosity of the program", default="1")

args = parser.parse_args()

STOCK_NAME = args.stock_name
STOCK_SYMBOL = args.stock_symbol
STOCK_HISTORY_FILE = args.stock_history_file

DAYS_TO_SCRAPE = int(args.days_to_scrape_data)

MODEL_FILE = args.model_file
LOOK_BACK_WINDOW = args.look_back_window

VERBOSE = int(args.verbose)

# CHECKS
assert 2 * LOOK_BACK_WINDOW < DAYS_TO_SCRAPE, "Days to scrape data has to be larger than twice the look back window."

# OBTAINING DATA
# Get stock data
if VERBOSE == 1:
    print(f"Obtaining {STOCK_NAME.lower()} stock data...")

stockDataFrame = si.get_data(STOCK_SYMBOL,
                             start_date=(datetime.datetime.today() - datetime.timedelta(days=DAYS_TO_SCRAPE)).strftime(
                                 "%m-%d-%Y"),
                             end_date=datetime.datetime.today().strftime("%m-%d-%Y"))  # Gets the historical data

# Get sentiment data
if VERBOSE == 1:
    print(f"Obtaining {STOCK_NAME.lower()} sentiment data...")

sentimentDataFrame = get_sentiment(STOCK_SYMBOL, STOCK_NAME,
                                   (datetime.date.today() - datetime.timedelta(days=DAYS_TO_SCRAPE)).strftime(
                                       "%Y-%m-%d"), verbose=False, to_csv=False)

# Get owned stock history
if VERBOSE == 1:
    print(f"Obtaining owned stock history...")

stockHist = pd.read_csv(STOCK_HISTORY_FILE).to_numpy()

if VERBOSE == 1:
    print("Done!")

# PREPROCESSING
# 1. Stock (OHLC) data
stockData = np.array([[-2] * 4] * LOOK_BACK_WINDOW, dtype=np.float64)  # OHLC values, using -2 as a placeholder
stockDataIndex = 0  # The index for the stockData array
dataframeIndex = 0  # The index for the dataframe

while True:
    # Find out what the current entry of the stock data is
    dataframeDate = stockDataFrame.index[-(dataframeIndex + 1)]  # This is the current date
    # If not current date, then find out how many days before it is
    if dataframeDate != datetime.date.today() - datetime.timedelta(days=stockDataIndex):
        daysDifference = (datetime.date.today() - datetime.timedelta(days=stockDataIndex) - dataframeDate).days

        # Get SARIMAX values
        sarimaxValues = [[-2] * daysDifference] * 4

        for i in range(4):  # First 4 columns
            currDataSeries = stockDataFrame.iloc[:, i]
            forecastModel = SARIMAX(np.array(currDataSeries), enforce_stationarity=False)  # Only want OHLC values
            modelFit = forecastModel.fit(method='bfgs', disp=False)
            forecast = modelFit.forecast(steps=daysDifference)  # Definitely an np.array

            assert isinstance(forecast, np.ndarray), "This error will never appear, this is just to pacify the IDEs!"

            sarimaxValues[i] = list(forecast)

        # Fill in SARIMAX values
        for i in range(stockDataIndex, stockDataIndex + daysDifference):
            for j in range(4):  # 4 Columns
                stockData[i][j] = sarimaxValues[j][i - stockDataIndex]

        stockDataIndex += daysDifference

    else:
        # Fill in entry with current day's OHLC data
        stockData[stockDataIndex] = list(stockDataFrame.iloc[-(dataframeIndex + 1)])[:4]  # OHLC values only
        dataframeIndex += 1  # Simply increment this by 1

    # Check if there are any entries left
    if [-2, -2, -2, -2] not in list(stockData.tolist()):
        break
    else:
        stockDataIndex = list(stockData.tolist()).index([-2, -2, -2, -2])

# 2. Sentiment data
sentimentData = [-2] * LOOK_BACK_WINDOW  # -2 cannot appear, therefore use it

sentimentDataIndex = 0  # The index for the sentimentData array
dataframeIndex = 0  # The index for the dataframe

while True:
    # Find out what the current entry of the sentiment data is
    dataframeDate = sentimentDataFrame["Date"][dataframeIndex]  # This is the date obtained from the dataframe

    # If not current date, then find out how many days before it is
    if dataframeDate != (datetime.datetime.today() - datetime.timedelta(days=sentimentDataIndex)).strftime("%Y-%m-%d"):
        daysDifference = (datetime.datetime.today() - datetime.timedelta(
            days=sentimentDataIndex) - datetime.datetime.strptime(dataframeDate, "%Y-%m-%d")).days

        # Fill in next (daysDifference + 1) days with the current entry's sentiment data
        for i in range(sentimentDataIndex, min(sentimentDataIndex + daysDifference + 1, LOOK_BACK_WINDOW)):
            sentimentData[i] = sentimentDataFrame["Sentiment"][dataframeIndex]

    else:  # If not, fill in current day's sentiment
        sentimentData[sentimentDataIndex] = sentimentDataFrame["Sentiment"][dataframeIndex]

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
for entry in stockHist[::-1]:
    if entry[2] == STOCK_SYMBOL:
        relevantHist.append(entry)

# Check if relevantHist is sufficient
ownedData = [0] * LOOK_BACK_WINDOW

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
            for i in range(ownedHistIndex, min(ownedHistIndex + daysDifference + 1, LOOK_BACK_WINDOW)):
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

# Find min and max from stocks
minVal = float("inf")
maxVal = -float("inf")

for entry in stockData:
    minVal = min(minVal, min(entry[0], min(entry[1], min(entry[2], entry[3]))))
    maxVal = max(maxVal, max(entry[0], max(entry[1], max(entry[2], entry[3]))))

# Normalise the stock data
for i in range(LOOK_BACK_WINDOW):
    for j in range(4):
        stockData[i][j] = normalise(stockData[i][j], minVal, maxVal, min_normalised_value=1, max_normalised_value=10)

# Put all three data together
"""
DISCLAIMER:
I'm not sure how to implement Net Worth history and Cash-In-Hand history yet, so they'll all be 0's.
"""
observation = np.array([ownedData, stockData[:, 0], stockData[:, 1], stockData[:, 2], stockData[:, 3], sentimentData,
                        np.array([0] * LOOK_BACK_WINDOW), np.array([0] * LOOK_BACK_WINDOW)])

if VERBOSE:
    print("Generated observation array.")

# MODEL PREDICTION
# Load A2C model
model = A2C.load(MODEL_FILE)

# Return an action for the current state
action, _ = model.predict([observation])
suggestedAction = action[0]

# Output action & amount
print()
if suggestedAction[0] == 0:  # Sell
    print(f"Sell {suggestedAction[1]}/10 of owned stocks (if possible).")

elif suggestedAction[0] == 1:  # Hold
    print("Hold the stocks.")

else:  # Buy
    print(f"Buy stocks using {suggestedAction[1]}/10 of total balance (if possible).")
