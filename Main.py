"""
Main.py

Created on 2019-12-04
Updated on 2019-12-25

Copyright Ryan Kan 2019

Description: The main file. Used to predict which actions to take on the current day.
"""

# IMPORTS
import argparse

import tensorflow as tf
from stable_baselines import A2C

from lib.execution.genAction import gen_action
from lib.execution.genObsArray import gen_obs_array
from lib.execution.obtainData import get_model_file, get_lookback_window, get_obs_data
from lib.execution.processData import preprocess_ohlcv_data, preprocess_sentiment_data

# SETUP
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)  # Remove the ugly tensorflow warnings

# ARGUMENTS
parser = argparse.ArgumentParser(description="A program which helps generate actions for the current day.")

parser.add_argument("model_dir", type=str, help="The model directory, which contains all the model files.")
parser.add_argument("stock_name", type=str, help="The stock's name. E.G. Amazon, Apple, Google/Alphabet, Tesla")
parser.add_argument("stock_symbol", type=str,
                    help="The stock's symbol. Also known as the ticker. E.G. AMZN, AAPL, GOOGL, TSLA")

parser.add_argument("-d", "--days_to_scrape_data", type=int, default=100,
                    help="The number of days to scrape the stock and sentiment data. Note that days_to_scrape_data "
                         "has to be larger than 2.5 times the look_back_window. If a model file is "
                         "\"Model_LBW-7_NOI-1000\", then the look_back_window is 7 (as LBW = 7).")
parser.add_argument("-p", "--no_predictions", type=int,
                    help="Number of predictions to run when choosing the action to take.", default=1000)
parser.add_argument("-r", "--retry_count", type=int,
                    help="Number of attempts to get the data from Yahoo Finance.", default=3)

args = parser.parse_args()

STOCK_NAME = args.stock_name
STOCK_SYMBOL = args.stock_symbol

DAYS_TO_SCRAPE = int(args.days_to_scrape_data)

MODEL_DIRECTORY = args.model_dir if args.model_dir[-1] == "/" else args.model_dir + "/"
NO_PREDICTIONS = int(args.no_predictions)

RETRY_COUNT = args.retry_count

# OBTAINING DATA
# Get the model file from the model directory
modelFile = get_model_file(MODEL_DIRECTORY)

# Get the value for the lookback window from the model file
lookbackWindow = get_lookback_window(modelFile)

# Obtain the data needed for preprocessing
ohlcvDataframe, sentimentDataframe = get_obs_data(STOCK_NAME, STOCK_SYMBOL, lookbackWindow,
                                                  days_to_scrape=DAYS_TO_SCRAPE, retry_count=RETRY_COUNT)

# PREPROCESSING
# Preprocess OHLCV data and sentiment data
ohlcvData = preprocess_ohlcv_data(ohlcvDataframe, lookbackWindow)
sentimentData = preprocess_sentiment_data(sentimentDataframe, lookbackWindow)

# Convert preprocessed data into the observation arrays
observation = gen_obs_array(ohlcvData, sentimentData)

print("Generated the observation array.")

# MODEL PREDICTION
# Load the A2C model
model = A2C.load(MODEL_DIRECTORY + modelFile)

# Get best action and amount
bestAction, bestAmount = gen_action(model, observation, no_predictions=NO_PREDICTIONS)

# Output the action & amount
print(f"\nThe current stock price is ${ohlcvDataframe.iloc[-1][3]:.2f}")
if bestAction == "Hold":
    print("HOLD the stocks.")

elif bestAction == "Sell":
    print(f"If possible, SELL {bestAmount}/5 of owned stocks.")

else:  # Buy
    print(f"If possible, BUY stocks using {bestAmount}/5 of total balance (if possible).")
