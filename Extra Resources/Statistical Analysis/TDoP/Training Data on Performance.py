# # Imports
print("Loading libraries...")
import datetime

import ta
import gym
import numpy as np
import pandas as pd
import seaborn as sns

from tqdm import tqdm
from gym import spaces
from pylab import rcParams
from pandas import read_csv
from matplotlib import pyplot as plt
from empyrical import sortino_ratio, calmar_ratio, omega_ratio

from stable_baselines import A2C
from stable_baselines.common import set_global_seeds
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.policies import MlpLstmPolicy

print("Done!\n")

# # Constants
TRAINING_DIRECTORY = "./trainingData/"  # Remember to add a "/" at the end
TESTING_DIRECTORY = "./testData/"  # Remember to add a "/" at the end

INIT_INVEST = 25.0

SEED = 256  # Seed of the model
NO_ENTRIES_TAKING_AVG = 10  # No. entries to consider when taking average

NO_ITERATIONS = 100000
MAX_TRADING_SESSION = 500  # How many entries, maximally, can the environment take as data?

IS_JUPYTER = False  # Is this run in a Jupyter notebook?

TRAINING_STOCKS = ["005930.KS", "AAPL", "AMZN", "BA", "FB", "GOOGL", "S63.SI", "TSLA", "U11.SI"]
TESTING_STOCKS = ["BTC", "DIS", "Z74.SI"]

# # Setup
print("Setting up...")
# Graph setup
def setup_graph(jupyter=False, render=False):
    # For Jupyter notebook
    if jupyter:
        if render:
            get_ipython().run_line_magic('matplotlib', 'notebook')
        
        else:
            get_ipython().run_line_magic('matplotlib', 'inline')
    
    if not render:
        rcParams['figure.figsize'] = 14, 8
    
    # Setup Seaborn style
    sns.set(style='white', palette='muted', font_scale=1.5)

setup_graph(jupyter=IS_JUPYTER)

# Seeding setup
set_global_seeds(SEED)

print("Done!\n")
# # Data Preparation
print("Preparing data...")

