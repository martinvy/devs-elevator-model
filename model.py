# -*- coding: utf-8 -*-
"""
Model of elevator system using DEVS formalism.
Model is coupled DEVS consisting of two atomic DEVS components.

Usage: python model.py
"""

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
    """
    Simple elevator model capable of moving one floor up or down.
    Interface:
        input: UP / DOWN command
        output: number of the current floor
    """

    def __init__(self, api):
        """
        :param api: reference to the GUI
        """
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
            return ONE_FLOOR_MOVING_TIME

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
    """
    Elevator model capable of moving to specified floor.
    Elevator stops on the floors by the way to original destination
    if customers intend to go in the same direction.
    Interface:
        input: internal floor button (buttons inside the elevator)
               external floor button up / down (buttons on the floors)
               current floor update from Simple Elevator
        output: one floor up / down request for Simple Elevator
    """
    def __init__(self, api):
        """
        :param api: reference to the GUI
        """
        super().__init__("ElevatorGO")
        self.api = api
        self.inport_go = self.addInPort("inport_go")
        self.inport_go_external_up = self.addInPort("inport_go_external_up")
        self.inport_go_external_down = self.addInPort("inport_go_external_down")
        self.inport_floor_update = self.addInPort("inport_floor_update")
        self.outport_updown_request = self.addOutPort("outport_updown_request")
        self.state = "IDLE"
        self.current_floor = 0
        self.last_stop = 0
        self.next_stop = 0
        self.request_queue = []

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
        if self.state == "CHECK_REQUEST_QUEUE":  # check queued requests and initiate new move if any
            return 0

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
            self.state = "CHECK_REQUEST_QUEUE"
            self.api.closed_doors(self.current_floor)
        elif self.state == "CHECK_REQUEST_QUEUE":
            if self.request_queue:
                self.move(self.request_queue.pop(0))
            else:
                self.state = "IDLE"
        elif self.state == "GO":
            self.state = "GOING"
            self.api.set_destination_floor(self.next_stop)
        return self.state

    def extTransition(self, inputs):
        logger.info("GO Ext: %s", inputs.values())

        # floor update (from Elevator)
        floor = inputs.get(self.inport_floor_update)
        if floor is not None:
            self.current_floor = floor
            if self.next_stop == floor:
                self.state = "OPENING"
            else:
                assert self.state == "GOING"
                self.state = "GO"

        # go request (internal button)
        next_stop = inputs.get(self.inport_go)
        if next_stop is not None:
            next_stop = self.cast_from_interrupt(next_stop)

            if self.state == "IDLE":
                self.move(next_stop)
            else:
                logger.info("GO queued %s", next_stop)
                self.request_queue.append(next_stop)

        # go request UP (external button)
        next_stop = inputs.get(self.inport_go_external_up)
        if next_stop is not None:
            next_stop = self.cast_from_interrupt(next_stop)

            if self.state == "IDLE":
                self.move(next_stop)
            else:
                if self.elevator_is_rising():
                    logger.info("GO original dest floor queued %s", next_stop)
                    self.request_queue.append(self.next_stop)
                    self.next_stop = next_stop

        # go request DOWN (external button)
        next_stop = inputs.get(self.inport_go_external_down)
        if next_stop is not None:
            next_stop = self.cast_from_interrupt(next_stop)

            if self.state == "IDLE":
                self.move(next_stop)
            else:
                if self.elevator_is_dropping():
                    logger.info("GO original dest floor queued %s", next_stop)
                    self.request_queue.append(self.next_stop)
                    self.next_stop = next_stop

        self.api.update_request_queue(self.request_queue)
        return self.state

    def elevator_is_rising(self):
        return self.next_stop > self.current_floor

    def elevator_is_dropping(self):
        return self.next_stop < self.current_floor

    @staticmethod
    def cast_from_interrupt(var):
        """ External transition from simulation interrupt is list for some reason """
        if isinstance(var, list):
            return int(var[0])
        return var

    def move(self, next_stop):
        logger.info("GO move %s", next_stop)
        if next_stop == self.current_floor:
            self.state = "OPENING"
        else:
            self.state = "GO"
            self.next_stop = next_stop


class RandomRequest(AtomicDEVS):
    """
    Random request generator for simulation purposes.
    """
    REQUEST_INTERVAL = 50

    def __init__(self, api):
        """
        :param api: reference to the GUI
        """
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
    """
    Coupled DEVS component connecting Elevator and ElevatorGO atomic DEVS components.
    For simulation purposes RandomRequest generator is connected to the ElevatorGO.
    """
    def __init__(self, api):
        super().__init__("model")
        self.elevator = self.addSubModel(Elevator(api))
        self.elevator_go = self.addSubModel(ElevatorGO(api))
        self.request = self.addSubModel(RandomRequest(api))
        self.connectPorts(self.elevator_go.outport_updown_request, self.elevator.inport)
        self.connectPorts(self.elevator.outport, self.elevator_go.inport_floor_update)
        self.connectPorts(self.request.outport, self.elevator_go.inport_go)

    def select(self, imm_children):
        """ On conflict prefer trasition on ElevatorGO """
        return imm_children[1]


# if this file is directly executed via `python model.py` simulate the model
# in fast simulation time. `api` param is set to the FakeGUI because model performs
# GUI update callback in various places

if __name__ == "__main__":

    class FakeGUI:
        def __getattr__(self, item):
            return lambda *args, **kwargs: True

    model = Model(FakeGUI())
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(200.0)
    sim.setVerbose()
    sim.simulate()
