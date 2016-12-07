# -*- coding: utf-8 -*-

import random
import logging

from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.simulator import Simulator
from pypdevs.infinity import INFINITY

from settings import *

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
        logger.info("EL Out: %s", self.floor)
        self.api.update_floor(self.floor)
        return {self.outport: self.floor}

    def intTransition(self):
        logger.info("EL Int: %s", self.floor)
        self.state = "IDLE"
        return self.state

    def extTransition(self, inputs):
        logger.info("EL Ext: %s", inputs.values())
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
        self.inport_floor_update = self.addInPort("inport_floor_update")
        self.outport_updown_request = self.addOutPort("outport_updown_request")
        self.state = "IDLE"
        self.current_floor = 0
        self.last_stop = 0
        self.next_stop = 0

    def timeAdvance(self):
        if self.state == "IDLE":   # waits for button request
            return INFINITY
        if self.state == "GOING":  # waits for floor update
            return INFINITY
        if self.state == "GO":  # perform UP or DOWN request to elevator and switch state to GOING
            return 0
        if self.state == "IS_OPENED":  # doors are open, switch to CLOSING
            return OPENING_TIME
        if self.state == "IS_CLOSED":  # doora are now CLOSING, after timeout switch to IS_CLOSED, then immediately to IDLE
            return CLOSING_TIME
        if self.state == "OPENING":  # immediately start opening the doors, switch to IS_OPENED
            return 0
        if self.state == "CLOSING":  # plan to switch to CLOSING state after timeout of IS_OPENED state
            return OPENED_FOR_TIME

    def outputFnc(self):
        logger.info("GO Out: %s -> %s", self.current_floor, self.next_stop)
        if self.state == "GO":
            if self.next_stop > self.current_floor:
                direction = "UP"
            else:
                direction = "DOWN"
            return {self.outport_updown_request: direction}
        return {}

    def intTransition(self):
        logger.info("GO Int: %s", self.current_floor)
        if self.state == "IS_OPENED":
            self.state = "CLOSING"
            self.api.opened_doors(self.current_floor)
        elif self.state == "OPENING":
            self.state = "IS_OPENED"
            self.api.opening_doors(self.current_floor)
        elif self.state == "CLOSING":
            self.state = "IS_CLOSED"
            self.api.closing_doors(self.current_floor)
        elif self.state == "IS_CLOSED":
            self.state = "IDLE"
            self.api.closed_doors(self.current_floor)
        elif self.state == "GO":
            self.state = "GOING"
            self.api.set_destination_floor(self.next_stop)
        return self.state

    def extTransition(self, inputs):
        logger.info("GO Ext: %s", inputs.values())

        floor = inputs.get(self.inport_floor_update)
        if floor:
            self.current_floor = floor
            if self.next_stop == floor:
                self.state = "OPENING"
            else:
                assert self.state == "GOING"
                self.state = "GO"

        next_stop = inputs.get(self.inport_go)
        if next_stop:
            # external transition from simulation interrupt is list for some reason
            if isinstance(next_stop, list):
                next_stop = int(next_stop[0])

            if self.state == "IDLE":
                if next_stop == self.current_floor:
                    self.state = "OPEN"
                else:
                    self.state = "GO"
                    self.next_stop = next_stop
            else:
                # TODO: new customer can't use elevator which is moving now
                pass
        return self.state


class RandomRequest(AtomicDEVS):
    REQUEST_INTERVAL = 30

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


class ButtonRequest(AtomicDEVS):
    def __init__(self, api):
        super().__init__("ButtonRequest")
        self.api = api
        self.inport_Extbutton = self.addInPort("inport_Extbutton")
        self.inport_Intbutton = self.addInPort("inport_Intbutton")
        self.inport_Floor = self.addInPort("inport_Floor")
        self.outport = self.addOutPort("outport_GoFloor")
        self.state = "IDLE"
        self.all_floor = []
        self.go_to_floor = 0

    def timeAdvance(self):
        return INFINITY

    def outputFnc(self):
        if self.state == "GO_TO":
            return {self.outport: self.go_to_floor}

    def intTransition(self):
        logger.info("Int: %s", self.floor)
        self.state = "IDLE"
        return self.state

    def extTransition(self, inputs):
        logger.info("Ext: %s", inputs.values())
        ext_button = inputs.get(self.inport_Extbutton)
        if ext_button:
            self.ExtButton = ext_button
            self.floor = inputs.get(self.inport_Floor)
            if self.state == "IDLE":
                self.all_floor.clear()
                self.all_floor.append(self.ExtButton % 10)
                self.state = "GO_TO"
            elif self.state == "MOVING":
                if self.floor == self.go_to_floor:
                    if len(self.all_floor) == 0:
                        self.state = "IDLE"
                    else:
                        self.state = "GO_TO"
                if self.floor < self.all_floor[0]:
                    if self.ExtButton/10 == 1 and self.ExtButton % 10 < self.all_floor[0]:
                        self.all_floor.append(self.ExtButton % 10)
                        self.state = "GO_TO"
                    else:
                        self.all_floor.append(self.ExtButton % 10)
                elif self.floor > self.all_floor[0]:
                    if self.ExtButton / 10 == 2 and self.ExtButton % 10 > self.all_floor[0]:
                        self.all_floor.append(self.ExtButton % 10)
                        self.state = "GO_TO"
                    else:
                        self.all_floor.append(self.ExtButton % 10)
                self.state = "GO_TO"
            elif self.state == "GO_TO":
                if max(self.all_floor) < self.floor:
                    self.go_to_floor = max(self.all_floor)
                    self.all_floor.remove(max(self.all_floor))
                elif min(self.all_floor) > self.floor:
                    self.go_to_floor = min(self.all_floor)
                    self.all_floor.remove(min(self.all_floor))
                self.state = "MOVING"
            return self.state


class Model(CoupledDEVS):
    def __init__(self, api):
        super().__init__("model")
        self.elevator = self.addSubModel(Elevator(api))
        self.elevator_go = self.addSubModel(ElevatorGO(api))
        self.request = self.addSubModel(RandomRequest(api))
        self.connectPorts(self.elevator_go.outport_updown_request, self.elevator.inport)
        self.connectPorts(self.elevator.outport, self.elevator_go.inport_floor_update)
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
