# -*- coding: utf-8 -*-

import threading
import tkinter as tk

from time import sleep


class TestModel:
    def __init__(self, number_of_floors):
        self.number_of_floors = number_of_floors
        self.floor = 0
        self.up = True
        self.down = False

    def next_state(self):
        if self.floor == self.number_of_floors - 1:
            self.up = False
            self.down = True
        if self.floor == 0:
            self.up = True
            self.down = False

        if self.up:
            self.floor += 1
        elif self.down:
            self.floor -= 1

        return {
            "floor": self.floor
        }

    def simulate(self):
        while True:
            print(self.floor)
            yield self.next_state()
            sleep(1)


class App:
    BACKGROUND = "lightgray"

    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Web spider for scientific documents')
        self.window.geometry('800x600')
        self.window.minsize(width=500, height=500)
        self.frame = tk.Frame(self.window)
        self.frame.grid(sticky=tk.W + tk.E + tk.N + tk.S)
        self.frame["bg"] = self.BACKGROUND

        self.number_of_floors = 8

        # adapt for window's resizing
        tk.Grid.rowconfigure(self.window, 0, weight=1)
        tk.Grid.columnconfigure(self.window, 0, weight=1)

        # widgets
        self.label = tk.Label(self.frame, text="Elevator model", background=self.BACKGROUND)
        self.floors = self.create_floors()

        # grid settings
        self.frame.columnconfigure(0, pad=10)
        self.frame.rowconfigure(0, pad=10)

        # layout of widgets
        self.label.grid(row=0, column=0)

        # simulation
        self.model = TestModel(self.number_of_floors)
        self.simulation()

    def create_floors(self):
        floors = {}
        for floor in range(self.number_of_floors):
            label = tk.Label(self.frame, text="", background=self.BACKGROUND)
            label.grid(row=floor + 1, column=0)
            floors[floor] = label
        return floors

    def simulation(self):
        def update():
            for state in self.model.simulate():
                for floor in self.floors.values():
                    floor["text"] = ""
                self.floors[state["floor"]]["text"] = "[]"

        self.t = threading.Thread(target=update)
        self.t.daemon = True
        self.t.start()


if __name__ == "__main__":
    app = App()
    app.window.mainloop()
