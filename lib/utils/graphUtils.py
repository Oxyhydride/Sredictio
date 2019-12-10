"""
graphUtils.py

Created on 2019-09-08
Updated on 2019-12-10

Copyright Ryan Kan 2019

Description: The utilities required to plot the graphs
"""
# IMPORTS
import seaborn as sns
from matplotlib import rcParams


# FUNCTIONS
def setup_graph(render=False):
    # For Jupyter notebook
    if not render:
        rcParams['figure.figsize'] = 14, 8

    # Setup Seaborn
    sns.set(style='white', palette='muted', font_scale=1.5)
