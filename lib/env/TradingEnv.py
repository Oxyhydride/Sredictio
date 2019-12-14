"""
TradingEnv.py

Created on 2019-06-03
Updated on 2019-12-14

Copyright Ryan Kan 2019

Description: The trading environment for the A2C agent.
"""
# IMPORTS
import gym
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import preprocessing

from lib.utils.trainingDataUtils import add_technical_indicators
from lib.utils.graphUtils import setup_graph


# CLASSES
class TradingEnv(gym.Env):
    """
    The trading environment.

    Observation State: A 44 * look_back_window array of technical indicators and values

    Action Space:
    - 3 Actions: Sell [0], Hold [1], Buy [2]
    - 10 Amounts: 1/10 of total, 2/10 of total, 3/10 of total etc.
    """
    metadata = {'render.modes': ['human', 'system', 'none']}
    viewer = None

    def __init__(self, data_df: pd.DataFrame, init_buyable_stocks: float = 2.5, reward_len: int = 32,
                 look_back_window_size: int = 5, is_serial: bool = False, max_trading_session: int = 100):
        """
        Initialization function for the trading environment.

        Keyword arguments:
        - data_df, pd.DataFrame: A pandas dataframe containing all the data.
        - init_buyable_stocks, float: The number of stocks which the agent can buy on its first step (Default = 2.5)
        - reward_len, int: No of entries to consider when calculating reward (Default = 32)
        - look_back_window_size, int: How many entries can the agent look back? (Default = 5)
        - is_serial, bool: Is the environment serial (i.e. following a strict sequence)? (Default = False)
        - max_trading_session, int: How many entries, maximally, can the environment take as data? (Default = 100)
        """
        # Checks
        assert init_buyable_stocks > 1, "init_buyable_stocks has to be greater than 1."

        # Convert given data into variables
        self.full_data_df = data_df  # This is the dataframe where all the data is stored
        self.init_buyable_stocks = init_buyable_stocks  # Initial number of stocks which the agent can buy
        self.reward_len = reward_len  # Length of reward consideration array
        self.look_back_window = look_back_window_size  # Size of the look_back window
        self.is_serial = is_serial  # Is the environment serial?
        self.max_trading_session = max_trading_session  # The maximum length for a trading session

        # Add technical indicators to self.full_data_df
        self.full_data_df = add_technical_indicators(self.full_data_df)

        # Create data_df
        self.total_len = len(self.full_data_df)
        self.cur_len = None

        self.start_index = None
        self.end_index = None

        self.data_df = None
        self.generate_data_df(self.is_serial)

        # Instance attributes
        self.cur_step = self.start_index
        self.init_invest = self.init_buyable_stocks * self.data_df["Close"].iloc[0]  # First element of the dataframe
        self.stock_owned = None
        self.cash_in_hand = None
        self.done = False
        self.actions_taken = []
        self.actions_amounts = []

        # Observation space variables
        self.net_worths = None
        self.stock_owned_history = None

        # Action space
        self.action_space = gym.spaces.MultiDiscrete([3, 10])

        # Observation space
        self.observation_space = gym.spaces.Box(low=0, high=1,
                                                shape=(len(self.full_data_df.columns) + 1, self.look_back_window),
                                                dtype=np.float32)

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

    def generate_data_df(self, serial: bool):
        """
        Generates the new data_df.

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

            self.cur_len = np.random.randint(self.look_back_window + 1,
                                             local_max_trading_session) - self.look_back_window
            self.start_index = np.random.randint(self.look_back_window, self.total_len - self.cur_len)
            self.end_index = self.start_index + self.cur_len

        self.data_df = self.full_data_df[self.start_index: self.end_index]

    def reset(self, print_init_invest_amount: bool = False):
        """
        Resets the environment.

        Keyword Arguments:
        - print_init_invest_amount, bool: Should this function print the initial investment amount?
        """
        # Create new active array
        self.generate_data_df(self.is_serial)

        # Reset all needed variables
        self.cur_step = self.start_index  # Step reset to 0
        self.stock_owned = 0
        self.init_invest = self.init_buyable_stocks * self.data_df["Close"].iloc[0]
        self.cash_in_hand = self.init_invest
        self.actions_taken = []
        self.actions_amounts = []
        self.net_worths = [self.init_invest] * self.look_back_window
        self.stock_owned_history = [0] * self.look_back_window

        # Rendering variables
        self.fig = None
        self.net_worth_ax = None
        self.net_worth_annotation = None
        self.net_worth_line = None
        self.stock_ax = None
        self.stock_line = None
        self.stock_annotation = None

        # Clear figure
        plt.clf()

        # Print initial investment amount
        if print_init_invest_amount:
            print(f"The initial investment amount is ${self.init_invest:.2f}")

        # Return observation list
        return self.get_obs()

    def step(self, action: tuple):
        """
        Moves forward one step in time.

        Keyword arguments:
        - action, tuple in the form (int, int): Action-Amount pair, representing the action to take and the amount
                                                bought/sold.

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

    def trade(self, action: tuple):
        """
        A function to help to "trade" the stocks.

        Keyword arguments:
        - action, tuple in the form (int, int): Action-Amount pair.
        """
        # Check if done
        self.done = (self.cur_step >= self.end_index)  # Only will be done if the current step is the ending step

        # Split Action type and Amount
        action_type = action[0]  # Sell: 0, Hold: 1, Buy: 2
        action_amount = (action[1] + 1) / 10  # Representing 1/10, 2/10, 3/10 etc.

        if action_type == 0:  # Sell
            stock_sold = int(self.stock_owned * action_amount)  # We won't want partial stocks, now do we?

            # Handle exchange of things
            self.cash_in_hand += self.full_data_df["Close"][self.cur_step] * stock_sold
            self.stock_owned -= stock_sold

        elif action_type == 1:  # Hold
            # Nothing to do here, moving on.
            pass

        elif action_type == 2:  # Buy
            stock_bought = int((self.cash_in_hand / self.full_data_df["Close"][self.cur_step]) * action_amount)

            # Handle the exchange
            self.cash_in_hand -= self.full_data_df["Close"][self.cur_step] * stock_bought
            self.stock_owned += stock_bought

        # Append new stock quantity to stock_owned_history
        self.stock_owned_history.append(self.stock_owned)

        # Append action type taken to actions_taken
        self.actions_taken.append(action[0])

        # Append action amount to actions_amounts
        # NOTE: Negative values = Sell
        self.actions_amounts.append(
            (action[1] + 1) / 10 if action[0] == 2 else (-(action[1] + 1) / 10 if action[0] == 0 else 0))

    def get_val(self):
        """
        Calculates the current portfolio value of the Agent.

        Returns:
        - Portfolio value (Float)
        """
        return self.stock_owned * self.full_data_df["Close"][self.cur_step] + self.cash_in_hand

    def gen_reward(self):
        """
        Generates the reward by taking the difference between the current net worth and the previous net worth.
        i.e. Reward = CurrentNetWorth - PreviousNetWorth

        Returns:
        - Reward (Float)
        """
        reward = self.net_worths[-1] - self.net_worths[-2]

        return reward

    def get_obs(self):
        """
        Processes and returns the observation list.

        Returns:
        - Observation list (List)
        """
        # Add dataframe values
        obs = self.full_data_df[self.cur_step - self.look_back_window: self.cur_step].transpose().values.tolist()

        # Add the stock_owned_history to the observation list
        obs.append(self.stock_owned_history[-self.look_back_window:])

        # Convert obs to np.ndarray
        obs = np.array(obs)

        # Normalise values
        min_max_scaler = preprocessing.MinMaxScaler()
        obs = min_max_scaler.fit_transform(obs.astype("float32"))

        # Return observation list
        return obs

    def render(self, mode: str = "human"):
        """
        Renders the trading environment.

        Keyword arguments:
        - mode, str: The mode to render the environment in. (Default = "human")
        """
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
            self.stock_line.set_ydata(self.full_data_df["Close"][self.start_index:self.cur_step])

            # Annotate the current net worth of the agent
            self.net_worth_annotation.set_text("{0:.2f}".format(self.net_worths[-1]))
            self.net_worth_annotation.set_x(self.cur_step)
            self.net_worth_annotation.set_y(self.net_worths[-1])

            # Annotate the current stock price
            self.stock_annotation.set_text("{0:.2f}".format(self.full_data_df["Close"][self.cur_step]))
            self.stock_annotation.set_x(self.cur_step)
            self.stock_annotation.set_y(self.full_data_df["Close"][self.cur_step])

            # Adjust the scale of the axes
            line_min_networth = min(self.net_worths)
            line_max_networth = max(self.net_worths)
            adjustment_networth = line_max_networth * 0.1
            self.net_worth_ax.set_ylim(
                [line_min_networth - adjustment_networth, line_max_networth + adjustment_networth])

            line_min_stock = min(self.full_data_df["Close"][self.start_index:self.cur_step])
            line_max_stock = max(self.full_data_df["Close"][self.start_index:self.cur_step])
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
                stock_ax.title.set_text("Stock Price: {0:.2f}".format(self.full_data_df["Close"][self.cur_step]))
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
                              self.full_data_df["Close"][self.start_index: self.end_index], color="r",
                              label="Closing Price")

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
                                 [sell_only[i - self.start_index] * self.full_data_df["Close"][i] for i in
                                  range(self.start_index, self.end_index)], label="Sell", color="red", marker="x")
                stock_ax.scatter(range(self.start_index, self.end_index),
                                 [buy_only[i - self.start_index] * self.full_data_df["Close"][i] for i in
                                  range(self.start_index, self.end_index)], label="Buy", color="green", marker="x")

                amount_ax.stem(range(self.start_index, self.end_index), sell_actions, "red", markerfmt="ro",
                               label="Sell")
                amount_ax.stem(range(self.start_index, self.end_index), buy_actions, "green", markerfmt="go",
                               label="Buy")

                # Legend
                net_worth_ax.legend(loc="best")
                stock_ax.legend(loc="best")
                amount_ax.legend(loc="best")

                # Show figure
                plt.show()


# DEBUGGING CODE
if __name__ == "__main__":
    from lib.utils.trainingDataUtils import prep_data

    # Prepare dataframe
    debugDF = prep_data("../trainingData/", "BA")  # Prepare boeing data

    # Prepare environment
    debugEnv = TradingEnv(debugDF, is_serial=True)

    # Reset environment
    debugEnv.reset()

    # Increment step
    debugEnv.step((2, 1))  # Buy with 1/10

    # Print data_df
    print(debugEnv.data_df)

    # Get observation list
    print(debugEnv.get_obs())
