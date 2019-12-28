"""
Test Sredictio.py

Created on 2019-12-25
Updated on 2019-12-28

Copyright Ryan Kan 2019

Description: A file which allows the user to test the model on previous data.
"""

# IMPORTS
import argparse
import datetime

import tensorflow as tf
from stable_baselines import A2C

from lib.environment.tradingEnv import TradingEnv
from lib.utils.baselineUtils import Baselines
from lib.utils.dataUtils import process_data, add_technical_indicators
from lib.utils.executionUtils.genAction import gen_action
from lib.utils.executionUtils.obtainData import get_model_file, get_lookback_window
from lib.utils.sentimentUtils import get_sentiment_data
from lib.utils.stockUtils import get_ohlcv_data

# SETUP
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)  # Remove tensorflow warnings

# ARGUMENTS
parser = argparse.ArgumentParser(description="A program which helps test Sredictio's model on previously known data.")

parser.add_argument("model_dir", type=str, help="The model directory, which contains all the model files.")
parser.add_argument("start_date", type=str, help="The first date to scrape the data. The start date has to be OLDER "
                                                 "than the end date. Note that the date has to be in the form "
                                                 "YYYY-MM-DD.")
parser.add_argument("end_date", type=str, help="The last date to scrape the data. The end date has to be MORE RECENT "
                                               "than the start date. Note that the date has to be in the form "
                                               "YYYY-MM-DD.")
parser.add_argument("stock_name", type=str, help="The stock's name. E.G. Amazon, Apple, Google, Tesla")
parser.add_argument("stock_symbol", type=str,
                    help="The stock's symbol. Also known as the ticker. E.G. AMZN, AAPL, GOOGL, TSLA")

parser.add_argument("-p", "--no_predictions", type=int,
                    help="Number of predictions to run when choosing the action to take.", default=100)
parser.add_argument("-r", "--retry_count", type=int, help="Number of attempts to get the data from Yahoo Finance.",
                    default=3)
parser.add_argument("-a", "--no_entries_taking_avg", type=int, help="Number of entries to consider when taking average",
                    default=3)
parser.add_argument("-i", "--init_buyable_stocks", type=float, help="Initial number of stocks that can be bought.",
                    default=2.5)
parser.add_argument("-render", "--render_type", choices=["0", "1", "2"], default="0",
                    help="What should the program render? 0 = None, 1 = Only A2C Renders, 2 = All renders")

args = parser.parse_args()

START_DATE = args.start_date
END_DATE = args.end_date

INIT_BUYABLE_STOCKS = args.init_buyable_stocks

STOCK_NAME = args.stock_name
STOCK_SYMBOL = args.stock_symbol

MODEL_DIRECTORY = args.model_dir if args.model_dir[-1] == "/" else args.model_dir + "/"
NO_PREDICTIONS = int(args.no_predictions)

RENDER = int(args.render_type)
RETRY_COUNT = args.retry_count
NO_ENTRIES_TAKING_AVG = int(args.no_entries_taking_avg)

# OBTAINING DATA
# Get the model file from the model directory
modelFile = get_model_file(MODEL_DIRECTORY)

# Get the value for the lookback window from the model file
lookbackWindow = get_lookback_window(modelFile)

# Determine how many days to scrape
daysDiff = (datetime.datetime.strptime(END_DATE, "%Y-%m-%d") - datetime.datetime.strptime(START_DATE, "%Y-%m-%d")).days

# Calculate the adjusted start date
adjustedStartDate = (datetime.datetime.strptime(END_DATE, "%Y-%m-%d") - datetime.timedelta(days=daysDiff)).strftime(
    "%Y-%m-%d")

# Get OHLCV dataframe
ohlcvDataframe = get_ohlcv_data(STOCK_SYMBOL, adjustedStartDate, END_DATE, retry_count=RETRY_COUNT)

# Get sentiment dataframe
print(f"Obtaining {STOCK_NAME} sentiment data...")
sentimentDataframe = get_sentiment_data(STOCK_SYMBOL, STOCK_NAME, adjustedStartDate, END_DATE, verbose=False)
print("Done!")

# PREPROCESSING
# Remove "Adj Close" column from `ohlcvDataframe`
ohlcvDataframe = ohlcvDataframe.drop(ohlcvDataframe.columns[5], axis=1)

# Typecast the "Date" columns to be string, and not `pd.Timestamp`
ohlcvDataframe["Date"] = ohlcvDataframe["Date"].astype(str)
sentimentDataframe["Date"] = sentimentDataframe["Date"].astype(str)

# Convert the stock dataframe to `np.ndarray`
ohlcvArr = ohlcvDataframe.values

# Convert the sentiment dataframe into `np.ndarray`, and reverse it
sentimentArr = sentimentDataframe.values[::-1]

# Get preprocessed combined dataframe
combinedDF = process_data(ohlcvArr, sentimentArr, entries_taking_avg=NO_ENTRIES_TAKING_AVG)

# Move sentiment column to the right
combinedDF = combinedDF[["Open", "High", "Low", "Close", "Volume", "Sentiment"]]

# Add technical indicators to the dataframe
combinedDF = add_technical_indicators(combinedDF)

# Load the latest model
model = A2C.load(MODEL_DIRECTORY + modelFile)

# Test how well the agent does on the data
agentEnv = TradingEnv(combinedDF, init_buyable_stocks=INIT_BUYABLE_STOCKS, is_serial=True,
                      lookback_window_size=lookbackWindow)

done = False
state = agentEnv.reset(print_init_invest_amount=True)
print()

while not done:
    # Generate action
    bestAction, bestAmount = gen_action(model, state, no_predictions=NO_PREDICTIONS)

    # Combine `bestAction` and `bestAmount` into a single list `action`
    action = [0, 0]
    action[0] = 0 if bestAction == "Sell" else 1 if bestAction == "Hold" else 2
    action[1] = bestAmount - 1  # The environment expects this value to be from 0 to 4

    # Output the generated action
    print(f"CV: ${agentEnv.full_data_df['Close'][agentEnv.cur_step]:.2f}| NW: ${agentEnv.get_val():.2f} | ", end="")
    if bestAction == "Hold":
        print("HOLD")

    elif bestAction == "Sell":
        print(f"SOLD {bestAmount + 1}/5")

    else:  # Buy
        print(f"BUY  {bestAmount + 1}/5")

    # Update the environment with the generated action
    state, _, done, _ = agentEnv.step(action)

    # Render the environment (if permitted)
    if RENDER in [1, 2]:
        agentEnv.render()

# Get agent's ending value
a2cScore = agentEnv.get_val()  # The model's ending portfolio value

# Output results of the testing environment
print(f"A2C got ${a2cScore:.2f} ({a2cScore / agentEnv.init_invest * 100 - 100:.3f}% Increase)")
print()

# Run the baselines against the A2C agent
baselines = Baselines(combinedDF, render=(RENDER == 2), init_buyable_stocks=INIT_BUYABLE_STOCKS)
baselines.run_policies()
