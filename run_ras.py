# native imports
import os
import shutil
import sys
from datetime import datetime
import subprocess

def run(hec_ras_model_dir, 
        hec_ras_output_dir,
        hec_ras_prj_file_name,
        hec_ras_plan_file_name,
        start_date,
        end_date,
        ras_directory,
        met_dir
        ):

    # # where all the HEC-RAS model files are stored
    # hec_ras_model_dir = "C:\Users\Joseph Gutenson\Desktop\Gutenson_RATES\TWDB-FIF-LRGVDC\2023\1.2.2.2.2\Models\HEC_RAS\RVD_TWDB1"
    # # need this to delete previous output and also move new output
    # hec_ras_output_dir = "hms_j4"
    # # name of the HEC-RAS project (i.e., *.prj) file
    # hec_ras_prj_file_name = "RVD_TWDB1.prj"
    # # name of the HMS plan we're using to run the simulation
    # hec_ras_plan_file_name = "RVD_TWDB1.p32"

    # # declare forecast start date and end date
    # # will need to be in this format 28JUL2023,1900,29JUL2023,1200
    # start_date = datetime(2023, 8, 2, 14, 0)
    # end_date = datetime(2023, 8, 3, 7, 0)
    # for Linux, we need to specify the folder containing all of the HEC-RAS code
    # Windows users can set this to NONE
    # ras_directory = "/home/jlgutenson/HEC-RAS_610_Linux"
    # full path to the HEC-RAS Output Results
    # for Linux, we need to specify the folder where were sticking the .sh file
    # easy answer is to put it into the directory with the meterological data
    # Windows users can set this to None
    # for Linux, trying to install Wine to run this...
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
        print("Running HEC-RAS on Linux.\n")
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
    
    # running HEC-RAS is a bit different in a Linux environment
    # used guidance in HEC-RAS release notes to piece this together 
    # https://www.hec.usace.army.mil/software/hec-ras/documentation/HEC-RAS_610_Linux_Build_Release_Notes.pdf
    # Kleinschmidt Group gives a good breakdown of different file types
    # https://www.kleinschmidtgroup.com/ras-post/hec-ras-file-types/
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        # we're building the bat file that runs HEC-HMS in Windows here
        print("Running HEC-RAS on Linux.\n")
        ras_file_name = "hecras_{0}{1}{2}{3}.sh".format(start_date.year, 
                                                        start_date.strftime("%m"),
                                                        start_date.strftime("%d"),
                                                        start_date.strftime("%H"))
        ras_file = os.path.join(met_dir,ras_file_name)
        with open(ras_file, "w") as open_ras_file:
            string_to_write = 'RAS_LIB_PATH="{0}/RAS_Linux_test_setup/libs:{0}/RAS_Linux_test_setup/libs/mkl:{0}/RAS_Linux_test_setup/libs/rhel_8"'.format(str(ras_directory))
            open_ras_file.write(string_to_write)
            open_ras_file.write('\n')
            string_to_write = 'export LD_LIBRARY_PATH="$RAS_LIB_PATH:$LD_LIBRARY_PATH"'
            open_ras_file.write(string_to_write)
            open_ras_file.write('\n')
            string_to_write = 'RAS_EXE_PATH="{0}/RAS_Linux_test_setup/Ras_v61/Release"'.format(str(ras_directory))
            open_ras_file.write(string_to_write)
            open_ras_file.write('\n')
            string_to_write = 'export PATH="$RAS_EXE_PATH:$PATH"'
            open_ras_file.write(string_to_write)
            open_ras_file.write('\n')
            # string_to_write = 'rm {0}.hdf'.format(hec_ras_plan_file_path)
            # open_ras_file.write(string_to_write)
            # open_ras_file.write('\n')
            # string_to_write = 'rm {0}.tmp.hdf'.format(hec_ras_plan_file_path)
            # open_ras_file.write(string_to_write)
            # open_ras_file.write('\n')
            # string_to_write = 'rm {0}dss'.format(hec_ras_plan_file_path[:-3])
            # open_ras_file.write(string_to_write)
            # open_ras_file.write('\n')

            str_ras_projectpath = os.path.join(hec_ras_model_dir, hec_ras_prj_file_name)
            project_number = hec_ras_plan_file_path[-2:]
            # string_to_write = 'RasGeomPreprocess "{1}x{2}"'.format(str_ras_projectpath, hec_ras_plan_file_path[:-3], project_number)
            # open_ras_file.write(string_to_write)
            # open_ras_file.write('\n')
            string_to_write = 'RasUnsteady "{1}c07" "b{2}"'.format(str_ras_projectpath, hec_ras_plan_file_path[:-3], project_number)
            open_ras_file.write(string_to_write)
            open_ras_file.write('\n')
            open_ras_file.close()

            # Open the subprocess without creating a new window
            process = subprocess.Popen(ras_file, shell=True)
            stdout, stderr = process.communicate()
    
    print("HEC-RAS Simulation Complete")



    