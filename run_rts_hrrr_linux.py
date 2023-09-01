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
    path_to_vortex_install = "/home/jlgutenson/vortex-0.11.0"
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
    download_met_data = False
    # where is the HEC-RAS install located?
    ras_directory = "/home/jlgutenson/HEC-RAS_610_Linux"
    # Are we running HEC-HMS as a forecast?
    forecast = True
    # where are all of the models stored? I stole this term of Will at HEC...
    model_library = "/home/jlgutenson/model_library"

    # list of watersheds we're going to run RTS for
    list_of_watersheds = ['RVD','IBWC','AC']

    # our dictionary that tell us where all the necessary data are
    watershed_vars_dict = {'RVD':{'hec_hms_clip_shp': "{0}/RVD/HMS/gis/RVD_83_1/RVD_83_1.shp".format(model_library),
                                  'vortex_dss_file' : "RVDJune2018_JLG_scripted_1.dss",
                                  'hms_model_directory' : "{0}/RVD/HMS".format(model_library),
                                  'hms_control_file_name' : "Forecast_1.forecast",
                                  'hms_project_file' : "RVD_NAD8310171.hms",
                                  'hms_run_name' : None,
                                  'hms_output_file': "Forecast_1.dss",
                                  'hms_forecast_name': "Forecast 1",
                                  'hec_ras_model_dir' : "{0}/RVD/RAS".format(model_library),
                                  'hec_ras_output_dir' : "hms_j4",
                                  'hec_ras_prj_file_name' : "RVD_TWDB1.prj",
                                  'hec_ras_plan_file_name' : "RVD_TWDB1.p32",
                                  },
                            'IBWC':{'hec_hms_clip_shp': "{0}/IBWC/HMS/gis/Basin_2/Basin_2.shp".format(model_library),
                                    'vortex_dss_file' : "HRRR_Forecast_IBWC.dss",
                                    'hms_model_directory' : "{0}/IBWC/HMS".format(model_library),
                                    'hms_control_file_name' : "Forecast_1.forecast",
                                    'hms_project_file' : "IBWC_GRID.hms",
                                    'hms_run_name' : None,
                                    'hms_output_file': "Forecast_1.dss",
                                    'hms_forecast_name': "Forecast 1",
                                    'hec_ras_model_dir' : None,
                                    'hec_ras_output_dir' : None,
                                    'hec_ras_prj_file_name' : None,
                                    'hec_ras_plan_file_name' : None,
                                    },
                            'AC':{'hec_hms_clip_shp': "{0}/IBWC/HMS/gis/Arroyo_Colorado/Arroyo_Colorado.shp".format(model_library),
                                  'vortex_dss_file' : "HRRR_Forecast_AC.dss",
                                  'hms_model_directory' : "{0}/AC/HMS".format(model_library),
                                  'hms_control_file_name' : "Forecast_1.forecast",
                                  'hms_project_file' : "AC4.8_RTS.hms",
                                  'hms_run_name' : None,
                                  'hms_output_file': "Forecast_1.dss",
                                  'hms_forecast_name': "Forecast 1",
                                  'hec_ras_model_dir' : None,
                                  'hec_ras_output_dir' : None,
                                  'hec_ras_prj_file_name' : None,
                                  'hec_ras_plan_file_name' : None,
                                 }
                          }

    for watershed in list_of_watersheds:
        print("Running {0}".format(watershed))
        # load our watershed variables
        vars_dict = watershed_vars_dict[watershed]

        # let's run HMS first
        start_date, end_date, met_dir = run_hms_hrrr.run(watershed,
                                                         simulation_length,
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
                                                         download_met_data,
                                                         forecast,
                                                         vars_dict['hms_forecast_name'],
                                                         vars_dict['hms_output_file'])
        

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
