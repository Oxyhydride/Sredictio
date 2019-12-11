"""
GUIMain.py

Created on 2019-12-11
Updated on 2019-12-11

Copyright Ryan Kan 2019

Description: The main python file for Sredictio's GUI

NOTE: This is just testing.
"""
# IMPORTS
from tkinter import *
from tkinter import ttk

# CODE
# Create root window
root = Tk()
root.title("Sredictio")

# Fill in main window with the frame
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Define variables
stockName = StringVar()
stockSymbol = StringVar()

# Create entries
stockNameEntry = ttk.Entry()
stockNameEntry.grid(column=1, row=1, sticky=(W, E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.mainloop()
