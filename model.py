# -*- coding: utf-8 -*-

import random
import logging

from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY

from settings import NUMBER_OF_FLOORS

logging.basicConfig()
logger = logging.getLogger("Model")
logger.setLevel(logging.DEBUG)


class Elevator(AtomicDEVS):
    MOVE_TIME = 2

    def __init__(self, api):
        super().__init__("Elevator")
        self.api = api
        self.inport = self.addInPort("inport")
        self.outport = self.addOutPort("outport")
        self.state = "IDLE"
        self.floor = 0

    def timeAdvance(self):
        if self.state == "IDLE":
            return INFINITY
        if self.state in ("UP", "DOWN"):
            return self.MOVE_TIME

    def outputFnc(self):
        logger.info("Out: %s", self.floor)
        self.api.update_floor(self.floor)
        return {self.outport: self.floor}

    def intTransition(self):
        logger.info("Int: %s", self.floor)
        self.state = "IDLE"
        return self.state

    def extTransition(self, inputs):
        logger.info("Ext: %s", inputs.values())
        self.state = inputs[self.inport]
        if self.state == "UP":
            self.floor = self.floor + 1 if self.floor < NUMBER_OF_FLOORS else self.floor
        elif self.state == "DOWN":
            self.floor = self.floor - 1 if self.floor > 0 else self.floor
        return self.state


class ElevatorGO(AtomicDEVS):
    def __init__(self, api):
        super().__init__("ElevatorGO")
        self.api = api
        self.inport_go = self.addInPort("inport_go")
        self.inport_floor = self.addInPort("inport_floor")
        self.outport = self.addOutPort("outport")
        self.state = "IDLE"
        self.current_floor = 0
        self.last_stop = 0
        self.next_stop = 0

    def timeAdvance(self):
        if self.state == "IDLE":
            return INFINITY
        if self.state == "GO":
            return 0

    def outputFnc(self):
        logger.info("Out: %s -> %s", self.current_floor, self.next_stop)
        direction = "UP" if self.next_stop > self.current_floor else "DOWN"
        return {self.outport: direction}

    def intTransition(self):
        logger.info("Int: %s", self.current_floor)
        self.state = "IDLE"
        return self.state

    def extTransition(self, inputs):
        logger.info("Ext: %s", inputs.values())

        floor = inputs.get(self.inport_floor)
        if floor:
            self.current_floor = floor
            if self.next_stop == floor:
                self.state = "IDLE"
                self.api.clear_destination_floor()
            else:
                self.state = "GO"

        next_stop = inputs.get(self.inport_go)
        if next_stop:
            if self.state == "IDLE":
                if next_stop == self.current_floor:
                    pass
                else:
                    self.state = "GO"
                    self.next_stop = next_stop
                    self.api.set_destination_floor(next_stop)
            else:
                # TODO: new customer can't use elevator which is moving now
                pass
        return self.state


class RandomRequest(AtomicDEVS):
    REQUEST_INTERVAL = 19

    def __init__(self, api):
        super().__init__("Request")
        self.api = api
        self.outport = self.addOutPort("output")
        self.state = False

    def timeAdvance(self):
        self.state = True
        return self.REQUEST_INTERVAL

    def outputFnc(self):
        if self.state:
            return {self.outport: random.choice(range(NUMBER_OF_FLOORS))}


class Model(CoupledDEVS):
    def __init__(self, api):
        super().__init__("model")
        self.elevator = self.addSubModel(Elevator(api))
        self.elevator_go = self.addSubModel(ElevatorGO(api))
        self.request = self.addSubModel(RandomRequest(api))
        self.connectPorts(self.elevator_go.outport, self.elevator.inport)
        self.connectPorts(self.elevator.outport, self.elevator_go.inport_floor)
        self.connectPorts(self.request.outport, self.elevator_go.inport_go)


if __name__ == "__main__":

    class FakeGUI:
        def __getattr__(self, item):
            return lambda *args, **kwargs: True

    model = Model(FakeGUI())
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(50.0)
    sim.setVerbose()
    sim.simulate()
