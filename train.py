"""
train.py
Version 1.1.2

Created on 2019-11-30
Updated on 2019-12-03

Copyright Ryan Kan 2019

Description: A file which helps train the agent and generate the model file.
"""

# IMPORTS
import argparse

import optuna
from stable_baselines import A2C
from stable_baselines.common import set_global_seeds
from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv

from env.TradingEnv import TradingEnv
from utils import baselineUtils, dataUtils, graphUtils

# ARGUMENTS
parser = argparse.ArgumentParser(description="A file which helps train the agent and generate the model file.")

parser.add_argument("stock_dir", type=str, help="Which directory should the system obtain the stock data from?")
parser.add_argument("training_stock", type=str, help="Which stock file should be used for training?")
parser.add_argument("testing_stock", type=str, help="Which stock file should be used for testing?")
parser.add_argument("study_file", type=str, help="Where are the parameters stored?")

parser.add_argument("-o", "--output_file", type=str, help="Name of the output file", default="Model.model")
parser.add_argument("-i", "--init_invest", type=float, help="Initial investment amount", default=25.0)
parser.add_argument("-n", "--no_iterations", type=int, default=50000,
                    help="Number of iterations to train the A2C agent")
parser.add_argument("-a", "--no_entries_taking_avg", type=int, help="Number of entries to consider when taking average",
                    default=10)
parser.add_argument("-m", "--max_trading_session", type=int,
                    help="How many entries, maximally, can the environment take as data?", default=500)
parser.add_argument("-s", "--set_seed", type=int, help="Set the seed of the program", default=None)
parser.add_argument("-r", "--render_type", choices=["0", "1", "2"], default="1",
                    help="What should the program render? 0 = None, 1 = Only A2C Renders, 2 = All renders")

args = parser.parse_args()

STOCK_DIRECTORY = args.stock_dir
TRAINING_STOCK = args.training_stock
TESTING_STOCK = args.testing_stock
OUTPUT_FILE = args.output_file

INIT_INVEST = args.init_invest

NO_ITERATIONS = args.no_iterations
NO_ENTRIES_TAKING_AVG = args.no_entries_taking_avg
MAX_TRADING_SESSION = args.max_trading_session
OPTUNA_STUDY_FILE = args.study_file

SEED = args.set_seed

RENDER = int(args.render_type)

# SETUP
graphUtils.setup_graph()
set_global_seeds(SEED)

# DATA PREPARATION
trainingDF = dataUtils.prep_data(STOCK_DIRECTORY, TRAINING_STOCK, entries_taking_avg=NO_ENTRIES_TAKING_AVG)

# PREPROCESSING
# Prepare baseline scores on training data
train_baselines = baselineUtils.Baselines(trainingDF, render=(RENDER == 2))
train_baseline_scores = train_baselines.run_policies()

# Obtain best study's parameters
study = optuna.load_study(study_name="A2C", storage=f"sqlite:///{OPTUNA_STUDY_FILE}")
params = study.best_trial.params

# MODEL TRAINING
# Define a environment for the agent to train on
agentEnv = TradingEnv(trainingDF, init_invest=INIT_INVEST, max_trading_session=MAX_TRADING_SESSION, is_serial=False,
                      seed=SEED)
trainEnv = DummyVecEnv([lambda: agentEnv])

# Create an A2C agent
model = A2C(MlpLstmPolicy, trainEnv, verbose=1, tensorboard_log="./tensorboard/A2C", **params)

# Train the model!
model.learn(total_timesteps=NO_ITERATIONS, seed=SEED)

# MODEL EVALUATION
# How well did our model perform on the training data?
a2cEnv = TradingEnv(trainingDF, init_invest=INIT_INVEST, is_serial=True, seed=SEED)
done = False

train_state = a2cEnv.reset()

while not done:
    action, _ = model.predict([train_state])

    train_state, _, done, _ = a2cEnv.step(action[0])

    if RENDER in [1, 2]:
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
test_baselines = baselineUtils.Baselines(testingDF, render=(RENDER == 2))
test_baseline_scores = test_baselines.run_policies()

# Run the A2C agent on the testing data
a2cEnv = TradingEnv(testingDF, init_invest=INIT_INVEST, is_serial=True)  # For training purposes
done = False

test_state = a2cEnv.reset()

while not done:
    action, _ = model.predict([test_state])

    test_state, _, done, _ = a2cEnv.step(action[0])

    if RENDER in [1, 2]:
        a2cEnv.render()

a2cScore = a2cEnv.get_val()  # The model's score

# Output results
print("-" * 50 + " TESTING RESULTS " + "-" * 50)
print("A2C Score: {:.3f}".format(a2cScore))
print("A2C - BHODL = {:.3f}".format(a2cScore - test_baseline_scores[0]))
print("A2C - RSI Divergence = {:.3f}".format(a2cScore - test_baseline_scores[1]))
print("A2C - SMA Crossover = {:.3f}".format(a2cScore - test_baseline_scores[2]))
print()

# SAVE THE MODEL
model.save(OUTPUT_FILE)
