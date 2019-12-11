"""
GUIMain.py

Created on 2019-12-11
Updated on 2019-12-11

Copyright Ryan Kan 2019

Description: The main python file for Sredictio's GUI

NOTE: This is just a test file.
"""
# IMPORTS
from tkinter import *
from tkinter import ttk
import tkinter.font as tk_font

# CONSTANTS
ERROR_STR_LEN = 50
ERROR_CODES = {
    1: "Not all entries are filled!",  # This is a common error!
    2: "Stock Name is too short!",  # I wonder how this can get triggered...
}


# FUNCTIONS
def set_error(error_code: int, error_str_len: int = ERROR_STR_LEN):
    """
    Places the error on the screen.

    Keyword arguments:
    - error_code, int: The error code. The program will extract the error from the above dictionary.
    - error_str_len, int: The maximum size the error string can be.
    """
    outputLabel["text"] = f"ERROR {error_code:02d}: {ERROR_CODES[error_code]}".center(error_str_len, " ")
    outputLabel["foreground"] = "Red"


def compute():
    # Reset output label colour
    outputLabel["foreground"] = "Black"  # Set to black first

    # Get entered variables
    stock_name = stockName.get() if stockName.get() != "" else None
    stock_symbol = stockSymbol.get() if stockSymbol.get() != "" else None

    # Check if both variables are filled in
    if stock_symbol is not None and stock_name is not None:
        print(stock_name, stock_symbol)

    else:
        # Place an error on the window
        set_error(1)
        return

    # Check stock name length
    if len(stock_name) < 3:  # How can a stock's name be less than 3 characters?
        set_error(2)
        return


# CODE
# Create root window
root = Tk()
root.title("Sredictio")

# Fill in main window with the frame
mainframe = ttk.Frame(root, padding="3 4 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Define variables
stockName = StringVar()
stockSymbol = StringVar()

# Create widgets
stockNameLabel = ttk.Label(mainframe, text="Enter the Stock Name:", )
stockNameLabel.grid(column=0, row=0, sticky=(W, E))

stockNameEntry = ttk.Entry(mainframe, textvariable=stockName)
stockNameEntry.grid(column=2, row=0, sticky=(W, E))

stockSymbolLabel = ttk.Label(mainframe, text="Enter the Stock Symbol:")
stockSymbolLabel.grid(column=0, row=1, sticky=(W, E))

stockSymbolEntry = ttk.Entry(mainframe, textvariable=stockSymbol)
stockSymbolEntry.grid(column=2, row=1, sticky=(W, E))

outputLabel = ttk.Label(mainframe, font=tk_font.Font(family="Courier New", size=16))
outputLabel.grid(column=1, row=3, sticky=W)
outputLabel["text"] = " " * ERROR_STR_LEN

ttk.Button(mainframe, text="Compute!", command=compute).grid(column=1, row=2)

# Configure widgets to be placed on grid
for child in mainframe.winfo_children():
    child.grid_configure(padx=3, pady=4)

# Bind the Return key to the compute function
root.bind('<Return>', compute)

# Run the application
root.mainloop()
