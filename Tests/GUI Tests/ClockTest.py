import time
from tkinter import *

root = Tk()
currTime = ""
clock = Label(root, font=("arial", 20, "bold"), bg="green")
clock.pack(fill=BOTH, expand=1)


def tick():
    global currTime

    # Get the current local time from the PC
    new_time = time.strftime("%H:%M:%S")

    # If time string has changed, update it
    if new_time != currTime:
        currTime = new_time
        clock.config(text=new_time)

    # Calls itself every 200 milliseconds to update the time display as needed
    # Can use >200 ms, but display gets jerky
    clock.after(200, tick)


tick()
root.mainloop()
