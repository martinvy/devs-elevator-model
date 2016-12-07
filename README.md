# Model of elevator system using DEVS formalism
University project for course of Intelligent systems (SIN) at FIT VUT. 

**Contributors:**
- Martin Veselovsky, xvesel60
- Marek Dokulil, xdokul03
- Marek Skalnik, xskaln03

### Dependencies:
- **pypdevs**
	- Download from http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS/Tutorial/distribution.zip
	- Extract the file
    - Go into `pypdevs/src` and run `python setup.py install`

### Usage:
- `python gui.py` to create a window with graphical user interface
- `python model.py` to run simulation of elevator model with console output

### Settings:
- see `settings.py` and adjust parameters of the model.
- important parameter is `SIMULATION_REAL_TIME_SCALE` which sets how fast will the simulation run in the GUI
