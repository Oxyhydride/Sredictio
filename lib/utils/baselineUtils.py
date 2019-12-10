"""
baselineUtils.py

Created on 2019-10-29
Updated on 2019-12-09

Copyright Ryan Kan 2019

Description: A python file which contains the baseline algorithms.
"""
# IMPORTS
import pandas as pd
import ta
from tqdm import tqdm

from lib.env.TradingEnv import TradingEnv


# BASELINES CLASS
class Baselines:
    def __init__(self, dataframe: pd.DataFrame, render: bool = True, init_buyable_stocks: float = 2.5):
        """
        Baselines class. Contains the 3 baselines' policies.

        Keyword argument:
        - dataframe, pd.DataFrame: The dataframe containing all the data needed to train our model
        - render, bool: To render the environment or not (Default = True)
        - init_buyable_stocks, float: The number of stocks which the agent can buy on the first step. (Default = 2.5)
        """
        self.dataframe = dataframe  # Our dataframe
        self.render = render  # Can render?
        self.init_buyable_stocks = init_buyable_stocks  # Initial investment amount

        self.env = TradingEnv(self.dataframe, init_buyable_stocks=self.init_buyable_stocks, is_serial=True)
        self.env.reset(print_init_invest_amount=True)

    def run_policies(self):
        """
        Run the baselines' policies against an environment.

        Returns:
        - Scores of the three baselines in a list in the form [BHODL Score, RSI Score, SMA Score].
        """

        def bhodl_policy():
            """
            An old trading strategy, BHODL will be our first baseline against our agent.

            It is a relatively simple baseline to program:
            - If can buy, buy.
            - Else, hold.

            In principle, BHODL buys as much stock it can before bankrupting, and holds it to the end of the training
            period.
            """
            # Buy if possible
            if self.env.cash_in_hand // self.env.full_data_df["Open"][self.env.cur_step] >= 1:
                return 2, 10  # Buy maximal amount

            # If not, hold for all other cases
            else:
                return 1, 10  # Amount doesn't matter

        def rsi_policy():
            """
            When consecutive closing price continues to rise as the Relative Strength Index (RSI) continues to drop,
            a negative trend reversal (aka a sell) is signaled. A positive trend reversal (aka buy) is signaled when
            closing price consecutively drops as the RSI consecutively rises.
            """
            period = 5
            prices = self.env.full_data_df["Close"]
            cur_step = self.env.cur_step

            rsi = ta.rsi(prices)

            if cur_step >= period:
                rsi_sum = sum(rsi[cur_step - period:cur_step + 1].diff().cumsum().fillna(0))
                price_sum = sum(prices[cur_step - period:cur_step + 1].diff().cumsum().fillna(0))

                if rsi_sum < 0 <= price_sum:
                    return 0, 10
                elif rsi_sum > 0 >= price_sum:
                    return 2, 10

            return 1, 10

        def sma_policy():
            """
            When the longer-term SMA crosses above the shorter-term SMA, a negative trend reversal (aka sell) is
            signaled. A positive trend reversal (aka buy) is signaled when the shorter-term SMA crosses above the
            longer-term SMA.
            """
            prices = self.env.full_data_df["Close"]
            cur_step = self.env.cur_step

            macd = ta.macd(prices)

            if macd[cur_step] > 0 >= macd[cur_step - 1]:
                return 0, 10

            elif macd[cur_step] < 0 <= macd[cur_step - 1]:
                return 2, 10

            return 1, 10

        # Run baselines
        policy_order = [bhodl_policy, rsi_policy, sma_policy]
        policy_names = ["BHODL", "RSI Divergence", "SMA Crossover"]

        init_val = self.env.init_invest

        for i, policy in enumerate(policy_order):
            if self.render is not True:
                running_list = tqdm(range(self.env.start_index, self.env.end_index),
                                    desc=f"Running {policy_names[i]} baseline")
            else:
                running_list = range(self.env.start_index, self.env.end_index)

            # Reset environment
            self.env.reset()

            # Run policies
            for _ in running_list:
                action = policy()

                self.env.step(action)

                if self.render:
                    self.env.render()

            score = self.env.get_val()
            print(f"{policy_names[i]} baseline got ${score:.2f} ({(score / init_val) * 100 - 100:.3f}% increase)")


# DEBUG CODE
if __name__ == "__main__":
    from lib.utils.dataUtils import prep_data

    # Prepare data
    debugDF = prep_data("../trainingData/", "AMZN")

    # Run baselines
    baselines = Baselines(debugDF, render=False)
    baselines.run_policies()
