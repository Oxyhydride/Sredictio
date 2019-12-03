"""
TradingEnv.py
Version 1.18.0

Created on 2019-06-03
Updated on 2019-12-03

Copyright Ryan Kan 2019

Description: The trading environment for the A2C agent.
"""
# IMPORTS
import gym
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from utils.graphUtils import setup_graph


# CLASSES
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

    def __init__(self, data_df: pd.DataFrame, init_invest: float = 25.0, reward_len: int = 32,
                 look_back_window_size: int = 5, is_serial: bool = False, max_trading_session: int = 100,
                 seed: int = None):
        """
        Initialization function for the trading environment.

        Keyword arguments:
        - data_df, pd.DataFrame: A pandas dataframe containing all the data.
        - init_invest, float: Starting cash (Default = 5.0)
        - reward_len, int: No of entries to consider when calculating reward (Default = 32)
        - look_back_window_size, int: How many entries can the agent look back? (Default = 5)
        - is_serial, bool: Is the environment serial (i.e. following a strict sequence)? (Default = False)
        - max_trading_session, int: How many entries, maximally, can the environment take as data? (Default = 100)
        - seed, int: The seed for the environment. (Default = None)
        """
        # Convert given data into variables
        self.data_df = data_df  # This is the dataframe where all the data is stored
        self.init_invest = init_invest  # Initial investment value
        self.reward_len = reward_len  # Length of reward consideration array
        self.look_back_window = look_back_window_size  # Size of the look_back window
        self.is_serial = is_serial  # Is the environment serial?
        self.max_trading_session = max_trading_session  # The maximum length for a trading session
        self.env_seed = seed  # The random seed

        # Seed environment
        self.seed(seed=self.env_seed)

        # Create the histories
        self.full_data_arr = self.data_df.values  # All the values, converted into a np.array

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
        self.action_space = gym.spaces.MultiDiscrete([3, 10])

        # Observation space: give estimates in order to sample and build scalar
        stock_max = max(max(self.open_history),
                        max(max(self.high_history), max(max(self.low_history), max(self.close_history))))

        self.observation_space = gym.spaces.Box(low=-1, high=init_invest * 3 * (1 + (1 // stock_max)),
                                                shape=(8, self.look_back_window), dtype=np.float32)

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

    def seed(self, seed=None):
        """
        Seeds the environment.

        Keyword arguments:
        - seed, int: Seed of the environment. (Default = None)
        """
        np.random.seed(seed)

    def generate_data_arr(self, serial):
        """
        Generates the new data_arr.

        Keyword arguments:
        - serial, bool: Is the environment serial (i.e. following a strict sequence)?
        """

        if serial:  # No need to randomise the start and end positions
            # Use all of the data_df values
            self.start_index = self.look_back_window
            self.end_index = self.total_len - 1

            self.cur_len = self.end_index - self.start_index

        else:
            # Generate a random range for training
            local_max_trading_session = min(self.max_trading_session, self.total_len)  # We don't want it to exceed

            self.cur_len = np.random.randint(self.look_back_window,
                                             local_max_trading_session) - self.look_back_window - 1
            self.start_index = np.random.randint(self.look_back_window, self.total_len - self.cur_len)
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

        self.net_worths = [self.init_invest] * self.look_back_window
        self.stock_owned_history = [0] * self.look_back_window
        self.cash_in_hand_history = [self.init_invest] * self.look_back_window

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

    def step(self, action: list):
        """
        Moves forward one step in time.

        Keyword arguments:
        - action, list: Action-Amount pair, representing the action to take and the amount bought/sold.

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
        
        return np.array([self.stock_owned_history[-self.look_back_window:],
                         self.open_history[self.cur_step - self.look_back_window: self.cur_step],
                         self.high_history[self.cur_step - self.look_back_window: self.cur_step],
                         self.low_history[self.cur_step - self.look_back_window: self.cur_step],
                         self.close_history[self.cur_step - self.look_back_window: self.cur_step],
                         self.sentiment_history[self.cur_step - self.look_back_window: self.cur_step],
                         self.cash_in_hand_history[-self.look_back_window:],
                         self.net_worths[-self.look_back_window:]])

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
        self.done = (self.cur_step >= self.end_index)  # Only will be done if the current step is the ending step

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
            stock_bought = int((self.cash_in_hand / self.open_history[
                self.cur_step]) * action_amount)  # We won't want partial stocks, now do we?

            self.cash_in_hand -= self.open_history[self.cur_step] * stock_bought
            self.stock_owned += stock_bought

        # Append new cash in hand to cash_in_hand_history
        self.cash_in_hand_history.append(self.cash_in_hand)

        # Append new stock quantity to stock_owned_history
        self.stock_owned_history.append(self.stock_owned)

        # Append action type taken to actions_taken
        self.actions_taken.append(action[0])

        # Append action amount to actions_amounts
        self.actions_amounts.append(action[1] / 10 if action[0] == 2 else (
            -action[1] / 10 if action[0] == 0 else 0))  # Negative values = Selling

    def render(self, mode="human"):
        if mode == "human":
            if self.cur_step == self.start_index + 1:
                # Render setup
                setup_graph()

                # Set up axes
                self.fig, (self.net_worth_ax, self.stock_ax) = plt.subplots(2, sharex="all")

                # Update axes titles
                self.net_worth_ax.title.set_text("Net Worth")
                self.stock_ax.title.set_text("Stock Price")

                # Set the scales
                self.net_worth_ax.set_xlim([self.start_index - 1, self.end_index])  # This is a known limit

                # Set up dummy variables
                self.net_worth_line, = self.net_worth_ax.plot(np.linspace(0, 0, self.cur_len),
                                                              np.linspace(0, 0, self.cur_len),
                                                              color="b")  # Create a line with the correct space
                self.net_worth_annotation = self.net_worth_ax.text(0, 0, "0",
                                                                   bbox=dict(boxstyle='round', fc='w', ec='k', lw=1))

                self.stock_line, = self.stock_ax.plot(np.linspace(0, 0, self.cur_len), np.linspace(0, 0, self.cur_len),
                                                      color="r")
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
            self.net_worth_ax.set_ylim(
                [line_min_networth - adjustment_networth, line_max_networth + adjustment_networth])

            line_min_stock = min(self.close_history[self.start_index:self.cur_step])
            line_max_stock = max(self.close_history[self.start_index:self.cur_step])
            adjustment_stock = line_max_stock * 0.1
            self.stock_ax.set_ylim([line_min_stock - adjustment_stock, line_max_stock + adjustment_stock])

            # Update canvas
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            if self.done is True:
                # Reset back to normal
                setup_graph()

                # Redraw graph in enlarged form
                fig, (net_worth_ax, stock_ax, amount_ax) = plt.subplots(3, sharex="all")

                # Update axes titles
                net_worth_ax.title.set_text("Net Worth: {0:.2f}".format(self.net_worths[-1]))
                stock_ax.title.set_text("Stock Price: {0:.2f}".format(self.close_history[self.cur_step]))
                amount_ax.title.set_text("Amount Bought/Sold (-1 to 1)")

                # Set the scales
                net_worth_ax.set_xlim([self.start_index - 1, self.end_index])

                net_worth_ax.set_ylim(
                    [line_min_networth - adjustment_networth, line_max_networth + adjustment_networth])
                stock_ax.set_ylim([line_min_stock - adjustment_stock, line_max_stock + adjustment_stock])
                amount_ax.set_ylim([-1.1, 1.1])

                # Draw lines
                net_worth_ax.plot(range(self.start_index, self.end_index), self.net_worths[:self.cur_len], color="b",
                                  label="Net Worth")
                stock_ax.plot(range(self.start_index, self.end_index),
                              self.close_history[self.start_index: self.end_index], color="r", label="Closing Price")

                # Process actions taken
                sell_only = [1 if x == 0 else 0 for x in self.actions_taken]
                buy_only = [1 if x == 2 else 0 for x in self.actions_taken]

                sell_actions = [x if x < 0 else None for x in self.actions_amounts]
                buy_actions = [x if x > 0 else None for x in self.actions_amounts]

                # Plot actions taken
                net_worth_ax.scatter(range(self.start_index, self.end_index),
                                     [sell_only[i] * self.net_worths[i] for i in range(self.cur_len)], label="Sell",
                                     color="red", marker="x")
                net_worth_ax.scatter(range(self.start_index, self.end_index),
                                     [buy_only[i] * self.net_worths[i] for i in range(self.cur_len)], label="Buy",
                                     color="green", marker="x")

                stock_ax.scatter(range(self.start_index, self.end_index),
                                 [sell_only[i - self.start_index] * self.close_history[i] for i in
                                  range(self.start_index, self.end_index)], label="Sell", color="red", marker="x")
                stock_ax.scatter(range(self.start_index, self.end_index),
                                 [buy_only[i - self.start_index] * self.close_history[i] for i in
                                  range(self.start_index, self.end_index)], label="Buy", color="green", marker="x")

                amount_ax.stem(range(self.start_index, self.end_index), sell_actions, "red", markerfmt="ro",
                               label="Sell")
                amount_ax.stem(range(self.start_index, self.end_index), buy_actions, "green", markerfmt="go",
                               label="Buy")

                # Legend
                net_worth_ax.legend(loc="best")
                stock_ax.legend(loc="best")
                amount_ax.legend(loc="best")
                plt.show()
