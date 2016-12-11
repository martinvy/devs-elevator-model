# Model of elevator system using DEVS formalism
University project for course of Intelligent systems (SIN) at FIT VUT. 

**Contributors:**
- Martin Veselovsky, xvesel60
- Marek Dokulil, xdokul03
- Marek Skalnik, xskaln03

### Install:
- Run `make install`
- Dependencies:
	-   **tkinter** for displaying the GUI window (tk must be installed on the system `sudo apt-get install python3-tk`)
	
	-   **pypdevs** for DEVS model and simulation of the Elevator system 
	(library has to be downloaded from http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS/Tutorial/distribution.zip and installed via `python setup.py install` - see INSTALL script for more info)


### Usage:
- Run `make run` to display the window
- Alternatively: 
	-   `python gui.py` to display the window with graphical user interface
	
	-   `python model.py` to run simulation of elevator model with only console output


### Settings:
- see `settings.py` and adjust parameters of the model.
- important parameter is `SIMULATION_REAL_TIME_SCALE` which sets how fast will the simulation run in the GUI
