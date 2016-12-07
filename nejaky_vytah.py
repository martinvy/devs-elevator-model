# -*- coding: utf-8 -*-

import sys
import random

# Import code for DEVS model representation:
from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY
from pypdevs.simulator import Simulator


POCET_PATER = 10


class Generator(AtomicDEVS):
    def __init__(self, api):
        super().__init__("Generator")
        self.api = api

        self.state = "IDLE" 

        self.elapsed = 0.0 

        self.BUTTON = self.addOutPort(name="BUTTON")
        #        self.INTERRUPT = self.addInPort(name="INTERRUPT")
        #        self.OBSERVED = self.addOutPort(name="OBSERVED")

#    def extTransition(self, inputs):
#        input = inputs.get(self.BUTTON)
#        

#    def intTransition(self):
#        input = 42
        
  
    def outputFnc(self):
        x = random.choice(range(POCET_PATER))
        print("Zavolani vytahu do " + str(x))
        return {self.BUTTON: x}
        #state = self.state.get()

        #if state == "red":
        #    return {self.OBSERVED: "grey"}
    
    def timeAdvance(self):
        return 14.33    
        #state = self.state.get()
        #       if state == "red":
        #           return INFINITY 





class Elevator(AtomicDEVS):
    def __init__(self, api):
        super().__init__("Elevator")
        self.api = api


        self.seznam_tlacitek = []
        for i in range(POCET_PATER):
          self.seznam_tlacitek.append(0)
        self.aktualni_patro = 0
       
        self.state = "IDLE" 

        self.elapsed = 0.0 


        self.BUTTON = self.addInPort(name="BUTTON")
        #        self.INTERRUPT = self.addInPort(name="INTERRUPT")
        #        self.OBSERVED = self.addOutPort(name="OBSERVED")

    def extTransition(self, inputs):
        input = inputs.get(self.BUTTON)
        
        self.seznam_tlacitek[input] = 1
        
        if self.state == "IDLE":
            if self.aktualni_patro < input:
                return "UP"
            elif self.aktualni_patro > input:
                return "DOWN"
            else:
                return "OPEN"
        return self.state
        #state = self.state.get()

        #if input == "toManual":
        #    if state == "manual":
        #        return TrafficLightMode("manual")


    def intTransition(self):

        if "UP" in self.state:
            self.aktualni_patro = self.aktualni_patro + 1
            print("prijizdi do " + str(self.aktualni_patro))
            if self.seznam_tlacitek[self.aktualni_patro] == 1:
                self.seznam_tlacitek[self.aktualni_patro] = 0
                return "U_OPEN"
            else:
                return "UP"+str(self.aktualni_patro)
        if "DOWN" in self.state:
            self.aktualni_patro = self.aktualni_patro - 1
            print("prijizdi do " + str(self.aktualni_patro))
            if self.seznam_tlacitek[self.aktualni_patro] == 1:
                self.seznam_tlacitek[self.aktualni_patro] = 0
                return "D_OPEN"
            else:
                return "DOWN"+str(self.aktualni_patro)
        if self.state == "OPEN":
            return "U_CLOSE"
        if self.state == "U_OPEN":
            return "U_CLOSE"
        if self.state == "D_OPEN":
            return "D_CLOSE"
        
        
        if self.state == "U_CLOSE":
            if self.seznam_tlacitek[self.aktualni_patro] == 1:
                self.seznam_tlacitek[self.aktualni_patro] = 0
                return "U_OPEN"     
            for i in range(self.aktualni_patro, POCET_PATER):
                if self.seznam_tlacitek[i] == 1:
                  return "UP"
            for i in range(0, self.aktualni_patro):
                if self.seznam_tlacitek[i] == 1:
                  return "DOWN"
            return "IDLE"
        if self.state == "D_CLOSE":
            if self.seznam_tlacitek[self.aktualni_patro] == 1:
                self.seznam_tlacitek[self.aktualni_patro] = 0
                return "D_OPEN"     
            for i in range(0, self.aktualni_patro):
                if self.seznam_tlacitek[i] == 1:
                  return "DOWN"
            for i in range(self.aktualni_patro, POCET_PATER):
                if self.seznam_tlacitek[i] == 1:
                  return "UP"
            return "IDLE"        
        return self.state
        #input = 42
        
        #state = self.state.get()

        #if state == "red":
        #    return TrafficLightMode("green")

  
    #def outputFnc(self):
        #input = 42
        #state = self.state.get()

        #if state == "red":
        #    return {self.OBSERVED: "grey"}
    
    def timeAdvance(self):
        if "UP" in self.state:
            return 10
        if "DOWN" in self.state:
            return 10
        if "OPEN" in self.state:
            return 5
        if "CLOSE" in self.state:
            return 1
        return INFINITY    
        #state = self.state.get()
        #       if state == "red":
        #           return INFINITY 




class Model(CoupledDEVS):
    def __init__(self, api):
        super().__init__("model")
        self.elevator = self.addSubModel(Elevator(api))
        self.request = self.addSubModel(Generator(api))
        #self.elevator_go = self.addSubModel(ElevatorGO(api))
        #self.request = self.addSubModel(RandomRequest(api))
        self.connectPorts(self.request.BUTTON, self.elevator.BUTTON)
        #self.connectPorts(self.elevator.outport, self.elevator_go.inport_floor)
        #self.connectPorts(self.request.outport, self.elevator_go.inport_go)


if __name__ == "__main__":

    class FakeGUI:
        def __getattr__(self, item):
            return lambda *args, **kwargs: True

    model = Model(FakeGUI())
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(150.0)
    sim.setVerbose()
    sim.simulate()