# To process the data from each subdirectory, a function called `get_data()` will handle the obtaining of data from each sub directory.
def get_data(directory):
    """
    Processes data from one subdirectory in the root directory
    to be parsed later for data training.
    
    directory: Directory which contains the stock values file and
               the sentiment scores file
    """
    full_path = directory

    # Load stock prices from the CSV file
    stock_data = read_csv(full_path + "stocks.csv", header=0, squeeze=True)

    # Remove the "Adj Close" and "Volume" column
    stock_data = stock_data.drop(stock_data.columns[list(range(5, 7))], axis=1)
    
    # Convert stock data to np.array
    stock_arr = stock_data.values

    # Load sentiment data
    sentiment_data = read_csv(full_path + "sentiments.csv", header=0, squeeze=True)

    # Convert sentiment data to np.array
    sentiment_arr = sentiment_data.values[::-1]
    
    # Fill in missing values for sentiment data
    sentiment_arr_new = sentiment_arr.copy()

    i = 0
    first_date = sentiment_arr_new[0][0]  # The literal first date

    while i < sentiment_arr_new.shape[0] - 1:
        date1 = datetime.datetime.strptime(sentiment_arr_new[i][0], "%Y-%m-%d")
        date2 = datetime.datetime.strptime(sentiment_arr_new[i + 1][0], "%Y-%m-%d")

        if (date2 - date1).total_seconds() > 60 * 60 * 24:  # More than 1 day
            no_days_separation = int((date2 - date1).total_seconds() / (60 * 60 * 24))
            difference_per_day = (sentiment_arr_new[i + 1][1] - sentiment_arr_new[i][1]) / no_days_separation

            for day in range(1, no_days_separation):
                sentiment_arr_new = np.insert(sentiment_arr_new, i + day, [datetime.datetime.strftime(date1 + datetime.timedelta(days=day), "%Y-%m-%d"), sentiment_arr_new[i][1] + day * difference_per_day], axis=0)

            i+= no_days_separation - 1
        i += 1

    sentiment_arr = sentiment_arr_new[:-1]
    
    # Fill in missing values for stock data
    stock_arr_new = list(stock_arr)

    i = 0
    first_date_processed = datetime.datetime.strptime(first_date, "%Y-%m-%d")
    first_surpassed_index = -1
    while i < len(stock_arr_new[:-1]):
        date1 = datetime.datetime.strptime(stock_arr_new[i][0], "%Y-%m-%d")

        if date1 >= first_date_processed:
            if first_surpassed_index == -1:
                first_surpassed_index = i

            date2 = datetime.datetime.strptime(stock_arr_new[i+1][0], "%Y-%m-%d")

            if (date2 - date1).total_seconds() > 60 * 60 * 24:  # More than 1 day
                no_days_separation = int((date2 - date1).total_seconds() / (60 * 60 * 24))
                
                difference_open = (stock_arr_new[i + 1][1] - stock_arr_new[i][1]) / no_days_separation
                difference_high = (stock_arr_new[i + 1][2] - stock_arr_new[i][2]) / no_days_separation
                difference_low = (stock_arr_new[i + 1][3] - stock_arr_new[i][3]) / no_days_separation
                difference_close = (stock_arr_new[i + 1][4] - stock_arr_new[i][4]) / no_days_separation

                for day in range(1, no_days_separation):
                    stock_arr_new.insert(i + day, [datetime.datetime.strftime(date1 + datetime.timedelta(days=day), "%Y-%m-%d"), 
                                                   stock_arr_new[i][1] + day * difference_open,
                                                   stock_arr_new[i][2] + day * difference_high,
                                                   stock_arr_new[i][3] + day * difference_low,
                                                   stock_arr_new[i][4] + day * difference_close])

                i += no_days_separation - 1
        i += 1

    stock_arr = np.array(stock_arr_new[first_surpassed_index:-1], dtype=object)
    
    # Clear memory
    del stock_arr_new, sentiment_arr_new, first_date_processed, i, first_date, first_surpassed_index
    
    # Make both start on same day
    if sentiment_arr[0][0] != stock_arr[0][0]:
        if sentiment_arr[0][0] < stock_arr[0][0]:
            while True:
                sentiment_arr = np.delete(sentiment_arr, 0, axis=0)

                if sentiment_arr[0][0] == stock_arr[0][0]:
                    break

        else:  # Must be larger
            while True:
                stock_arr = np.delete(stock_arr, 0, axis=0)

                if sentiment_arr[0][0] == stock_arr[0][0]:
                    break
    
    # Make both end on same day
    if sentiment_arr[-1][0] != stock_arr[-1][0]:
        if sentiment_arr[-1][0] < stock_arr[-1][0]:        
            while True:
                stock_arr = np.delete(stock_arr, stock_arr.shape[0]-1, axis=0)
                if sentiment_arr[sentiment_arr.shape[0] - 1][0] == stock_arr[stock_arr.shape[0] - 1][0]:
                    break

        else:  # Must be larger
            while True:
                sentiment_arr = np.delete(sentiment_arr, sentiment_arr.shape[0] - 1, axis=0)
                if sentiment_arr[sentiment_arr.shape[0] - 1][0] == stock_arr[stock_arr.shape[0] - 1][0]:
                    break
                    
    # Join the two separate arrays into one single array
    data_arr = []
    for i in range(stock_arr.shape[0]):  # Should have same shape
        data_arr.append([stock_arr[i][0], stock_arr[i][1], stock_arr[i][2], stock_arr[i][3], stock_arr[i][4], sentiment_arr[i][1]])  # The format is: DATE, OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, SENTIMENT_VAL

    return np.array(data_arr, dtype=object)

print("Done!\n")
# # Preprocessing
print("Preprocessing data...")

# To save time and effort for future preprocessings, we create a universal function `prep_data()` to load and prepare the data required for training. `prep_data()` will take the source directory as input, and will output a dataframe as the output.

