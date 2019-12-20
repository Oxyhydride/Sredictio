"""
graphingUtils.py

Created on 2019-09-08
Updated on 2019-12-16

Copyright Ryan Kan 2019

Description: Utilities related to graphing are stored in this file.
"""
# IMPORTS
import seaborn as sns
from matplotlib import rcParams


# FUNCTIONS
def setup_graph(render=False):
    """
    A function which sets up the graphs' parameters

    Args:
        render (bool): Whether the environment should be rendered.

    """
    if not render:
        rcParams['figure.figsize'] = 14, 8

    # Setup Seaborn parameters
    sns.set(style='white', palette='muted', font_scale=1.5)
