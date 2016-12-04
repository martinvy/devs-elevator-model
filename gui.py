# -*- coding: utf-8 -*-

import threading
import tkinter as tk

from model import Model, Simulator
from settings import NUMBER_OF_FLOORS


class App:
    BACKGROUND = "lightgray"

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Elevator DEVS model")
        self.window.geometry("800x600")
        self.window.minsize(width=500, height=500)
        self.frame = tk.Frame(self.window)
        self.frame.grid(sticky=tk.W + tk.E + tk.N + tk.S)
        self.frame["bg"] = self.BACKGROUND

        # adapt for window's resizing
        tk.Grid.rowconfigure(self.window, 0, weight=1)
        tk.Grid.columnconfigure(self.window, 0, weight=1)

        # widgets
        self.top_label = tk.Label(self.frame, text="Elevator", background=self.BACKGROUND)
        self.floors = self.create_floors()
        self.update_floor(0)  # set floor #0 as initial
        self.bottom_label = tk.Label(self.frame, text="====", background=self.BACKGROUND)

        # grid settings
        self.frame.columnconfigure(0, pad=10)
        self.frame.rowconfigure(0, pad=10)

        # layout of widgets
        self.top_label.grid(row=0, column=0)
        self.bottom_label.grid(row=NUMBER_OF_FLOORS + 1, column=0)

    def create_floors(self):
        floors = {}
        for floor in range(NUMBER_OF_FLOORS):
            label = tk.Label(self.frame, text="", background=self.BACKGROUND)
            label.grid(row=NUMBER_OF_FLOORS - floor, column=0)
            floors[floor] = label
        return floors

    def update_floor(self, new_floor: int):
        for floor in self.floors.values():
            floor["text"] = ""
        self.floors[new_floor]["text"] = "[]"


if __name__ == "__main__":
    app = App()

    model = Model(app)
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(500.0)
    sim.setVerbose()
    sim.setRealTime(True, scale=0.5)

    t = threading.Thread(target=sim.simulate)
    t.daemon = True
    t.start()

    app.window.mainloop()
