"""
Train.py

Created on 2019-11-30
Updated on 2019-12-14

Copyright Ryan Kan 2019

Description: A file which helps train the agent and generate the model file.
"""

# IMPORTS
import argparse
import os

import optuna
from stable_baselines import A2C
from stable_baselines.common import set_global_seeds
from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv

from lib.environment.TradingEnv import TradingEnv
from lib.utils import baselineUtils, dataUtils, graphingUtils
from lib.utils.miscUtils import create_path, natural_sort

# ARGUMENTS
parser = argparse.ArgumentParser(description="A file which helps train the agent and generate the model file.")

parser.add_argument("stock_dir", type=str, help="Which directory should the system obtain the stock data from?")
parser.add_argument("training_stock", type=str, help="Which stock file should be used for training?")
parser.add_argument("testing_stock", type=str, help="Which stock file should be used for testing?")
parser.add_argument("study_file", type=str, help="Where are the parameters stored?")

parser.add_argument("-d", "--model_dir", type=str, help="Which directory should the model be placed in?",
                    default="./Models/")
parser.add_argument("-o", "--output_file_prefix", type=str, help="Prefix of the output file", default="Model")
parser.add_argument("-i", "--init_buyable_stocks", type=float, help="Initial number of stocks that can be bought.",
                    default=2.5)
parser.add_argument("-n", "--no_iterations", type=int, default=50000,
                    help="Number of iterations to train the A2C agent")
parser.add_argument("-a", "--no_entries_taking_avg", type=int, help="Number of entries to consider when taking average",
                    default=10)
parser.add_argument("-m", "--max_trading_session", type=int,
                    help="How many entries, maximally, can the environment take as data?", default=500)
parser.add_argument("-l", "--look_back_window", type=int, default=5,
                    help="How many entries can the model look back into?")
parser.add_argument("-s", "--set_seed", type=int, help="Set the seed of the program", default=None)
parser.add_argument("-r", "--render_type", choices=["0", "1", "2"], default="0",
                    help="What should the program render? 0 = None, 1 = Only A2C Renders, 2 = All renders")
parser.add_argument("-t", "--use_tensorboard", choices=["0", "1"], default="1",
                    help="Should the program use tensorboard? 0 = No, 1 = Yes")

args = parser.parse_args()

STOCK_DIRECTORY = args.stock_dir if args.stock_dir[-1] == "/" else args.stock_dir + "/"
MODEL_DIRECTORY = args.model_dir if args.model_dir[-1] == "/" else args.model_dir + "/"

TRAINING_STOCK = args.training_stock
TESTING_STOCK = args.testing_stock
OUTPUT_FILE_PREFIX = args.output_file_prefix

INIT_BUYABLE_STOCKS = args.init_buyable_stocks

NO_ITERATIONS = args.no_iterations
NO_ENTRIES_TAKING_AVG = args.no_entries_taking_avg
MAX_TRADING_SESSION = args.max_trading_session
LOOK_BACK_WINDOW = args.look_back_window
OPTUNA_STUDY_FILE = args.study_file

SEED = args.set_seed

RENDER = int(args.render_type)
USE_TENSORBOARD = (args.use_tensorboard == "1")

# SETUP
graphingUtils.setup_graph()
set_global_seeds(SEED)

# DATA PREPARATION
trainingDF = dataUtils.process_data(STOCK_DIRECTORY, TRAINING_STOCK, entries_taking_avg=NO_ENTRIES_TAKING_AVG)

# PREPROCESSING
# Run baselines on training data and generate their scores
train_baselines = baselineUtils.Baselines(trainingDF, render=(RENDER == 2))
train_baselines.run_policies()

# Obtain the best agent's parameters from the Optuna study
print("\nLoading Optuna study hyperparameters...")
study = optuna.load_study(study_name="A2C", storage=f"sqlite:///{OPTUNA_STUDY_FILE}")
hyperparams = study.best_trial.params
print("Successfully obtained hyperparameters!\n")

# MODEL TRAINING
# Define a environment for the agent to train on
agentEnv = TradingEnv(trainingDF, init_buyable_stocks=INIT_BUYABLE_STOCKS, max_trading_session=MAX_TRADING_SESSION,
                      is_serial=False, lookback_window_size=LOOK_BACK_WINDOW)