def prep_data(directory):
    def normalise(xi, xmin, xmax, p=0, q=1):
        """
        Normalises the data to be in the range p to q.
        """
        return (((q - p) * (xi - xmin)) / (xmax - xmin)) + p
    
    def moving_avg(arr, index, i_val, no_entries_taking_avg):
        """
        Computes the moving average list given an array `arr`.
        """
        return sum([x[index] for x in arr[i_val - no_entries_taking_avg:i_val]]) / no_entries_taking_avg
        
    dl = get_data(directory)
    
    # Find min and max from stocks
    min_val = float("inf")
    max_val = -float("inf")

    for entry in dl:
        # Check for stock values ONLY
        min_val = min(min_val, min(entry[1], min(entry[2], min(entry[3], entry[4]))))
        max_val = max(max_val, max(entry[1], max(entry[2], max(entry[3], entry[4]))))
    
    # Normalise both the stocks' values and the sentiment values
    normed = []

    for entry in dl:
        # Normalise stock values. The Sentiment value can remain as is
        normed.append([normalise(entry[1], min_val, max_val, p=1, q=10),
                       normalise(entry[2], min_val, max_val, p=1, q=10),
                       normalise(entry[3], min_val, max_val, p=1, q=10),
                       normalise(entry[4], min_val, max_val, p=1, q=10),
                       entry[5]])

    # Take moving average of both the stock values and the sentiment values
    avged = []

    for i in range(NO_ENTRIES_TAKING_AVG, len(normed)):  # Remove `NO_ENTRIES_TAKING_AVG` entries from the datalist
        avged.append([moving_avg(normed, 0, i, NO_ENTRIES_TAKING_AVG),
                      moving_avg(normed, 1, i, NO_ENTRIES_TAKING_AVG),
                      moving_avg(normed, 2, i, NO_ENTRIES_TAKING_AVG),
                      moving_avg(normed, 3, i, NO_ENTRIES_TAKING_AVG),
                      moving_avg(normed, 4, i, NO_ENTRIES_TAKING_AVG),
                     ])
    
    # Convert `avged` to a pandas dataframe
    df_dict = {"Open": [], "High": [], "Low": [], "Close": [], "Sentiment": []}
    
    for i in range(len(avged)):
        df_dict["Open"].append(avged[i][0])
        df_dict["High"].append(avged[i][1])
        df_dict["Low"].append(avged[i][2])
        df_dict["Close"].append(avged[i][3])
        df_dict["Sentiment"].append(avged[i][4])
        
    df = pd.DataFrame(df_dict)
    
    return df

# # Building the environment

# **Observation State**: [# of stock owned, open history, high history, low history, close history, 
#                         sentiment history, cash in hand history, net worth history]
# 
# **Action Space**: 
# - 3 Actions: Sell [0], Hold [1], Buy [2]
# - 10 Amounts: 1/10 of total, 2/10 of total, 3/10 of total etc.

