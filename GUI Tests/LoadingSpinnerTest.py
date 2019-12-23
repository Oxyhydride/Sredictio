from tkinter import *
from math import sqrt


def draw_progress_circle(canvas, center_x, center_y, scale_factor, circle_radius=5, colour="blue"):
    progress_circle_points = [
        # First 4: "edge" points
        draw_circle(canvas, center_x + scale_factor, center_y + scale_factor, circle_radius, colour=colour),
        draw_circle(canvas, center_x - scale_factor, center_y + scale_factor, circle_radius, colour=colour),
        draw_circle(canvas, center_x + scale_factor, center_y - scale_factor, circle_radius, colour=colour),
        draw_circle(canvas, center_x - scale_factor, center_y - scale_factor, circle_radius, colour=colour),

        # Next 4: "axes" points
        draw_circle(canvas, scale_factor * sqrt(2) + center_x, center_y, circle_radius, colour=colour),
        draw_circle(canvas, -scale_factor * sqrt(2) + center_x, center_y, circle_radius, colour=colour),
        draw_circle(canvas, center_x, scale_factor * sqrt(2) + center_y, circle_radius, colour=colour),
        draw_circle(canvas, center_x, -scale_factor * sqrt(2) + center_y, circle_radius, colour=colour),

        # Center point
        # TODO (Ryan-Kan, 0.3.0): REMOVE THIS CODE AFTER DEBUGGING
        draw_circle(canvas, center_x, center_y, 1, colour="red")
    ]

    return progress_circle_points


def draw_circle(canvas, x, y, rad, colour="blue"):
    return canvas.create_oval(x - rad, y - rad, x + rad, y + rad, width=0, fill=colour)


def update_spinner():
    # TODO (Ryan-Kan, 0.3.0): UPDATE SPINNER
    pass


top = Tk()
C = Canvas(top, height=95, width=95)
pcp = draw_progress_circle(C, 50, 50, 20, colour="gray")

C.pack()
top.mainloop()