trainEnv = DummyVecEnv([lambda: agentEnv])  # This is the environment which the agent trains on

# Create the A2C agent
if USE_TENSORBOARD:
    model = A2C(MlpLstmPolicy, trainEnv, verbose=1, tensorboard_log="./tensorboard/A2C", **hyperparams)

else:
    model = A2C(MlpLstmPolicy, trainEnv, verbose=1, **hyperparams)

# Train the agent
model.learn(total_timesteps=NO_ITERATIONS, seed=SEED)

# MODEL EVALUATION
# Define an evaluation environment
a2cEnv = TradingEnv(trainingDF, init_buyable_stocks=INIT_BUYABLE_STOCKS, is_serial=True,
                    lookback_window_size=LOOK_BACK_WINDOW)
done = False

train_state = a2cEnv.reset(print_init_invest_amount=True)

while not done:
    action, _ = model.predict([train_state])

    train_state, _, done, _ = a2cEnv.step(action[0])

    if RENDER in [1, 2]:
        a2cEnv.render()

a2cScore = a2cEnv.get_val()  # The model's score

# Output results for the training environment
print("-" * 50, "TRAINING RESULTS", "-" * 50)
print(f"A2C got ${a2cScore:.2f} ({a2cScore / a2cEnv.init_invest * 100 - 100:.3f}% Increase)")
print()

# MODEL TESTING
# Prepare the testing data
testingDF = dataUtils.process_data(STOCK_DIRECTORY, TESTING_STOCK, entries_taking_avg=NO_ENTRIES_TAKING_AVG)

# Run baselines on testing data and generate their scores
test_baselines = baselineUtils.Baselines(testingDF, render=(RENDER == 2))
test_baselines.run_policies()

# Test how well the agent does on the testing environment
a2cEnv = TradingEnv(testingDF, init_buyable_stocks=INIT_BUYABLE_STOCKS, is_serial=True,
                    lookback_window_size=LOOK_BACK_WINDOW)
done = False

test_state = a2cEnv.reset(print_init_invest_amount=True)

while not done:
    action, _ = model.predict([test_state])

    test_state, _, done, _ = a2cEnv.step(action[0])

    if RENDER in [1, 2]:
        a2cEnv.render()

a2cScore = a2cEnv.get_val()  # The model's ending portfolio value

# Output results of the testing environment
print("-" * 50, "TESTING RESULTS", "-" * 50)
print(f"A2C got ${a2cScore:.2f} ({a2cScore / a2cEnv.init_invest * 100 - 100:.3f}% Increase)")
print()

# SAVE THE MODEL
# Create the model directory
create_path(MODEL_DIRECTORY)

# List all files in `MODEL_DIRECTORY`
allModelFiles = natural_sort(os.listdir(MODEL_DIRECTORY))

# Attempt to obtain the latest model
latestModelFile = "NO_FILE_FOUND!"
for fileName in allModelFiles:
    if fileName[:7] == "LATEST=":
        latestModelFile = fileName
        break

# Check if there is a latest model
if latestModelFile != "NO_FILE_FOUND!":  # There is a latest model
    # Get all existing files
    allExistingFiles = os.listdir(MODEL_DIRECTORY)

    currRenameAttempt = 0
    while True:
        # Generate new name
        if currRenameAttempt == 0:
            proposedName = latestModelFile[7:]
        else:
            proposedName = latestModelFile[7:].split(".")[0] + f" ({currRenameAttempt}).zip"

        if proposedName not in allExistingFiles:
            # No conflicting games; go ahead with rename
            os.rename(MODEL_DIRECTORY + latestModelFile, MODEL_DIRECTORY + proposedName)
            break

        else:
            # Conflicting names; increment `currRenameAttempt` by 1 and try again
            currRenameAttempt += 1

# Save the current model as the latest model
model.save(MODEL_DIRECTORY + f"LATEST={OUTPUT_FILE_PREFIX}_LBW-{LOOK_BACK_WINDOW}_NOI-{NO_ITERATIONS}.zip")
