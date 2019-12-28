"""
loadingSpinner.py

Created on 2019-12-28
Updated on 2019-12-28

Copyright Ryan Kan 2019

Description: A file which helps draw a loading spinner in a Tkinter window.
"""

# IMPORTS
from math import sqrt
from tkinter import *


# CLASS
class LoadingSpinner:
    """
    This is a class which assists in the making of a loading spinner animation.

    The animation is done in Tkinter, which is a built-in GUI creator.

    To see a draft of the circle, you can go to https://www.desmos.com/calculator/e8hzykjid7
    to see a Desmos plot of the progress circle.
    """

    def __init__(self, window, scale_factor=10, length=45, circle_radius=5, full_spin_duration=0.6):
        """
        The initialisation method of the `LoadingSpinner` class.

        Args:
            window (Tk): The window of the Tkinter application that this spinner should be
                         placed in.

            scale_factor (int): The scale factor of the loading spinner. (Default=10)

                                Refer to https://www.desmos.com/calculator/e8hzykjid7 to
                                see how the scale factor is calculated, and how the circle
                                would look like in the end.

            length (int): The length of the canvas. (Default = 45)

            circle_radius (int): The radius of each circle in the spinner. (Default = 5)

            full_spin_duration (float): How long, in seconds, does it take for the spinner
                                        to complete one revolution? (Default = 0.6)

        Yields:
            AssertionError: If `full_spin_duration * 1000 / 8` is not an integer.

        """
        # Check if `full_spin_duration * 1000 / 8` is an integer
        assert (full_spin_duration * 1000 / 8).is_integer(), "`full_spin_duration * 1000 / 8` is not an integer."

        # Define Tkinter variables
        self.canvas = Canvas(window, height=length, width=length)
        self.progress_circle_points = self.draw_loading_spinner((length + 5) / 2, (length + 5) / 2, scale_factor,
                                                                circle_radius=circle_radius)

        # Define other variables
        self.full_spin_duration = full_spin_duration * 1000  # This is in milliseconds
        self.current_selected_circle = 0

        # Start the progress circle
        self.canvas.pack()
        self.update_loading_spinner()

    def draw_circle(self, x, y, radius, fill_colour="gray70"):
        circle = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, width=0, fill=fill_colour)

        return circle

    def draw_loading_spinner(self, center_x, center_y, scale_factor, circle_radius=5, colour="gray70"):
        progress_circle_points = [
            self.draw_circle(center_x + scale_factor, center_y + scale_factor, circle_radius, fill_colour=colour),
            self.draw_circle(center_x, scale_factor * sqrt(2) + center_y, circle_radius, fill_colour=colour),
            self.draw_circle(center_x - scale_factor, center_y + scale_factor, circle_radius, fill_colour=colour),
            self.draw_circle(-scale_factor * sqrt(2) + center_x, center_y, circle_radius, fill_colour=colour),
            self.draw_circle(center_x - scale_factor, center_y - scale_factor, circle_radius, fill_colour=colour),
            self.draw_circle(center_x, -scale_factor * sqrt(2) + center_y, circle_radius, fill_colour=colour),
            self.draw_circle(center_x + scale_factor, center_y - scale_factor, circle_radius, fill_colour=colour),
            self.draw_circle(scale_factor * sqrt(2) + center_x, center_y, circle_radius, fill_colour=colour),
        ]

        return progress_circle_points

    def update_spinner(self, progress_circle_points, new_triggered_circle, orig_colour="gray70", new_colour="gray"):
        self.canvas.itemconfig(progress_circle_points[(new_triggered_circle - 1) % 8], fill=orig_colour)
        self.canvas.itemconfig(progress_circle_points[new_triggered_circle], fill=new_colour)

        return progress_circle_points

    def update_loading_spinner(self):
        to_update = (self.current_selected_circle + 1) % 8

        self.update_spinner(self.progress_circle_points, to_update)
        self.current_selected_circle += 1

        self.canvas.after(int(self.full_spin_duration / 8), self.update_loading_spinner)


# DEBUG CODE
if __name__ == "__main__":
    root = Tk()
    loadingSpinner = LoadingSpinner(root)

    root.mainloop()
