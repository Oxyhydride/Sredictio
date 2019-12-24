"""
TradingEnv.py

Created on 2019-06-03
Updated on 2019-12-24

Copyright Ryan Kan 2019

Description: The trading environment for the A2C agent.
"""
# IMPORTS
import gym
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import preprocessing

from lib.utils.dataUtils import add_technical_indicators
from lib.utils.graphingUtils import setup_graph


# CLASSES
class TradingEnv(gym.Env):
    """
    The trading environment for the A2C agent.

    Observation State: A `len(self.full_data_df.columns) + 1` * `look_back_window array` of technical indicators
                       and values. This would usually be a `np.ndarray`.

    Action Space: A np.ndarray with the shape (3, 5).
                  The action space consists of the following:
                  - 3 Actions: Sell [0], Hold [1], Buy [2]
                  - 5 Amounts: 1/5 of total, 2/5 of total, 3/5 of total etc.
    """

    def __init__(self, data_df, init_buyable_stocks=2.5, lookback_window_size=5, is_serial=False,
                 max_trading_session=100):
        """
        Initialization method for the trading environment.

        Args:
            data_df (pd.DataFrame): A pandas dataframe containing all the environment's data.

                                    This environment would usually contain the OHLCV data, the sentiment data
                                    and the technical indicator values.

            init_buyable_stocks (float): The number of stocks that the agent can buy on the first step.
                                         (Default = 2.5)

                                         For example, if `init_buyable_stocks = 3` and the closing price for
                                         the first day is $100, then the agent will have $300 on the first
                                         day.

            lookback_window_size (int): How many entries can the agent look back when considering its next
                                        move? (Default = 5)

                                        For example, if the `lookback_window_size` is set to 3, then the agent
                                        can consult the past 3 days' data to decide its action on the current
                                        day.

                                        It will come as no surprise that as `lookback_window_size` increases,
                                        the time needed to train the model will also increase.

            is_serial (bool): Is the environment serial (i.e. following a strict sequence)? (Default = False)

                              To understand this, a serial environment will follow a strict sequence. For
                              example, if the list [1, 2, 3, 4, 5] is considered to be "serial", then ALL
                              the elements in that list would be used for training. In addition, the
                              order in which the numbers would appear would be the same: from smallest to
                              largest. That means that if [1, 2, 3, 4, 5] is "serial", then 2 will come
                              after 1, and 3 will come after 2. This will continue until 5 is reached.

                              In a non-serial environment, two indices, i and j, are selected at random
                              where 0 <= i < j < len(arr). Then, only the elements with an index which
                              falls between i and j (i.e. for an element with index X, i <= X <= j) will
                              be selected. Using the same list [1, 2, 3, 4, 5] as before, any sublist can
                              be selected (e.g. [1, 2, 3], [2], [3, 4, 5], [1, 2, 3, 4] etc).

                              A serial environment would usually be used during TESTING. A non-serial
                              environment would usually be used for TRAINING. This is because there are
                              more possible "types" of "training sets" in a non-serial environment than a
                              serial environment.

            max_trading_session (int): How many entries, maximally, can the environment take as data?
                                       (Default = 100)

                                       In a non-serial environment, following the above analogy, the
                                       `max_trading_session` would be the UPPER BOUND of the value of j.
                                       I.E. i < j <= `max_trading_session`.

        Raises:
            AssertionError: If init_buyable_stocks < 1.

        """

        # Checks
        assert init_buyable_stocks > 1, "The value of `init_buyable_stocks` has to be greater than 1."

        # Convert given data into variables
        self.full_data_df = data_df  # Dataframe where all the data is stored
        self.init_buyable_stocks = init_buyable_stocks  # Initial number of stocks which the agent can buy
        self.lookback_window = lookback_window_size
        self.is_serial = is_serial  # Whether the environment is serial or not
        self.max_trading_session = max_trading_session  # The maximum length for a trading session

        # Add technical indicators to `full_data_df`
        self.full_data_df = add_technical_indicators(self.full_data_df)

        # Create a scaled copy of `full_data_df`
        full_data_df_values = self.full_data_df.values
        full_data_df_columns = self.full_data_df.columns

        self.min_max_scaler = preprocessing.MinMaxScaler()
        scaled_values = self.min_max_scaler.fit_transform(full_data_df_values)

        self.scaled_full_data_df = pd.DataFrame(scaled_values, columns=full_data_df_columns)

        # Create the current iteration's dataframe, also known as `data_df`
        self.full_data_df_len = len(self.full_data_df)
        self.data_df_len = None

        self.df_start_index = None
        self.df_end_index = None

        self.data_df = None
        self.generate_data_df(self.is_serial)

        # Other variables
        self.cur_step = self.df_start_index
        self.init_invest = self.init_buyable_stocks * self.data_df["Close"].iloc[0]  # First element of the dataframe
        self.stock_owned = None
        self.cash_in_hand = None
        self.done = False
        self.actions_taken = []
        self.actions_amount = []

        # Reward function variables
        self.net_worths = None

        # Observation space variables
        self.stock_owned_history = None

        # Define the action space
        self.action_space = gym.spaces.MultiDiscrete([3, 5])  # 3 actions, with 5 amounts

        # Define the observation space
        self.observation_space = gym.spaces.Box(low=0, high=1,
                                                shape=(len(self.full_data_df.columns), self.lookback_window),
                                                # shape=(len(self.full_data_df.columns) + 1, self.lookback_window),
                                                dtype=np.float32)

        # Rendering variables
        self.fig = None
        self.net_worth_ax = None
        self.net_worth_annotation = None
        self.net_worth_line = None
        self.stock_ax = None
        self.stock_line = None
        self.stock_annotation = None

        # Reset the environment
        self.reset()

    def generate_data_df(self, serial):
        """
        Generates the new `data_df` for the current iteration.

        Args:
            serial (bool): Whether the environment is serial or not. If True, the environment is serial.
                           If False, the environment is not serial.

        """

        if serial:  # No need to randomise the start and end positions
            # Use all of the data_df values
            self.df_start_index = self.lookback_window
            self.df_end_index = self.full_data_df_len - 1

            self.data_df_len = self.df_end_index - self.df_start_index

        else:
            # Generate a random range for training
            local_max_trading_session = min(self.max_trading_session, self.full_data_df_len)

            self.data_df_len = np.random.randint(self.lookback_window + 1,
                                                 local_max_trading_session) - self.lookback_window
            self.df_start_index = np.random.randint(self.lookback_window, self.full_data_df_len - self.data_df_len)
            self.df_end_index = self.df_start_index + self.data_df_len

        self.data_df = self.full_data_df[self.df_start_index: self.df_end_index]

    def reset(self, print_init_invest_amount=False):
        """
        Resets the environment.

        Args:
            print_init_invest_amount (bool): Should this method print the initial investment amount
                                             once run? (Default = False)

        Returns:
            np.ndarray: The observation array of the environment.

        """

        # Create new `data_df` for this iteration
        self.generate_data_df(self.is_serial)

        # Reset all needed variables
        self.cur_step = self.df_start_index  # Step reset to the new starting index
        self.stock_owned = 0  # Obviously, remove all stocks from the agent
        self.init_invest = self.init_buyable_stocks * self.data_df["Close"].iloc[0]
        self.cash_in_hand = self.init_invest  # Initial investment amount is what we started with

        # Reset lists
        self.actions_taken = []  # No actions taken
        self.actions_amount = []  # No amounts recorded
        self.net_worths = [self.init_invest] * self.lookback_window
        self.stock_owned_history = [0] * self.lookback_window

        # Reset rendering variables
        self.fig = None
        self.net_worth_ax = None
        self.net_worth_annotation = None
        self.net_worth_line = None
        self.stock_ax = None
        self.stock_line = None
        self.stock_annotation = None

        # Clear current figure
        plt.clf()

        # Print the initial investment amount (if needed)
        if print_init_invest_amount:
            print(f"The initial investment amount is ${self.init_invest:.2f}")

        # Return the current state's observation array
        return self.get_obs()

    def step(self, action):
        """
        Makes the environment move forward one step in time.

        Args:
            action (Tuple[int, int]): Action-Amount pair, representing the action that the agent
                                      will take and the amount of stock sold/amount of money used.

                                      For example:
                                      - If `action = (0, 2)`, then the agent will SELL 3/5 of its
                                        stocks.
                                      - If `action = (1, 3)`, then the agent will HOLD.
                                      - If `action = (2, 4)`, then the agent will BUY stocks using
                                        5/5 of its cash

                                      In general, for an `action = (P, Q)`, where P and Q are natural
                                      numbers:
                                      - `P` is the "action type".
                                        * If `P = 0` then the action is `SELL`.
                                        * If `P = 1` then the action is `HOLD`.
                                        * If `P = 2` then the action is `BUY`.

                                      - `Q` is the "action amount".
                                        * This is the amount of stock to be sold OR the amount of cash
                                          the agent is willing to spend on stocks.
                                        * For any `Q`, the actual "action amount" is one more than `Q`.
                                          That is, `"action amount" = Q + 1`. This is because the values
                                          of Q can range from 0 to 4, and adding 1 would ensure that all
                                          numbers from 1 to 5 are covered.

        Returns:
            np.ndarray: The observation array.
            float: The reward for taking that `action`.
            bool: A value which says whether the environment has completed all its steps (i.e. the value
                  indicates whether the environment is "done" or not)
            dict: A dictionary with useful information.
                  This dictionary currently only contains the `cur_val` variable of the environment.

        """

        # Move forward one day in time
        self.cur_step += 1
        self.update_stocks(action)

        # What's changed?
        self.net_worths.append(self.get_val())  # `self.get_val()` is the current net worth

        # Generate current iteration's reward
        reward = self.gen_reward()

        # Update the info
        info = {'cur_val': self.net_worths[-1]}

        return self.get_obs(), reward, self.done, info

    def update_stocks(self, action):
        """
        A method to help the agent to manage the stocks.

        Args:
            action (Tuple[int, int]): Action-Amount pair, representing the action that the agent
                                      will take and the amount of stock sold/amount of money used.

        """
        # Check if environment is done
        self.done = (self.cur_step >= self.df_end_index)

        # Split `action` into the "Action Type" and "Action Amount"
        action_type = action[0]  # Sell: 0, Hold: 1, Buy: 2
        action_amount = (action[1] + 1) / 5  # Representing 1/5, 2/5, 3/5 etc. Add 1 as action amounts are from 0 to 4

        if action_type == 0:  # Sell
            stock_sold = int(self.stock_owned * action_amount)  # We don't want partial stocks

            # Handle addition of money and the subtraction of stocks
            self.cash_in_hand += self.full_data_df["Close"][self.cur_step] * stock_sold
            self.stock_owned -= stock_sold

        elif action_type == 1:  # Hold
            pass

        elif action_type == 2:  # Buy
            stock_bought = int((self.cash_in_hand / self.full_data_df["Close"][self.cur_step]) * action_amount)

            # Handle addition of stocks and the subtraction of money
            self.cash_in_hand -= self.full_data_df["Close"][self.cur_step] * stock_bought
            self.stock_owned += stock_bought

        # Append new stock quantity to `stock_owned_history`
        self.stock_owned_history.append(self.stock_owned)

        # Append "Action Type" to `actions_taken`
        self.actions_taken.append(action[0])

        # Append "Action Amount" to `actions_amount`
        # NOTE: Negative values = Sell
        if action_type == 0:  # Sell
            self.actions_amount.append(-(action[1] + 1) / 5)

        elif action_type == 1:  # Hold
            self.actions_amount.append(0)

        else:  # Buy
            self.actions_amount.append((action[1] + 1) / 5)

    def get_val(self):
        """
        Calculates the current portfolio value of the agent.

        Returns:
            float: Portfolio value of the agent at this current step

        """

        return self.stock_owned * self.full_data_df["Close"][self.cur_step] + self.cash_in_hand

    def gen_reward(self):
        """
        Generates the reward for the current step.

        The reward function is known as "DIFFERENCE". It is calculated by taking the difference
        between the current net worth and the previous net worth.
        (i.e. Reward = Current Net Worth - Previous Net Worth)

        Returns:
            float: The reward for the current step.
        """

        reward = self.net_worths[-1] - self.net_worths[-2]

        return reward

    def get_obs(self):
        """
        Processes and returns the observation array.

        Returns:
            np.ndarray: The observation array for the current step.

        """

        # Add dataframe values
        obs = self.scaled_full_data_df[self.cur_step - self.lookback_window: self.cur_step].transpose().values.tolist()

        # Add the stock_owned_history to the observation list
        # obs.append(self.stock_owned_history[-self.lookback_window:])

        # Convert obs to np.ndarray
        obs = np.array(obs)

        # Return observation list
        return obs

    def render(self, mode="human", fig_res=(600, 480), dpi=60):
        """
        Renders the trading environment.

        Args:
            mode (str): The mode to render the environment in. (Default = "human")

                        By default, there are three modes: "human", "system" and "none".

                        If the mode is "human", then the environment's rendering function will run
                        and will display the current net worth and the current stock price.

                        If not, then the environment will not render anything.

            fig_res (Tuple[int, int]): The resolution of the plotted graph. (Default = (600, 480))

                                       The `fig_res` will be a tuple in the form (W, H), where W is
                                       the width while H is the height.

            dpi (int): The DPI (aka Dots Per Inch) for the plot. (Default = 40)

        """

        if mode == "human":
            # Calculate `fig_size`
            fig_size = (fig_res[0] / dpi, fig_res[1] / dpi)

            # Check if first step
            if self.cur_step == self.df_start_index + 1:
                # Render setup
                setup_graph()

                # Set up axes
                self.fig, (self.net_worth_ax, self.stock_ax) = plt.subplots(2, sharex="all", figsize=fig_size, dpi=dpi)

                # Update axes titles
                self.net_worth_ax.title.set_text("Agent's Net Worth")
                self.stock_ax.title.set_text("Stock Price")

                # Set the scales
                self.net_worth_ax.set_xlim([self.df_start_index - 1, self.df_end_index])  # This is a known limit

                # Set up dummy variables
                (self.net_worth_line,) = self.net_worth_ax.plot(np.linspace(0, 0, self.data_df_len),
                                                                np.linspace(0, 0, self.data_df_len), color="b")
                self.net_worth_annotation = self.net_worth_ax.text(0, 0, "0",
                                                                   bbox=dict(boxstyle='round', fc='w', ec='k', lw=1))

                self.stock_line, = self.stock_ax.plot(np.linspace(0, 0, self.data_df_len),
                                                      np.linspace(0, 0, self.data_df_len), color="r")
                self.stock_annotation = self.stock_ax.text(0, 0, "0", bbox=dict(boxstyle='round', fc='w', ec='k', lw=1))

            # Update data of the net worth line
            self.net_worth_line.set_xdata(range(self.df_start_index, self.cur_step))
            self.net_worth_line.set_ydata(self.net_worths[:self.cur_step - self.df_start_index])

            # Update data of the stock line
            self.stock_line.set_xdata(range(self.df_start_index, self.cur_step))
            self.stock_line.set_ydata(self.full_data_df["Close"][self.df_start_index:self.cur_step])

            # Annotate the current net worth of the agent
            self.net_worth_annotation.set_text("${0:.2f}".format(self.net_worths[-1]))
            self.net_worth_annotation.set_x(self.cur_step)
            self.net_worth_annotation.set_y(self.net_worths[-1])

            # Annotate the current stock price
            self.stock_annotation.set_text("${0:.2f}".format(self.full_data_df["Close"][self.cur_step]))
            self.stock_annotation.set_x(self.cur_step)
            self.stock_annotation.set_y(self.full_data_df["Close"][self.cur_step])

            # Adjust the scales of the axes
            line_min_networth = min(self.net_worths)
            line_max_networth = max(self.net_worths)
            adjustment_networth = line_max_networth * 0.1
            self.net_worth_ax.set_ylim(
                [line_min_networth - adjustment_networth, line_max_networth + adjustment_networth])

            line_min_stock = min(self.full_data_df["Close"][self.df_start_index:self.cur_step])
            line_max_stock = max(self.full_data_df["Close"][self.df_start_index:self.cur_step])
            adjustment_stock = line_max_stock * 0.1
            self.stock_ax.set_ylim([line_min_stock - adjustment_stock, line_max_stock + adjustment_stock])

            # Update the canvas
            plt.pause(1e-5)  # Wait for a while for it to load

            if self.done is True:
                # Reset the graph settings
                setup_graph()
                plt.close("all")  # Close all active windows

                # Redraw graph in an enlarged form
                fig, (net_worth_ax, stock_ax, amount_ax) = plt.subplots(3, sharex="all")

                # Update the axes' titles
                net_worth_ax.title.set_text("Net Worth: ${0:.2f}".format(self.net_worths[-1]))
                stock_ax.title.set_text("Stock Price: ${0:.2f}".format(self.full_data_df["Close"][self.cur_step]))
                amount_ax.title.set_text("Amount Bought/Sold (-1 to 1)")

                # Set the scales
                net_worth_ax.set_xlim([self.df_start_index - 1, self.df_end_index])

                net_worth_ax.set_ylim([line_min_networth - adjustment_networth,
                                       line_max_networth + adjustment_networth])
                stock_ax.set_ylim([line_min_stock - adjustment_stock, line_max_stock + adjustment_stock])
                amount_ax.set_ylim([-1.1, 1.1])

                # Draw data lines
                net_worth_ax.plot(range(self.df_start_index, self.df_end_index), self.net_worths[:self.data_df_len],
                                  color="b", label="Net Worth")
                stock_ax.plot(range(self.df_start_index, self.df_end_index),
                              self.full_data_df["Close"][self.df_start_index: self.df_end_index], color="r",
                              label="Closing Price")

                # Process the actions taken
                sell_only = [1 if x == 0 else 0 for x in self.actions_taken]
                buy_only = [1 if x == 2 else 0 for x in self.actions_taken]

                sell_actions = [x if x < 0 else None for x in self.actions_amount]
                buy_actions = [x if x > 0 else None for x in self.actions_amount]

                # Find where to place the symbols
                sell_positions = []
                buy_positions = []

                for i in range(self.data_df_len):
                    sell_pos = sell_only[i] * self.net_worths[i]
                    buy_pos = buy_only[i] * self.net_worths[i]

                    sell_positions.append(sell_pos if sell_pos != 0 else None)  # If 0, don't place the symbol
                    buy_positions.append(buy_pos if buy_pos != 0 else None)

                # Plot the actions taken
                net_worth_ax.scatter(range(self.df_start_index, self.df_end_index), sell_positions, label="Sell",
                                     color="red", marker="x")
                net_worth_ax.scatter(range(self.df_start_index, self.df_end_index), buy_positions, label="Buy",
                                     color="green", marker="x")

                stock_ax.scatter(range(self.df_start_index, self.df_end_index),
                                 [sell_only[i - self.df_start_index] * self.full_data_df["Close"][i] for i in
                                  range(self.df_start_index, self.df_end_index)], label="Sell", color="red", marker="x")
                stock_ax.scatter(range(self.df_start_index, self.df_end_index),
                                 [buy_only[i - self.df_start_index] * self.full_data_df["Close"][i] for i in
                                  range(self.df_start_index, self.df_end_index)], label="Buy", color="green",
                                 marker="x")

                # Plot action amounts
                amount_ax.stem(range(self.df_start_index, self.df_end_index), sell_actions, "red", markerfmt="ro",
                               label="Sell", use_line_collection=True)
                amount_ax.stem(range(self.df_start_index, self.df_end_index), buy_actions, "green", markerfmt="go",
                               label="Buy", use_line_collection=True)

                # Generate plot legend
                net_worth_ax.legend(loc="best")
                stock_ax.legend(loc="best")
                amount_ax.legend(loc="best")

                # Show the resulting figure
                plt.show()


# DEBUG CODE
if __name__ == "__main__":
    from lib.utils.dataUtils import process_data

    # Prepare the training dataframe
    debugDF = process_data("../trainingData/", "BA")  # Prepare Boeing data

    # Prepare the environment
    debugEnv = TradingEnv(debugDF, is_serial=True)

    # Reset the environment
    debugEnv.reset()

    # Increment the environment's step
    debugEnv.step((2, 1))  # BUY with 2/5 of money

    # Print `data_df`
    print(debugEnv.data_df)

    # Get the current state's observation list
    print(debugEnv.get_obs())
