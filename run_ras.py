# native imports
import os
import shutil
import sys
from datetime import datetime

# local imports


# list of variables that we'll later convert into a function
# where all the HEC-RAS model files are stored
hec_ras_model_dir = r"C:\Users\Joseph Gutenson\Desktop\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\1.2.2.2.2\Models\HEC_RAS\RVD_TWDB1"
# need this to delete previous output and also move new output
hec_ras_output_dir = "hms_j4"
# name of the HEC-RAS project (i.e., *.prj) file
hec_ras_prj_file_name = "RVD_TWDB1.prj"
# name of the HMS plan we're using to run the simulation
hec_ras_plan_file_name = "RVD_TWDB1.p32"

# declare forecast start date and end date
# will need to be in this format 28JUL2023,1900,29JUL2023,1200
start_date = datetime(2023, 8, 2, 14, 0)
end_date = datetime(2023, 8, 3, 7, 0)

if __name__ == '__main__':

    # full path to the HEC-RAS Output Results
    full_hec_ras_output_dir = os.path.join(hec_ras_model_dir,hec_ras_output_dir)

    # remove old outputs directory, if it exists
    if os.path.exists(full_hec_ras_output_dir):
        shutil.rmtree(full_hec_ras_output_dir)
    else:
        pass

    # need to update the date in the input files before we get too frisky
    # in our paradigm, that's just in the project's plan file
    hec_ras_plan_file_path = os.path.join(hec_ras_model_dir, hec_ras_plan_file_name)
    # Read lines using readlines()
    open_file = open(hec_ras_plan_file_path, 'r')
    Lines = open_file.readlines()
    open_file.close()
    # writing to file changing only the date in the plan file
    open_file = open(hec_ras_plan_file_path, 'w')
    for line in Lines:
        if line.startswith("Simulation Date="):
            line="Simulation Date={0}{1}{2},{3}00,{4}{5}{6},{7}00\n".format(start_date.strftime("%d"),
                                                                          start_date.strftime("%b").upper(),
                                                                          start_date.strftime("%Y"),
                                                                          start_date.strftime("%H"),
                                                                          end_date.strftime("%d"),
                                                                          end_date.strftime("%b").upper(),
                                                                          end_date.strftime("%Y"),
                                                                          end_date.strftime("%H"))
            open_file.writelines(line)
        else:
            open_file.writelines(line)
    open_file.close()

    # check what system you're using to figure out how to run HEC-RAS
    # lifted a lot of this from ras2fim here: https://github.com/NOAA-OWP/ras2fim/blob/dev/src/worker_fim_rasters.py
    if sys.platform == 'win32':
        # import the com client and find the HEC-RAS controller
        import win32com.client
        hec = win32com.client.Dispatch("RAS641.HECRASController")

        # open the HEC-RAS model 
        str_ras_projectpath = os.path.join(hec_ras_model_dir, hec_ras_prj_file_name)
        hec.Project_Open(str_ras_projectpath) 

        # to be populated: number and list of messages, blocking mode
        NMsg, TabMsg, block = None, None, True

        # computations of the current plan
        v1, NMsg, TabMsg, v2 = hec.Compute_CurrentPlan(NMsg, TabMsg, block)

        # close the HEC-RAS simulation
        hec.QuitRas()  # close HEC-RAS



    