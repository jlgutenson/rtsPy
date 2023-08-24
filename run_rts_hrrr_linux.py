# local imports
import run_hms_hrrr
import run_ras

if __name__ == "__main__":

    # variables that will be constant for all watersheds
    # length of the simulation, in hours
    simulation_length = 18
    # path to folder where each hours MRMS data will be downloaded
    name_of_gridded_directory = "hrrr_subhourly" # name of the directory storing each forecast
    # path to the folder containing the Vortex install, the HEC tool for converted gridded data into DSS format
    path_to_vortex_install = "/home/jlgutenson/Vortex/build/distributions/vortex-0.12.0-dev.0.uncommitted+60a63fa"
    # path to Jython executable
    path_to_jython_install = "/home/jlgutenson/jython-standalone-2.7.3.jar"
    # path to the HEC-HMS directory
    hms_directory = "/home/jlgutenson/HEC-HMS-4.11"
    # type of meteorological data we're using
    met_forcing = "HRRR"
    # variable in the meteorlogy data containing precipitation
    variables = 'Total_precipitation_surface_15_Minute_Accumulation'
    # the time-step of the HEC-HMS simulation, in minutes
    hms_time_step = 15
    # do we need to download the met data to create the DSS file?
    download_met_data = True
    # where is the HEC-RAS install located?
    ras_directory = "/home/jlgutenson/HEC-RAS_610_Linux"

    # list of watersheds we're going to run RTS for
    list_of_watersheds = ['RVD']

    # our dictionary that tell us where all the necessary data are
    watershed_vars_dict = {'RVD':{'hec_hms_clip_shp': "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/1.2.2.2.2/Models/HEC_HMS_411beta16/1_RVD/1_HEC-HMS_Model/RVD_NAD8310171/gis/RVD_83_1/RVD_83_1.shp",
                                  'vortex_dss_file' : "RVDJune2018_JLG_scripted_1.dss",
                                  'hms_model_directory' : "/mnt/c/Users/Joseph Gutenson/Desktop/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/1.2.2.2.2/Models/HEC_HMS_411beta16/1. RVD/1. HEC-HMS Model/RVD_NAD8310171",
                                  'hms_control_file_name' : "June2018.control",
                                  'hms_project_file' : "RVD_NAD8310171.hms",
                                  'hms_run_name' : "June 2018",
                                  'hms_output_file': "June_2018.dss",
                                  'hec_ras_model_dir' : "/mnt/c/Users/Joseph Gutenson/Desktop/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/1.2.2.2.2/Models/HEC_RAS/RVD_TWDB1",
                                  'hec_ras_output_dir' : "hms_j4",
                                  'hec_ras_prj_file_name' : "RVD_TWDB1.prj",
                                  'hec_ras_plan_file_name' : "RVD_TWDB1.p32",
                                  }
                          }

    for watershed in list_of_watersheds:
        # load our watershed variables
        vars_dict = watershed_vars_dict[watershed]

        # let's run HMS first
        start_date, end_date, met_dir = run_hms_hrrr.run(simulation_length,
                                                name_of_gridded_directory,
                                                path_to_vortex_install, 
                                                path_to_jython_install,
                                                vars_dict['hec_hms_clip_shp'], 
                                                vars_dict['vortex_dss_file'],
                                                met_forcing,
                                                variables,
                                                vars_dict['hms_model_directory'], 
                                                vars_dict['hms_control_file_name'],
                                                hms_time_step,
                                                hms_directory, 
                                                vars_dict['hms_project_file'],
                                                vars_dict['hms_run_name'],
                                                download_met_data)

        # now let's turn off meteorological forecast downloads to save time
        download_met_data = False

        # now let's run HEC-RAS with our HMS streamflow forecast
        # run_ras.run(vars_dict['hec_ras_model_dir'], 
        #             vars_dict['hec_ras_output_dir'],
        #             vars_dict['hec_ras_prj_file_name'],
        #             vars_dict['hec_ras_plan_file_name'],
        #             start_date,
        #             end_date,
        #             ras_directory,
        #             met_dir)
