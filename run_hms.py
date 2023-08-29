# third party Java modules
from hms.model import Project
from hms import Hms

# native modules to add
import sys

if __name__ == "__main__":

    # The actual command line arguments start from index 1.
    # The first item in sys.argv is the name of the script itself (e.g., my_script.py).
    # list of variables that we'll eventually convert to inputs in a function.
    hms_project_file = sys.argv[1]
    forecast = sys.argv[3]

    if forecast == "False":
        print("Running a HMS run...")
        hms_run = sys.argv[2]
        myProject = Project.open(hms_project_file)
        myProject.computeRun(hms_run)
        myProject.close()
    elif forecast == "True":
        print("Running a HMS Forecast...")
        hms_forecast = sys.argv[2]
        print(hms_forecast)
        myProject = Project.open(hms_project_file)
        myProject.computeForecast(hms_forecast)
        myProject.close()
        
    Hms.shutdownEngine()