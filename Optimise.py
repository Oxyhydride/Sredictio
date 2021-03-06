"""
Optimise.py

Created on 2019-11-30
Updated on 2019-12-14

Copyright Ryan Kan 2019

Description: A program that helps generate an Optuna study which contains the best hyperparameters.
"""

# IMPORTS
import argparse

import optuna
import tensorflow as tf
from stable_baselines import A2C
from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv

from lib.environment.TradingEnv import TradingEnv
from lib.utils import dataUtils

# SETUP
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)  # Remove ugly tensorflow warnings

# ARGUMENTS
parser = argparse.ArgumentParser(description="A file which uses Bayesian Optimisation to find the best hyperparameters "
                                             "for the A2C agent.")

parser.add_argument("stock_dir", type=str, help="Directory where the stock files are found")
parser.add_argument("training_stock", type=str, help="Which stock file should be used for training?")
parser.add_argument("testing_stock", type=str, help="Which stock file should be used for testing?")

parser.add_argument("-t", "--no_trials", type=int, help="Number of trials to find the best hyperparameters",
                    default=1000)
parser.add_argument("-n", "--no_parallel_jobs", type=int, help="Number of parallel jobs", default=1)
parser.add_argument("-f", "--output_file", type=str, help="Output name of the sqlite database",
                    default="Hyperparams.db")
parser.add_argument("-v", "--verbose", choices=["0", "1"], help="Set verbose type. 0 = None, 1 = All", default="1")

args = parser.parse_args()

STOCK_DIRECTORY = args.stock_dir if args.stock_dir[-1] == "/" else args.stock_dir + "/"
TRAINING_STOCK = args.training_stock
TESTING_STOCK = args.testing_stock
OUTPUT_FILE = args.output_file

NO_TRIALS = args.no_trials
NO_JOBS = args.no_parallel_jobs

VERBOSE = int(args.verbose) == 1

# DATA PREPARATION
# Get data for the training dataframe and the testing dataframe
trainingDF = dataUtils.process_data(STOCK_DIRECTORY, TRAINING_STOCK)
testingDF = dataUtils.process_data(STOCK_DIRECTORY, TESTING_STOCK)


# OPTUNA FUNCTIONS
def optimise_a2c(trial):
    """
    A function to get the suggested hyperparameters of the A2C agent.

    Args:
        trial (optuna.Trial): The current Optuna trial

    Returns:
        dict: A dictionary containing all the generated hyperparameters.

    """
    return {
        "gamma": trial.suggest_loguniform("gamma", 0.9, 0.9999),
        "ent_coef": trial.suggest_loguniform("ent_coef", 1e-8, 1e-1),
        "learning_rate": trial.suggest_loguniform("learning_rate", 1e-5, 1.)
    }


def optimise_agent(trial):
    """
    A function to help train the agent with new hyperparameters.

    Args:
        trial (optuna.Trial): The current Optuna trial

    Returns:
        float: The loss of the model.

    """
    # Prepare the agent's environments
    if VERBOSE:
        print("Preparing the environments...")

    train_env = TradingEnv(trainingDF)
    test_env = TradingEnv(testingDF)

    # Generate model hyperparameters
    model_hyperparams = optimise_a2c(trial)
    if VERBOSE:
        print("Obtained the model hyperparams:")
        print(model_hyperparams)

    # Prepare model
    if VERBOSE:
        print("Preparing the model...")

    model = A2C(MlpLstmPolicy, DummyVecEnv([lambda: train_env]), verbose=0, **model_hyperparams)

    # Train the A2C agent with the new hyperparameters
    if VERBOSE:
        print("Training model...")

    model.learn(len(train_env.data_df))  # Run it for `len(train_env.data_df)` iterations

    # Evaluate the performance of the agent
    if VERBOSE:
        print("Calculating the performance of the model...")

    total_inc, done = 0, False
    obs = test_env.reset()

    for i in range(len(test_env.data_df)):
        action, _ = model.predict([obs])
        obs, reward, done, _ = test_env.step(action[0])

        total_inc += reward

        if done:
            break

    # Return the performance of the agent
    if VERBOSE:
        print("Returning the performance...")

    return -float(total_inc)  # Negative because Optuna takes in the LOSS, and not the REWARD


def optimise():
    """
    Creates and runs trials as part of an Optuna study.

    Returns:
        pd.DataFrame: The dataframe containing all the trials' losses and parameters.

    """
    # Create Optuna study
    study = optuna.create_study(study_name="A2C", storage=f"sqlite:///{OUTPUT_FILE}", load_if_exists=True)

    # Run Bayesian Optimisation on the hyperparameters
    try:
        study.optimize(optimise_agent, n_trials=NO_TRIALS, n_jobs=NO_JOBS)

    except KeyboardInterrupt:
        # If there is a KeyboardInterrupt, stop and show the results of the Bayesian Optimisation
        print("\nKeyboardInterrupt was called. Halting trial...")
        pass

    # Output statistics
    print("Number of completed trials:", len(study.trials))

    trial = study.best_trial  # This will get the trial with the best agent

    print("Value of best trial: ", trial.value)
    print("Params of best trial: ")
    for k, v in trial.params.items():
        print("    {}: {}".format(k, v))

    return study.trials_dataframe()


# DEBUG CODE
if __name__ == "__main__":
    optimise()
