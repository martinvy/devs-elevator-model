# -*- coding: utf-8 -*-

import random

from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY


class Elevator(AtomicDEVS):
    MOVE_TIME = 2

    def __init__(self, api):
        super().__init__("Elevator")
        self.api = api
        self.inport = self.addInPort("inport")
        self.outport = self.addOutPort("outport")
        self.state = "IDLE"
        self.floor = 0
        self.max_floors = 10

    def timeAdvance(self):
        if self.state == "IDLE":
            return INFINITY
        if self.state in ("UP", "DOWN"):
            return self.MOVE_TIME

    def outputFnc(self):
        print(self.floor)
        return {self.outport: self.floor}

    def intTransition(self):
        if self.state == "UP":
            self.floor = self.floor + 1 if self.floor < self.max_floors else self.floor
        elif self.state == "DOWN":
            self.floor = self.floor - 1 if self.floor > 0 else self.floor
        self.state = "IDLE"
        return self.state

    def extTransition(self, inputs):
        self.state = inputs[self.inport]
        return self.state


class RandomRequest(AtomicDEVS):
    REQUEST_INTERVAL = 5

    def __init__(self, api):
        super().__init__("Request")
        self.api = api
        self.outport = self.addOutPort("output")

    def timeAdvance(self):
        return self.REQUEST_INTERVAL

    def outputFnc(self):
        return {self.outport: random.choice(("UP", "DOWN"))}


class Model(CoupledDEVS):
    def __init__(self, api):
        super().__init__("model")
        self.elevator = self.addSubModel(Elevator(api))
        self.request = self.addSubModel(RandomRequest(api))
        self.connectPorts(self.request.outport, self.elevator.inport)


model = Model(None)
sim = Simulator(model)
sim.setClassicDEVS()
sim.setTerminationTime(20.0)
sim.setVerbose()
sim.simulate()

