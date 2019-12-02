"""
train.py
Version 1.1.0

Created on 2019-11-30
Updated on 2019-12-02

Copyright Ryan Kan 2019

Description: A file which helps train the agent
"""

# IMPORTS
import argparse

from stable_baselines import A2C
from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv

from env.TradingEnv import TradingEnv
from utils import baselineUtils, dataUtils, graphUtils

# ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument("stock_dir", type=str, help="Which directory should the system obtain the stock data from?")
parser.add_argument("training_stock", type=str, help="Which stock file should be used for training?")
parser.add_argument("testing_stock", type=str, help="Which stock file should be used for testing?")
parser.add_argument("no_iterations", type=int, help="Number of iterations to train the A2C agent")

parser.add_argument("-i", "--init_invest", type=float, help="Initial investment amount", default=25.0)
parser.add_argument("-a", "--no_entries_taking_avg", type=int, help="Number of entries to consider when taking average",
                    default=10)
parser.add_argument("-m", "--max_trading_session", type=int,
                    help="How many entries, maximally, can the environment take as data?", default=500)

args = parser.parse_args()

STOCK_DIRECTORY = args.stock_dir
TRAINING_STOCK = args.training_stock
TESTING_STOCK = args.testing_stock

INIT_INVEST = args.init_invest

NO_ITERATIONS = args.no_iterations
NO_ENTRIES_TAKING_AVG = args.no_entries_taking_avg
MAX_TRADING_SESSION = args.max_trading_session

# SETUP
graphUtils.setup_graph()

# DATA PREPARATION
trainingDF = dataUtils.prep_data(STOCK_DIRECTORY, TRAINING_STOCK, entries_taking_avg=NO_ENTRIES_TAKING_AVG)

# PRE-TRAINING PROCESSING
# Prepare baseline scores on training data
train_baselines = baselineUtils.Baselines(trainingDF, render=False)
train_baseline_scores = train_baselines.run_policies()

# MODEL TRAINING
# Define a environment for the agent to train on
agentEnv = TradingEnv(trainingDF, init_invest=INIT_INVEST, max_trading_session=MAX_TRADING_SESSION, is_serial=False)
trainEnv = DummyVecEnv([lambda: agentEnv])

# Create an A2C agent
model = A2C(MlpLstmPolicy, trainEnv, verbose=1, tensorboard_log="./tensorboard/A2C")

# Train the model!
model.learn(total_timesteps=NO_ITERATIONS)

# MODEL EVALUATION
# How well did our model perform on the training data?
a2cEnv = TradingEnv(trainingDF, init_invest=INIT_INVEST, is_serial=True)
done = False

train_state = a2cEnv.reset()

while not done:
    action, _ = model.predict([train_state])

    train_state, _, done, _ = a2cEnv.step(action[0])
    a2cEnv.render()

a2cScore = a2cEnv.get_val()  # The model's score

# Output results
print("-" * 50 + " TRAINING RESULTS " + "-" * 50)
print("A2C Score: {:.3f}".format(a2cScore))
print("A2C - BHODL = {:.3f}".format(a2cScore - train_baseline_scores[0]))
print("A2C - RSI Divergence = {:.3f}".format(a2cScore - train_baseline_scores[1]))
print("A2C - SMA Crossover = {:.3f}".format(a2cScore - train_baseline_scores[2]))
print()

# MODEL TESTING
# Prepare testing data
testingDF = dataUtils.prep_data(STOCK_DIRECTORY, TESTING_STOCK, entries_taking_avg=NO_ENTRIES_TAKING_AVG)

# Generate baseline scores
test_baselines = baselineUtils.Baselines(testingDF, render=False)
test_baseline_scores = test_baselines.run_policies()

# Run the A2C agent on the testing data
a2cEnv = TradingEnv(testingDF, init_invest=INIT_INVEST, is_serial=True)  # For training purposes
done = False

test_state = a2cEnv.reset()

while not done:
    action, _ = model.predict([test_state])

    test_state, _, done, _ = a2cEnv.step(action[0])
    a2cEnv.render()

a2cScore = a2cEnv.get_val()  # The model's score

# Output results
print("-" * 50 + " TESTING RESULTS " + "-" * 50)
print("A2C Score: {:.3f}".format(a2cScore))
print("A2C - BHODL = {:.3f}".format(a2cScore - test_baseline_scores[0]))
print("A2C - RSI Divergence = {:.3f}".format(a2cScore - test_baseline_scores[1]))
print("A2C - SMA Crossover = {:.3f}".format(a2cScore - test_baseline_scores[2]))
print()
