# -*- coding: utf-8 -*-

import threading
import tkinter as tk

from functools import partial

from model import Model, Simulator
from settings import NUMBER_OF_FLOORS, SIMULATION_REAL_TIME_SCALE


class App:
    BACKGROUND = "lightgray"

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Elevator DEVS model")
        self.window.geometry("800x640")
        self.window.minsize(width=500, height=500)
        self.frame = tk.Frame(self.window)
        self.frame.grid(sticky=tk.W + tk.E + tk.N + tk.S)
        self.frame["bg"] = self.BACKGROUND

        self.right_frame = tk.Frame(self.window)
        self.right_frame.grid(row=0, column=1, sticky=tk.W + tk.E + tk.N + tk.S)
        self.right_frame["bg"] = self.BACKGROUND

        # adapt for window's resizing
        tk.Grid.rowconfigure(self.window, 0, weight=1)
        tk.Grid.columnconfigure(self.window, 0, weight=1)

        # widgets
        self.top_label = tk.Label(self.frame, text="Elevator", background=self.BACKGROUND)
        self.top_label_time = tk.Label(self.frame, text=0, background=self.BACKGROUND)
        self.buttons, self.floors, self.floors_info = self.create_floors()
        self.update_floor(0)  # set floor #0 as initial
        self.bottom_label = tk.Label(self.frame, text="====", background=self.BACKGROUND)

        self.time = 0
        canvas = tk.Canvas(self.right_frame, width=600, height=600, scrollregion=(0, 0, 2000, 2000))
        canvas.grid(row=0, column=0)
        canvas.create_line(0, 100, 600, 100)
        canvas.create_line(0, 200, 600, 200)
        self.current_floor = 0
        self.destination_floor = 0

        right_scrollbar = tk.Scrollbar(self.right_frame, orient=tk.HORIZONTAL)
        right_scrollbar.grid(row=1, column=0, sticky=tk.W + tk.E)
        right_scrollbar.config(command=canvas.xview)
        canvas.config(xscrollcommand=right_scrollbar.set)

        def update_time():
            self.time += 1
            if self.current_floor:
                canvas.create_line(
                    self.time,
                    100,
                    self.time + 1,
                    100 - 10 * self.current_floor,
                    fill="red", width=2.0
                )
            if self.destination_floor:
                canvas.create_line(
                    self.time,
                    200,
                    self.time + 1,
                    200 - 10 * self.destination_floor,
                    fill="green", width=2.0
                )
            self.top_label_time["text"] += 1
            self.window.after(int(1000 * SIMULATION_REAL_TIME_SCALE), update_time)
        update_time()

        # grid settings
        self.frame.columnconfigure(0, pad=10)
        self.frame.rowconfigure(0, pad=10)

        # layout of widgets
        self.top_label.grid(row=0, column=0)
        self.top_label_time.grid(row=0, column=1)
        self.bottom_label.grid(row=NUMBER_OF_FLOORS + 1, column=0)

        self.simulator = None

    def create_floors(self):
        buttons, floors, floors_info = {}, {}, {}
        for floor in range(NUMBER_OF_FLOORS):
            label = tk.Label(self.frame, text="", background=self.BACKGROUND)
            label.grid(row=NUMBER_OF_FLOORS - floor, column=0)
            floors[floor] = label

            button = tk.Button(self.frame, text="O", background=self.BACKGROUND, command=partial(self.go_floor, floor))
            button.grid(row=NUMBER_OF_FLOORS - floor, column=1)
            buttons[floor] = button

            label = tk.Label(self.frame, text="", background=self.BACKGROUND)
            label.grid(row=NUMBER_OF_FLOORS - floor, column=2)
            floors_info[floor] = label

        return buttons, floors, floors_info

    def add_simulator(self, simulator):
        self.simulator = simulator

    def go_floor(self, floor):
        self.simulator.realtime_interrupt("inport_go %s" % floor)

    def update_floor(self, new_floor: int):
        self.current_floor = new_floor
        for floor in self.floors.values():
            floor["text"] = ""
        self.floors[new_floor]["text"] = "[]"

    def clear_destination_floor(self):
        for floor in self.floors_info.values():
            floor["text"] = ""
        for button in self.buttons.values():
            button.config(state=tk.NORMAL, background=self.BACKGROUND)

    def set_destination_floor(self, new_floor: int):
        self.destination_floor = new_floor
        self.clear_destination_floor()
        self.floors_info[new_floor]["text"] = "x"
        self.buttons[new_floor].config(state=tk.DISABLED, background="orange")


if __name__ == "__main__":
    app = App()

    model = Model(app)
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setVerbose()
    sim.setDrawModel()

    sim.setRealTime(True, scale=SIMULATION_REAL_TIME_SCALE)
    sim.setRealTimePorts({"inport_go": model.elevator_go.inport_go})

    t = threading.Thread(target=sim.simulate)
    t.daemon = True
    t.start()

    app.add_simulator(sim)
    app.window.mainloop()
