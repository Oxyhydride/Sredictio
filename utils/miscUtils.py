"""
miscUtils.py
Version 1.0.1

Created on 2019-12-04
Updated on 2019-12-10

Copyright Ryan Kan 2019

Description: Miscellaneous functions and classes.
"""
# IMPORTS
import re


# FUNCTIONS
def natural_sort(array):
    """
    Natural sort function.

    Keyword arguments:
    - array: List of strings.
    """

    def __convert__(text):
        if text.isdigit():
            return int(text)

        return text.lower()

    def alphanum_key(key):
        key_split = re.split('([0-9]+)', key)
        return [__convert__(c) for c in key_split]  # Ensure it is alphanumeric

    return sorted(array, key=alphanum_key)


def normalise(x_i, x_min, x_max, min_normalised_value=0, max_normalised_value=1):
    """
    Normalises the data to be in the range `min_normalised_value` to `max_normalised_value`.
    """
    return (((max_normalised_value - min_normalised_value) * (x_i - x_min)) / (x_max - x_min)) + min_normalised_value


def moving_average(arr, index, i_val, no_entries_taking_avg):
    """
    Computes the moving average list given an array `arr`.
    """
    return sum([x[index] for x in arr[i_val - no_entries_taking_avg:i_val]]) / no_entries_taking_avg
