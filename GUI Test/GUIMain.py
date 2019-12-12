"""
GUIMain.py

Created on 2019-12-11
Updated on 2019-12-12

Copyright Ryan Kan 2019

Description: The main python file for Sredictio's GUI

NOTE: This is just a test file.
"""
import tkinter.font as tk_font
# IMPORTS
from tkinter import *
from tkinter import ttk

from lib.utils.stockUtils import get_html_rows

# CONSTANTS
MESSAGE_STR_LEN = 80
MESSAGE_CODES = {
    # Errors
    "E1": "Not all entries are filled!",  # This is a common error!
    "E2": "Stock name is too short!",  # I wonder how this can get triggered...

    # Warnings
    "W1": "Stock symbol could not be found on Yahoo Finance."
}


# APPLICATION CLASS
class Application(ttk.Frame):
    def __init__(self, master):
        # Initialise tkinter things
        super().__init__(master)
        self.master = master
        self.pack()

        # Initialise window
        self["padding"] = "3 4 12 12"
        self.grid(column=0, row=0, sticky=(N, W, E, S))

        # Define application variables
        self.stockName = StringVar()
        self.stockSymbol = StringVar()

        # Initialise widget variables
        self.stockNameLabel = None
        self.stockNameEntry = None
        self.stockSymbolLabel = None
        self.stockSymbolEntry = None
        self.outputLabel = None

        # Create things
        self.create_widgets()

    def show_message(self, message_type: str, message_code: int, message_str_len: int = MESSAGE_STR_LEN):
        """
        Places the error on the screen.

        Keyword arguments:
        - message_type, str: The message type. Must be in the list ["ERROR", "WARNING"]
        - message_code, int: The message's code.
        - message_str_len, int: The maximum size the error string can be.
        """
        # Check if message type is known
        assert message_type.upper() in ["ERROR", "WARNING"], "Message type not known."

        # Find the correct prefix
        prefix = message_type[0].upper()

        # Check if message with code exists
        assert prefix + str(
            message_code) in MESSAGE_CODES.keys(), "Type-Code pair not found in the MESSAGE_CODES dictionary."

        # Get correct colour
        if message_type.upper() == "ERROR":
            self.outputLabel["foreground"] = "red"
        elif message_type.upper() == "WARNING":
            self.outputLabel["foreground"] = "yellow4"

        # Place message
        self.outputLabel["text"] = f"{message_type.upper()} {message_code:02d}: " \
                                   f"{MESSAGE_CODES[f'{message_type.upper()[0]}{message_code}']}" \
            .center(message_str_len, " ")

    def create_widgets(self):
        self.stockNameLabel = ttk.Label(self, text="Enter the Stock Name:", )
        self.stockNameLabel.grid(column=0, row=0, sticky=(W, E))

        self.stockNameEntry = ttk.Entry(self, textvariable=self.stockName)
        self.stockNameEntry.grid(column=2, row=0, sticky=(W, E))

        self.stockSymbolLabel = ttk.Label(self, text="Enter the Stock Symbol:")
        self.stockSymbolLabel.grid(column=0, row=1, sticky=(W, E))

        self.stockSymbolEntry = ttk.Entry(self, textvariable=self.stockSymbol)
        self.stockSymbolEntry.grid(column=2, row=1, sticky=(W, E))

        self.outputLabel = ttk.Label(self, font=tk_font.Font(family="Courier New", size=16))
        self.outputLabel.grid(column=1, row=3, sticky=W)
        self.outputLabel["text"] = " " * MESSAGE_STR_LEN

        ttk.Button(self, text="Compute!", command=self.compute).grid(column=1, row=2)

    def compute(self):
        # Reset output label colour
        self.outputLabel["foreground"] = "Black"  # Set to black first

        # Get entered variables
        stock_name = self.stockName.get() if self.stockName.get() != "" else None
        stock_symbol = self.stockSymbol.get() if self.stockSymbol.get() != "" else None

        # Check if both variables are filled in
        if (stock_symbol is None) or (stock_name is None):
            # Place an error on the window
            self.show_message("ERROR", 1)
            return

        # Check stock name length
        if len(stock_name) < 3:  # How can a stock's name be less than 3 characters?
            self.show_message("ERROR", 2)
            return

        # Check if the stock symbol exists
        try:
            print("Getting HTML rows...")
            get_html_rows(stock_symbol)

        except NameError:
            print("Stock symbol not found... uh oh")
            self.show_message("WARNING", 1)
            return


# Create root
root = Tk()
root.title("Sredictio")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Create application
app = Application(master=root)

# Configure children of application
for child in app.winfo_children():
    child.grid_configure(padx=3, pady=4)

# Start the application
app.mainloop()
