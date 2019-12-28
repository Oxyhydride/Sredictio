"""
baselineUtils.py

Created on 2019-10-29
Updated on 2019-12-25

Copyright Ryan Kan 2019

Description: A python file which contains the baseline algorithms.
"""
# IMPORTS
import pandas as pd
import ta
from tqdm import tqdm

from lib.environment.tradingEnv import TradingEnv


# BASELINES CLASS
class Baselines:
    """
    This is the `Baselines` class, which contains the 3 baseline policies used to test the environment.

    The three baselines used to test the environment are as follows:
        1. Buy and Hold On for Dear Life (BHODL)
            An old trading strategy, BHODL will be our first baseline against our agent.

            It is a relatively simple baseline to program:
            - If can buy, buy.
            - Else, hold.

            In principle, BHODL buys as much stock it can before bankrupting, and holds it to the end
            of the training period.

        2. RSI Divergence
            When consecutive closing price continues to rise as the Relative Strength Index (RSI)
            continues to drop, a negative trend reversal (a.k.a. a sell) is signaled. A positive trend
            reversal (a.k.a. buy) is signaled when closing price consecutively drops as the RSI
            consecutively rises.

        3. SMA Crossover
            When the longer-term SMA crosses above the shorter-term SMA, a negative trend reversal (a.k.a.
            sell) is signaled. A positive trend reversal (a.k.a. buy) is signaled when the shorter-term
            SMA crosses above the longer-term SMA.

    """
    def __init__(self, dataframe, render=True, init_buyable_stocks=2.5):
        """
        Initialisation method for the `Baselines` class.

        Args:
            dataframe (pd.DataFrame): The dataframe containing all the OHLCV data + the sentiment data

            render (bool): To render the environment or not (Default = True)

                           The rendering function used is the same as the `TradingEnv` rendering function,
                           which allows us to see the agent's net worth and the current stock price for
                           that particular stock.

            init_buyable_stocks (float): The number of stocks that the agent can buy on the first step.
                                         (Default = 2.5)

                                         For example, if `init_buyable_stocks = 3` and the closing price for
                                         the first day is $100, then the agent will have $300 on the first
                                         day.

        """
        self.dataframe = dataframe
        self.render = render  # Can the environment render?
        self.init_buyable_stocks = init_buyable_stocks  # Initial number of stocks which the agent can buy

        # Initialise the trading environment
        self.env = TradingEnv(self.dataframe, init_buyable_stocks=self.init_buyable_stocks, is_serial=True)
        self.env.reset(print_init_invest_amount=True)

    def run_policies(self):
        """
        Runs the baseline policies against a defined environment.

        Returns:
            List[float, float, float]: Scores of the three baselines in a list in the following form:
                                       [BHODL Score, RSI Score, SMA Score]

        """

        def bhodl_policy():
            """
            The BHODL baseline algorithm.

            Returns:
                Tuple[int, int]: The Action-Amount pair.

            """
            # Buy if possible
            if self.env.cash_in_hand // self.env.full_data_df["Open"][self.env.cur_step] >= 1:
                return 2, 10  # Buy maximal amount

            # If not, hold for all other cases
            else:
                return 1, 10  # Amount doesn't matter

        def rsi_policy():
            """
            The RSI Divergence algorithm.

            Returns:
                Tuple[int, int]: The Action-Amount pair.

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
            The SMA Crossover algorithm.

            Returns:
                Tuple[int, int]: The Action-Amount pair.

            """
            prices = self.env.full_data_df["Close"]
            cur_step = self.env.cur_step

            macd = ta.macd(prices)

            if macd[cur_step] > 0 >= macd[cur_step - 1]:
                return 0, 10

            elif macd[cur_step] < 0 <= macd[cur_step - 1]:
                return 2, 10

            return 1, 10

        # Run the baselines against the environment
        policy_order = [bhodl_policy, rsi_policy, sma_policy]
        policy_names = ["BHODL", "RSI Divergence", "SMA Crossover"]

        init_val = self.env.init_invest

        for i, policy in enumerate(policy_order):
            if self.render is not True:
                running_list = tqdm(range(self.env.df_start_index, self.env.df_end_index),
                                    desc=f"Running {policy_names[i]} baseline")
            else:
                running_list = range(self.env.df_start_index, self.env.df_end_index)

            self.env.reset()

            # Run the baselines' algorithms
            for _ in running_list:
                action = policy()

                self.env.step(action)

                if self.render:
                    self.env.render()

            score = self.env.get_val()
            print(f"{policy_names[i]} baseline got ${score:.2f} ({(score / init_val) * 100 - 100:.3f}% increase)")


# DEBUG CODE
if __name__ == "__main__":
    from lib.utils.dataUtils import obtain_data, process_data

    # Prepare the data
    ohlcvData, sentimentData = obtain_data("../../Training Data/", "AMZN")
    debugDF = process_data(ohlcvData, sentimentData)

    # Run baselines against environment
    baselines = Baselines(debugDF, render=False)
    baselines.run_policies()
