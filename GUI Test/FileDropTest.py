import tkinter as tk
from tkinter import filedialog


def select_file():
    filename = filedialog.askopenfilename()

    if filename == "":
        print("No file selected!")
    else:
        print("Selected:", filename)


root = tk.Tk()
button = tk.Button(root, text="Open File...", command=select_file)
button.pack()

root.mainloop()
