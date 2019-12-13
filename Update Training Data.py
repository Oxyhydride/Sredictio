"""
Update Training Data.py

Created on 2019-12-13
Updated on 2019-12-13

Copyright Ryan Kan 2019

Description: A program which helps update the training data folders located in each of the subdirectories.
"""

# IMPORTS
import os

from tqdm import trange

from lib.utils.miscUtils import natural_sort
from lib.utils.sentimentUtils import get_sentiment_data
from lib.utils.stockUtils import get_stock_data

# INPUT
TRAINING_DIR = "./Training Data/"

ALL_OR_ONE = input("Should the program update all the training data or just one stock's?\nIf it is just one stock, "
                   "input the STOCK'S SYMBOL in ALL CAPS. If not, enter `ALL` without the quotes. ")

print("\nFor the ENDING date, ensure that it is MORE RECENT than the STARTING date.")
START_DATE = input("Please enter the starting date in the form YYYY-MM-DD: ")
END_DATE = input("Please enter the ending date in the form YYYY-MM-DD:   ")

VERBOSE_LEVEL = int(input("\nWhat should the verbose level be?\n0 = No messages; 1 = No sentiment messages; 2 = All "
                          "messages: "))

print()

# CODE
# Find all stock symbols
stockSymbols = natural_sort([d.split("/")[2] for d in [x[0] for x in os.walk(TRAINING_DIR)][1:]])

# Remove __pycache__
try:
    stockSymbols.remove("__pycache__")

except ValueError:
    pass

# Get all stocks' saved names
stockNames = []
for stockSymbol in stockSymbols:
    with open(TRAINING_DIR + stockSymbol + "/Stock Info.txt") as f:
        allLines = f.readlines()
        fileDict = {}

        for line in allLines:
            lineContent = line.strip().replace(" ", "").split(":")

            try:
                fileDict[lineContent[0].upper()] = lineContent[1]

            except IndexError:
                pass

        f.close()
    stockNames.append(fileDict["STOCKNAME"])

# Replace all dashes in stock names with spaces
for i in range(len(stockNames)):
    stockNames[i] = list(stockNames)[i].replace("-", " ")

# Create a symbol-name dictionary
symbolName = {}
for i in range(len(stockNames)):
    symbolName[stockSymbols[i]] = stockNames[i]

# Check what needs to be updated
if ALL_OR_ONE != "ALL":
    # Find the stock that needs updating
    symbolUpdate = ALL_OR_ONE
    nameUpdate = symbolName[symbolUpdate]

    # Update symbolName with that stock
    symbolName = {symbolUpdate: nameUpdate}

# Update training data for each stock
if VERBOSE_LEVEL == 0:
    iterable = trange(len(symbolName), desc="Updating training data (this may take a while!)")

else:
    iterable = range(len(symbolName))

for i in iterable:
    symbol, name = list(symbolName.keys())[i], list(symbolName.values())[i]

    if VERBOSE_LEVEL > 0:
        print(f" UPDATING '{symbol}' TRAINING DATA ".center(80, "-"))

    # Update OHLCV data
    get_stock_data(symbol, START_DATE, END_DATE, save_as_csv=True, verbose=(VERBOSE_LEVEL != 0),
                   file_location=TRAINING_DIR + symbol + "/" + symbol + "_stocks.csv")

    # Update sentiment data
    if VERBOSE_LEVEL > 0:
        print(f"Getting {symbol} sentiment data...")
    get_sentiment_data(symbol, name, START_DATE, END_DATE, output_dir=TRAINING_DIR + symbol + "/",
                       verbose=VERBOSE_LEVEL == 2)

    # Print new line
    if VERBOSE_LEVEL > 0:
        print()

print(f"Update complete! Updated {len(symbolName)} directory's/directories' contents.")
