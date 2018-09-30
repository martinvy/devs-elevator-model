# Model of elevator system using DEVS

DEVS, Discrete Event System Specification, is a modular and hierarchical formalism for modeling and analyzing general systems.

This project implements simple elevator, which collects passengers along the way if they want to go in the same direction as the elevator goes at the moment.
If they want to go in the opposite direction, elevator will return to the floor as soon as it finishes current journey.

### Install
Create Python virtual environment
```
python3 -m venv .venv
source .venv/bin/activate
```

Dependencies:
 - **tkinter** for displaying the GUI, tk must be installed on the system (`sudo apt-get install python3-tk`).
 - **pypdevs** for DEVS model and simulation of the Elevator system 
	- download library from http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS/Tutorial/distribution.zip
	- unzip the file, go to `distribution/pypdevs/src`
	- and install the library via `python setup.py install`

Settings:
 - see `settings.py` and adjust parameters of the model.
 - important parameter is `SIMULATION_REAL_TIME_SCALE` which sets how fast will the simulation run in the GUI

### Usage
- `python gui.py` to display the window with graphical user interface
- `python model.py` to run simulation of elevator model with only console output

### Note
The project was created as team homework within lessons of Intelligent systems (SIN) at Faculty of Information Technology, Brno University of Technology, 2016.
Team consisted of Martin Veselovsky, Marek Dokulil and Marek Skalnik.
