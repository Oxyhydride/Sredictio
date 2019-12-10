"""
miscUtils.py

Created on 2019-12-04
Updated on 2019-12-10

Copyright Ryan Kan 2019

Description: Miscellaneous functions and classes.
"""
# IMPORTS
import os
import re


# FUNCTIONS
def natural_sort(array):
    """
    Natural sort function.

    Keyword arguments:
    - array: List of strings.

    Returns:
    - Sorted list of strings
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

    Keyword arguments:
    - x_i, float/int: The ith value in the array x.
    - x_min, float/int: The smallest number in the array x. I.E. x_min = min(x)
    - x_max, float/int: The largest number in the array x. I.E. x_max = max(x)
    - min_normalised_value, float/int: The value which x_min will be set in the normalised array. (Default = 0)
    - max_normalised_value, float/int: The value which x_max will be set in the normalised array. (Default = 1)

    Returns:
    - The normalised value of x_i (Float / Integer)
    """
    return (((max_normalised_value - min_normalised_value) * (x_i - x_min)) / (x_max - x_min)) + min_normalised_value


def moving_average(arr, index, i_val, no_entries_taking_avg):
    """
    Computes the moving average (MA) list given an array `arr`.

    Keyword arguments:
    - arr, list: The array containing floats/integers
    - index, int: If in a 2D array, `index` is the index of the array to select in that 2D array
    - i_val, int: The array `arr[i_val - no_entries_taking_avg:i_val]` is the set of numbers within the range of the MA
                  function. I.E. The numbers from `i_val - no_entries_taking_avg` to `i_val` will be selected for MA
                  processing.
    - no_entries_taking_avg, int: The number of entries to consider when taking the moving average.

    Returns:
    - The MAed value of x[index] for x = arr[i_val - no_entries_taking_avg:i_val].
    """
    return sum([x[index] for x in arr[i_val - no_entries_taking_avg:i_val]]) / no_entries_taking_avg


def create_path(path):
    """
    Attempts to make a new directory with the given path. If the path already exists, this function will not override
    the directory.

    Keyword arguments:
    - path, str: The directory path.
    """
    try:
        os.mkdir(path)  # Make a directory with that path

    except OSError:
        pass  # Directory already exists, don't want to do anything with it
