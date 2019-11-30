"""
train.py
Version 1.0.0

Created on 2019-11-30
Updated on 2019-11-30

Copyright Ryan Kan 2019

Description: A file which helps train the agent
"""

# IMPORTS
from stable_baselines import A2C
from stable_baselines.common import set_global_seeds
from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv

from env.TradingEnv import TradingEnv
from utils import baselineUtils, dataUtils, graphUtils

# CONSTANTS
STOCK_DIRECTORY = "./data/"  # Where should the system obtain the stock data from?
TRAINING_STOCK = "FB"  # Which stock file should be used for training?
TESTING_STOCK = "BTC"  # Which stock file should be used for testing?

INIT_INVEST = 25.0

SEED = 256  # Seed of the model
NO_ENTRIES_TAKING_AVG = 10  # No. entries to consider when taking average

NO_ITERATIONS = 100000  # Number of iterations to train the A2C agent on?
MAX_TRADING_SESSION = 500  # How many entries, maximally, can the environment take as data?

# SETUP
graphUtils.setup_graph()
set_global_seeds(SEED)

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
print("A2C Score: {:.3f}".format(a2cScore))
print("A2C - BHODL = {:.3f}".format(a2cScore - train_baseline_scores[0]))
print("A2C - RSI Divergence = {:.3f}".format(a2cScore - train_baseline_scores[1]))
print("A2C - SMA Crossover = {:.3f}".format(a2cScore - train_baseline_scores[2]))

# MODEL TESTING
# Prepare testing data
testingDF = dataUtils.prep_data(STOCK_DIRECTORY, TESTING_STOCK)

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
print("A2C Score: {:.3f}".format(a2cScore))
print("A2C - BHODL = {:.3f}".format(a2cScore - test_baseline_scores[0]))
print("A2C - RSI Divergence = {:.3f}".format(a2cScore - test_baseline_scores[1]))
print("A2C - SMA Crossover = {:.3f}".format(a2cScore - test_baseline_scores[2]))
