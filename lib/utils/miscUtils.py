"""
miscUtils.py

Created on 2019-12-04
Updated on 2019-12-16

Copyright Ryan Kan 2019

Description: Miscellaneous functions that are used in the programs.
"""
# IMPORTS
import os
import re


# FUNCTIONS
def natural_sort(array):
    """
    The natural sort function.

    Args:
        array (list): A list of strings to be sorted naturally.

                      In `natural_sort`, the elements in the list `array` would be sorted according to
                      how a human would sort it.
    Returns:
        list: The sorted list.

    Examples:
        >>> natural_sort(["1-Alpha", "Alpha-1", "2-Beta", "Beta-2", "3-Gamma"])
        ['1-Alpha', '2-Beta', '3-Gamma', 'Alpha-1', 'Beta-2']

    """

    def __convert__(text):
        if text.isdigit():
            return int(text)

        return text.lower()

    def alphanum_key(key):
        key_split = re.split('([0-9]+)', key)
        return [__convert__(c) for c in key_split]  # Ensure that the list is alphanumeric

    return sorted(array, key=alphanum_key)


def normalise(x_i, x_min, x_max, min_normalised_value=0, max_normalised_value=1):
    """
    A function to normalise the data to be in the range `min_normalised_value` to `max_normalised_value`.

    Args:
        x_i (float): The i-th value in the array `x`.

        x_min (float): The smallest number in the array `x`. I.E. `x_min = min(x)`

        x_max (float): The largest number in the array `x`. I.E. `x_max = max(x)`

        min_normalised_value (float): The value which `x_min` will be set in the normalised array.
                                      (Default = 0)

        max_normalised_value (float): The value which x_max will be set in the normalised array.
                                      (Default = 1)

    Returns:
        float: The normalised value of `x_i`.

    Examples:
        >>> normalise(3, 1, 6)
        0.4
        >>> normalise(6, 1, 6)
        1.0
        >>> normalise(1, 1, 6)
        0.0
        >>> normalise(4, 1, 6, min_normalised_value=1, max_normalised_value=2)
        1.6

    """
    return (((max_normalised_value - min_normalised_value) * (x_i - x_min)) / (x_max - x_min)) + min_normalised_value


def moving_average(arr, index, i_val, no_entries_taking_avg):
    """
    Computes the Moving Average (MA) list given a(n) list/array `arr`.

    Args:
        arr (list, np.ndarray): The list/array containing floats.

        index (int): If in a 2D array, `index` is the index of the array to select in that 2D array

        i_val (int): The array `arr[i_val - no_entries_taking_avg:i_val]` is the set of numbers within
                     the range of the MA function. I.E. The numbers from `i_val - no_entries_taking_avg`
                     to `i_val` will be selected for MA processing.

        no_entries_taking_avg (int): The number of entries to consider when taking the moving average.

    Returns:
        float: The MAed value of x[index] for x = arr[i_val - no_entries_taking_avg:i_val].

    Examples:
        >>> import numpy as np
        >>> L = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19, 20]])
        >>> moving_average(L, 1, 2, no_entries_taking_avg=2)
        4.0

    """

    return sum([x[index] for x in arr[i_val - no_entries_taking_avg:i_val]]) / no_entries_taking_avg


def create_path(path):
    """
    Attempts to make a new directory with the given path. If the path already exists, this function will
    not override the contents inside the directory.

    Args:
        path (str): The path to place the directory.

    """

    try:
        os.mkdir(path)  # Make a directory with that path

    except OSError:
        pass  # Directory already exists, don't want to do anything with it
