# third party Java modules
from hms.model import Project
from hms import Hms

# native modules to add
import sys

if __name__ == "__main__":
    """
    This is a Jython 2.7 script that is utilizes Jython to run HEC-HMS. The script uses HEC-HMS and Jython. Functions as a command line script. 
    Currently works only for Ubuntu 20.04.

    Args:
        hms_project_file (str): Full path to the HEC-HMS project file.
        forecast (bol): Boolean telling the script whether to execute a HEC-HMS run or a forecast. If true, the script will execute a forecast.

    Returns:
        None
        
    """

    # The actual command line arguments start from index 1.
    # The first item in sys.argv is the name of the script itself (e.g., my_script.py).
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