class TradingEnv(gym.Env):
    """
    The trading environment.
  
    Observation State: [# of stock owned, open history, high history, low history, close history, 
                        sentiment history, cash in hand history, net worth history]

    Action Space: 
    - 3 Actions: Sell [0], Hold [1], Buy [2]
    - 10 Amounts: 1/10 of total, 2/10 of total, 3/10 of total etc.
    """
    metadata = {'render.modes': ['human', 'system', 'none']}
    viewer = None

    def __init__(self, data_df, init_invest=25.0, reward_len=32, lookback_window_size=5, is_serial=False, reward_function="Difference", forecast_length=5):
        """
        Initialization function for the trading environment.
        
        Keyword arguments:
        - data_df, pd.DataFrame: A pandas dataframe containing all the data.
        - init_invest, Float: Starting cash (Default = 5.0)
        - reward_len, Integer: No of entries to consider when calculating reward (Default = 32)
        - lookback_window_size, Integer: How many entries can the agent look back? (Default = 5)
        - is_serial, bool: Is the environment serial (i.e. following a strict sequence)? (Default = False)
        - reward_function, string: What reward function to use? Must be in the list [Difference"]. (Default = "Difference")
        - forecast_length, int: How many entries to forecast? (Default = 5)
        """
        # Assert reward function parameter is defined
        assert reward_function in ["Difference"], "Reward function not in the list [Difference]"
        
        # Convert given data into variables
        self.data_df = data_df  # This is the dataframe where all the data is stored
        self.full_data_arr = self.data_df.values  # All the values, converted into a np.array
        self.init_invest = init_invest  # Initial investment value
        self.reward_len = reward_len  # Length of reward consideration array
        self.lookback_window = lookback_window_size  # Size of the lookback window
        self.is_serial = is_serial  # Is the environment serial?
        self.reward_function = reward_function  # The reward function
        self.forecast_len = forecast_length  # The forecast length
        
        # Create the histories
        self.open_history = [x[0] for x in self.full_data_arr]  # All the `Open` values for the stock
        self.high_history = [x[1] for x in self.full_data_arr]  # All the `High` values for the stock
        self.low_history = [x[2] for x in self.full_data_arr]  # All the `Low` values for the stock
        self.close_history = [x[3] for x in self.full_data_arr]  # All the `Close` values for the stock
        self.sentiment_history = [x[4] for x in self.full_data_arr]  # This is the normalised sentiment data
        
        # Create data_arr
        self.total_len = len(self.data_df)
        self.cur_len = None
        
        self.start_index = None
        self.end_index = None
        
        self.data_arr = None
        self.generate_data_arr(is_serial)

        # Instance attributes
        self.cur_step = self.start_index
        self.stock_owned = None
        self.cash_in_hand = None
        self.done = False
        self.actions_taken = []
        self.actions_amounts = []
        
        # Observation space variables
        self.net_worths = None
        self.stock_owned_history = None
        self.cash_in_hand_history = None

        # Action space
        self.action_space = spaces.MultiDiscrete([3, 10]) 
        
        # Observation space: give estimates in order to sample and build scaler
        stock_max = max(max(self.open_history), max(max(self.high_history), max(max(self.low_history), max(self.close_history))))

        self.observation_space = spaces.Box(low=-1, high=init_invest * 3 * (1 + (1 // stock_max)), shape=(8, self.lookback_window), dtype=np.float32)
        
        # Rendering variables
        self.fig = None
        self.net_worth_ax = None
        self.net_worth_annotation = None
        self.net_worth_line = None
        self.stock_ax = None
        self.stock_line = None
        self.stock_annotation = None
        
        # Reset env and start
        self.reset()
        
    def generate_data_arr(self, serial):
        """
        Generates the new data_arr.
        
        Keyword arguments:
        - serial, bool: Is the environment serial (i.e. following a strict sequence)?
        """
        
        if serial:  # No need to randomise the start and end positions
            # Use all of the data_df values
            self.start_index = self.lookback_window
            self.end_index = self.total_len - 1
            
            self.cur_len = self.end_index - self.start_index
        
        else:
            # Generate a random range for training
            local_max_trading_session = min(MAX_TRADING_SESSION, self.total_len)  # We won't want it exceeding, now would we?
            
            self.cur_len = np.random.randint(self.lookback_window, local_max_trading_session) - self.lookback_window - 1
            self.start_index = np.random.randint(self.lookback_window, self.total_len - self.cur_len)
            self.end_index = self.start_index + self.cur_len
            
        self.data_arr = self.data_df.values[self.start_index: self.end_index]

    def reset(self):
        """
        Resets the environment.
        """
        # Create new active array
        self.generate_data_arr(self.is_serial)
        
        # Reset all needed variables
        self.cur_step = self.start_index  # Step reset to 0
        self.stock_owned = 0.
        self.cash_in_hand = self.init_invest
        self.actions_taken = []
        self.actions_amounts = []
        
        self.net_worths = [self.init_invest] * self.lookback_window
        self.stock_owned_history = [0] * self.lookback_window
        self.cash_in_hand_history = [self.init_invest] * self.lookback_window
        
        self.fig = None
        self.net_worth_ax = None
        self.net_worth_annotation = None
        self.net_worth_line = None
        self.stock_ax = None
        self.stock_line = None
        self.stock_annotation = None
        
        # Clear figure
        plt.clf()
        
        return self.get_obs()

    def step(self, action):
        """
        Moves forward one step in time.
        
        Keyword arguments:
        - action: Action to be taken. (Integer)
        
        Returns:
        - Observation space (List)
        - reward: Reward for taking the action (Float)
        - done: Whether the environment has completed its cycle (Boolean Value)
        - info: Useful info (String)
        """
        # Move forward one day in time
        self.cur_step += 1
        self.trade(action)
        
        # What's changed?
        self.net_worths.append(self.get_val())  # Current net worth
        
        # Generate reward
        reward = self.gen_reward()
        
        # Update info
        info = {'cur_val': self.net_worths[-1]}
        
        return self.get_obs(), reward, self.done, info

    def get_obs(self):
        """
        Gets the observation list.
        
        Returns:
        - Observation list (List)
        """
        return np.array([self.stock_owned_history[-self.lookback_window:], 
                         self.open_history[self.cur_step-self.lookback_window: self.cur_step], 
                         self.high_history[self.cur_step-self.lookback_window: self.cur_step],
                         self.low_history[self.cur_step-self.lookback_window: self.cur_step],
                         self.close_history[self.cur_step-self.lookback_window: self.cur_step],
                         self.sentiment_history[self.cur_step-self.lookback_window: self.cur_step], 
                         self.cash_in_hand_history[-self.lookback_window:],
                         self.net_worths[-self.lookback_window:]])

    def get_val(self):
        """
        Calculates the current portfolio value of the Agent.
        
        Returns:
        - Portfolio value (Float)
        """
        return self.stock_owned * self.close_history[self.cur_step] + self.cash_in_hand
    
    def gen_reward(self):
        """
        Generates the reward based on the reward function defined.
        """
        reward = None
        
        """
        REWARD FUNCTION: Difference
        Take current net worth - previous net worth.
        """
        reward = self.net_worths[-1] - self.net_worths[-2]
        
        return reward if np.isfinite(reward) else 0

    def trade(self, action):
        """
        Helper function to "trade" the stocks
        
        Keyword arguments:
        - action: Action to take (Integer)
        """
        # Check if done
        self.done = self.cur_step >= self.end_index  # Only will be done if the current step is the ending step (in zero based indexing)
        
        # Split Action type and Amount
        action_type = action[0]
        action_amount = action[1] / 10  # Representing 1/10, 2/10, 3/10 etc.
        
        if action_type == 0:  # Sell
            stock_sold = int(self.stock_owned * action_amount)  # We won't want partial stocks, now do we?
            
            self.cash_in_hand += self.open_history[self.cur_step] * stock_sold
            self.stock_owned -= stock_sold
        
        elif action_type == 1:  # Hold
            # Nothing to do here, move on.
            pass
        
        elif action_type == 2:  # Buy
            stock_bought = int((self.cash_in_hand / self.open_history[self.cur_step]) * action_amount)  # We won't want partial stocks, now do we?
            
            self.cash_in_hand -= self.open_history[self.cur_step] * stock_bought
            self.stock_owned += stock_bought
        
        # Append new cash in hand to cash_in_hand_history
        self.cash_in_hand_history.append(self.cash_in_hand)
        
        # Append new stock quantity to stock_owned_history
        self.stock_owned_history.append(self.stock_owned)
        
        # Append action type taken to actions_taken
        self.actions_taken.append(action[0])
        
        # Append action amount to actions_amounts
        self.actions_amounts.append(action[1] / 10 if action[0] == 2 else (-action[1] / 10 if action[0] == 0 else 0))  # Negative values = Selling
    
    def render(self, mode="human"):
        if mode == "human":
            if self.cur_step == self.start_index + 1:
                # Render setup
                setup_graph(jupyter=IS_JUPYTER, render=True)
                
                # Set up axes
                self.fig, (self.net_worth_ax, self.stock_ax) = plt.subplots(2, sharex=True)  # 2 Horizontally stacked subplots with shared axes
                
                # Update axes titles
                self.net_worth_ax.title.set_text("Net Worth")
                self.stock_ax.title.set_text("Stock Price")
                
                # Set the scales
                self.net_worth_ax.set_xlim([self.start_index - 1, self.end_index])  # This is a known limit
                
                # Set up dummy variables
                self.net_worth_line, = self.net_worth_ax.plot(np.linspace(0, 0, self.cur_len), np.linspace(0, 0, self.cur_len), color="b")  # Create a line with the correct space
                self.net_worth_annotation = self.net_worth_ax.text(0, 0, "0", bbox=dict(boxstyle='round', fc='w', ec='k', lw=1))
                
                self.stock_line, = self.stock_ax.plot(np.linspace(0, 0, self.cur_len), np.linspace(0, 0, self.cur_len), color="r")
                self.stock_annotation = self.stock_ax.text(0, 0, "0", bbox=dict(boxstyle='round', fc='w', ec='k', lw=1))
                             
            # Update data of the net worth line
            self.net_worth_line.set_xdata(range(self.start_index, self.cur_step))
            self.net_worth_line.set_ydata(self.net_worths[:self.cur_step - self.start_index])
            
            # Update data of the stock line
            self.stock_line.set_xdata(range(self.start_index, self.cur_step))
            self.stock_line.set_ydata(self.close_history[self.start_index:self.cur_step])
            
            # Annotate the current net worth of the agent
            self.net_worth_annotation.set_text("{0:.2f}".format(self.net_worths[-1]))
            self.net_worth_annotation.set_x(self.cur_step)
            self.net_worth_annotation.set_y(self.net_worths[-1])
            
            # Annotate the current stock price
            self.stock_annotation.set_text("{0:.2f}".format(self.close_history[self.cur_step]))
            self.stock_annotation.set_x(self.cur_step)
            self.stock_annotation.set_y(self.close_history[self.cur_step])
            
            # Adjust the scale of the axes
            line_min_networth = min(self.net_worths)
            line_max_networth = max(self.net_worths)
            adjustment_networth = line_max_networth * 0.1
            self.net_worth_ax.set_ylim([line_min_networth - adjustment_networth, line_max_networth + adjustment_networth])
            
            line_min_stock = min(self.close_history[self.start_index:self.cur_step])
            line_max_stock = max(self.close_history[self.start_index:self.cur_step])
            adjustment_stock = line_max_stock * 0.1
            self.stock_ax.set_ylim([line_min_stock - adjustment_stock, line_max_stock + adjustment_stock])

            # Update canvas
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            
            if self.done is True:
                # Reset back to normal
                setup_graph(jupyter=IS_JUPYTER)
                
                # Redraw graph in enlarged form
                fig, (net_worth_ax, stock_ax, amount_ax) = plt.subplots(3, sharex=True)
                
                # Update axes titles
                net_worth_ax.title.set_text("Net Worth: {0:.2f}".format(self.net_worths[-1]))
                stock_ax.title.set_text("Stock Price: {0:.2f}".format(self.close_history[self.cur_step]))
                amount_ax.title.set_text("Amount Bought/Sold (-1 to 1)")
                
                # Set the scales
                net_worth_ax.set_xlim([self.start_index - 1, self.end_index])
                
                net_worth_ax.set_ylim([line_min_networth - adjustment_networth, line_max_networth + adjustment_networth])
                stock_ax.set_ylim([line_min_stock - adjustment_stock, line_max_stock + adjustment_stock])
                amount_ax.set_ylim([-1.1, 1.1])
                
                # Draw lines
                net_worth_ax.plot(range(self.start_index, self.end_index), self.net_worths[:self.cur_len], color="b", label="Net Worth")
                stock_ax.plot(range(self.start_index, self.end_index), self.close_history[self.start_index: self.end_index], color="r", label="Closing Price")
                
                # Process actions taken
                sell_only = [1 if x == 0 else 0 for x in self.actions_taken]
                buy_only = [1 if x == 2 else 0 for x in self.actions_taken]
                
                sell_actions = [x if x < 0 else None for x in self.actions_amounts]
                buy_actions = [x if x > 0 else None for x in self.actions_amounts]
                
                # Plot actions taken
                net_worth_ax.scatter(range(self.start_index, self.end_index), [sell_only[i] * self.net_worths[i] for i in range(self.cur_len)], label="Sell", color="red", marker="x")
                net_worth_ax.scatter(range(self.start_index, self.end_index), [buy_only[i] * self.net_worths[i] for i in range(self.cur_len)], label="Buy", color="green", marker="x")
                
                stock_ax.scatter(range(self.start_index, self.end_index), [sell_only[i - self.start_index] * self.close_history[i] for i in range(self.start_index, self.end_index)], label="Sell", color="red", marker="x")
                stock_ax.scatter(range(self.start_index, self.end_index), [buy_only[i - self.start_index] * self.close_history[i] for i in range(self.start_index, self.end_index)], label="Buy", color="green", marker="x")
                
                amount_ax.stem(range(self.start_index, self.end_index), sell_actions, "red", markerfmt="ro", label="Sell")
                amount_ax.stem(range(self.start_index, self.end_index), buy_actions, "green", markerfmt="go", label="Buy")
                
                # Legend
                net_worth_ax.legend(loc="best")
                stock_ax.legend(loc="best")
                amount_ax.legend(loc="best")
                plt.show()

print("Done!\n")
# # Run code per training stock
print("Running the agents...")

with open("outFile.txt", "w+") as outFile:
    for trainingStock in TRAINING_STOCKS:
        fullTrainPath = TRAINING_DIRECTORY + trainingStock + "_"
        trainingDF = prep_data(fullTrainPath)
        
        # # Training the Model
        # Before we train the model, we need to make a training environment for the model to train on:
        trainEnv = DummyVecEnv([lambda: TradingEnv(trainingDF, init_invest=INIT_INVEST, reward_function="Difference", is_serial=False)])

        # Let's now create a `A2C` model from the `stable-baselines` library:
        model = A2C(MlpLstmPolicy, trainEnv, verbose=1)

        # Now, let's train the A2C model!
        from time import time
        print("Training model...")
        startTime = time()
        
        model.learn(total_timesteps=NO_ITERATIONS)
        
        print("Done! Took", time() - startTime, "seconds to run", NO_ITERATIONS, "iterations.")

        # Now, let's see how well the model performs on the training data:
        # A2C algorithm
        a2cEnv = TradingEnv(trainingDF, init_invest=INIT_INVEST, is_serial=True)  # For training purposes
        done = False
        state = a2cEnv.reset()

        print("Generating training score...")
        while not done:
            action, _ = model.predict([state])
            state, _, done, _ = a2cEnv.step(action[0])

        a2cScore = a2cEnv.get_val()  # The model's score

        # print("-----> A2C Score (TRAINING: {}): {:.3f}".format(trainingStock, a2cScore))
        outFile.write("----- {} -----\nA2C Score (TRAINING): {:.3f}\n".format(trainingStock, a2cScore))


        # # Testing the Model
        # Let's prep the data for each of our testing stocks and use them to test our model:
        for testingStock in TESTING_STOCKS:
            fullTestPath = TESTING_DIRECTORY + testingStock + "_"

            testingDF = prep_data(fullTestPath)

            # Now, run the A2C algorithm for the testing data:
            # A2C algorithm
            a2cEnv = TradingEnv(testingDF, init_invest=INIT_INVEST, is_serial=True)  # For training purposes
            done = False
            state = a2cEnv.reset()

            print("Generating testing score for {}...".format(testingStock))
            while not done:
                action, _ = model.predict([state])
                state, _, done, _ = a2cEnv.step(action[0])

            a2cScore = a2cEnv.get_val()  # The model's score

            # print("-----> A2C Score (TESTING: {}): {:.3f}".format(testingStock, a2cScore))
            outFile.write("A2C Score (TESTING: {}): {:.3f}\n".format(testingStock, a2cScore))

        print("\n" + "-" * 50)
        outFile.write("\n")

    print("Done!")

    outFile.close()
