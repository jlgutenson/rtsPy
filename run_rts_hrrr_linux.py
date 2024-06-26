# built in imports
import os
from datetime import datetime, timezone, timedelta

# local imports
import run_hms_hrrr
from data_retrieval_scripts.STOFS3D_Stage_Download import get_stofs3d
import flood_inundation_mapping
import cleaner

import run_ras

if __name__ == "__main__":

        # variables that will be constant for all watersheds
        # length of the simulation, in hours
        simulation_length = 18
        # specify how long each forecast will stick around, in days
        forecast_age_to_filter = 30
        # path to folder where each hours MRMS data will be downloaded
        name_of_gridded_directory = "/home/jlgutenson/rtspy/hrrr_subhourly" # name of the directory storing each forecast
        # name_of_gridded_directory = "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/hrrr_subhourly" # name of the directory storing each forecast
        # path to the folder containing the Vortex install, the HEC tool for converted gridded data into DSS format
        path_to_vortex_install = "/home/jlgutenson/vortex-0.11.0"
        # path to Jython executable
        path_to_jython_install = "/home/jlgutenson/jython-standalone-2.7.3.jar"
        # path to the HEC-HMS directory
        hms_directory = "/home/jlgutenson/HEC-HMS-4.11"
        # path to the HEC-DssVue installed on your machine
        path_to_dssvue_install = "/home/jlgutenson/hec-dssvue-3.3.26"
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
        # Are we running HEC-HMS as a forecast?
        forecast = True
        # where are all of the models stored? I stole this term of Will at HEC...
        model_library = "/home/jlgutenson/model_library"
        # should I delete the grib forecast files? They're big!
        delete_gribs = True
        # where are the scripts were executing (for cron jobs)
        cwd = '/home/jlgutenson/rtspy'
        # cwd = os.getcwd()
        # should I download the STOFS-3D-Atlantic data?
        download_stofs_data = True
        # what STOFS-3D-Atlantic file format should I download?
        file_format_for_stofs = "grib2"
        # where are we storing the STOFS forecasts?
        name_of_stofs_directory = "/home/jlgutenson/rtspy/stofs3d_daily"
        # name_of_stofs_directory = "/mnt/d/Gutenson_RATES/TWDB-FIF-LRGVDC/2023/Scripts/build_hms_inputs/stofs3d_daily"

        # list of watersheds we're going to run RTS for
        list_of_watersheds = ['RVD','IBWC','AC','BSC','HWMD']
        # list_of_watersheds = ['IBWC']

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
                                        'station_assimilation_list': [],
                                        'lat_of_boundary': 26.502514,
                                        'lon_of_boundary': -97.402596,
                                        'dem_path': "{0}/RVD/HMS/terrain/Terrain_2.elevation.tif".format(model_library),
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
                                        'station_assimilation_list': ["08470200", "TWDB 3"],
                                        'lat_of_boundary': 26.397862,
                                        'lon_of_boundary': -97.366219,
                                        'dem_path': "{0}/IBWC/HMS/terrain/Terrain_2.elevation.tif".format(model_library),
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
                                        'station_assimilation_list': [],
                                        'lat_of_boundary': 26.362558,
                                        'lon_of_boundary': -97.327534,
                                        'dem_path': "{0}/AC/HMS/terrain/Terrain_1.elevation.tif".format(model_library),
                                        },
                                'BSC':{'hec_hms_clip_shp': "{0}/IBWC/HMS/gis/Basin_1/BSC.shp".format(model_library),
                                        'vortex_dss_file' : "HRRR_Forecast_BSC.dss",
                                        'hms_model_directory' : "{0}/BSC/HMS".format(model_library),
                                        'hms_control_file_name' : "Forecast_1.forecast",
                                        'hms_project_file' : "BSC_1.hms",
                                        'hms_run_name' : None,
                                        'hms_output_file': "Forecast_1.dss",
                                        'hms_forecast_name': "Forecast 1",
                                        'hec_ras_model_dir' : None,
                                        'hec_ras_output_dir' : None,
                                        'hec_ras_prj_file_name' : None,
                                        'hec_ras_plan_file_name' : None,
                                        'station_assimilation_list': [],
                                        'lat_of_boundary': 26.056447,
                                        'lon_of_boundary': -97.188190,
                                        'dem_path': "{0}/BSC/HMS/terrain/Terrain_1.elevation.tif".format(model_library),
                                        },
                                'HWMD':{'hec_hms_clip_shp': "{0}/IBWC/HMS/gis/Basin_1/HWMD.shp".format(model_library),
                                        'vortex_dss_file' : "HRRR_Forecast_HWMD.dss",
                                        'hms_model_directory' : "{0}/HWMD/HMS".format(model_library),
                                        'hms_control_file_name' : "Forecast_1.forecast",
                                        'hms_project_file' : "HWMD2.hms",
                                        'hms_run_name' : None,
                                        'hms_output_file': "Forecast_1.dss",
                                        'hms_forecast_name': "Forecast 1",
                                        'hec_ras_model_dir' : None,
                                        'hec_ras_output_dir' : None,
                                        'hec_ras_prj_file_name' : None,
                                        'hec_ras_plan_file_name' : None,
                                        'station_assimilation_list': [],
                                        'lat_of_boundary': 26.467848,
                                        'lon_of_boundary': -97.395641,
                                        'dem_path': "{0}/HWMD/HMS/terrain/Terrain_1.elevation.tif".format(model_library),
                                        },
                                }

        for watershed in list_of_watersheds:
                print("Running {0}".format(watershed))

                # load our watershed variables
                vars_dict = watershed_vars_dict[watershed]

                # clear out old HEC-HMS forecasts
                cleaner.remove_old_forecasts(name_of_gridded_directory, watershed, vars_dict['hms_forecast_name'], forecast_age_to_filter)

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
                                                                vars_dict['hms_output_file'],
                                                                path_to_dssvue_install,
                                                                vars_dict['station_assimilation_list'],
                                                                cwd
                                                                )


                # now let's turn off meteorological forecast downloads to save time
                download_met_data = False

                # download the coastal boundary (this only updates once a day at the moment at 1900 UTC)
                current_time = datetime.now(timezone.utc)
                cycle = int(current_time.strftime("%-H"))
                if cycle == 19:
                        coastal_boundary_dss_path, coastal_dir, max_wse = get_stofs3d(watershed, 
                                                                                      vars_dict['lat_of_boundary'], 
                                                                                      vars_dict['lon_of_boundary'], 
                                                                                      name_of_stofs_directory, 
                                                                                      download_stofs_data,
                                                                                      file_format_for_stofs, 
                                                                                      path_to_dssvue_install, 
                                                                                      path_to_jython_install, 
                                                                                      cwd)

                        # now let's turn off tidal and surge forecast downloads to save time
                        download_stofs_data = False

                        # use the maximum water surface elevation forecast to estimate a flood inundation map
                        flood_inundation_raster_path = flood_inundation_mapping.with_max_wse(watershed, vars_dict['dem_path'], max_wse, coastal_dir)



                # now let's run HEC-RAS with our HMS streamflow forecast
                # run_ras.run(vars_dict['hec_ras_model_dir'], 
                #             vars_dict['hec_ras_output_dir'],
                #             vars_dict['hec_ras_prj_file_name'],
                #             vars_dict['hec_ras_plan_file_name'],
                #             start_date,
                #             end_date,
                #             ras_directory,
                #             met_dir)

        if delete_gribs is True:
                for file in os.listdir(met_dir):
                        if file.endswith(".grib2"):
                                os.remove(os.path.join(met_dir,file))
                        elif file.endswith(".gbx9"):
                                os.remove(os.path.join(met_dir,file))
                        elif file.endswith(".ncx4"):
                                os.remove(os.path.join(met_dir,file))
                if cycle == 20:
                        for file in os.listdir(coastal_dir):
                                if file.endswith(".grib2"):
                                        os.remove(os.path.join(coastal_dir,file))
                                elif file.endswith(".idx"):
                                        os.remove(os.path.join(coastal_dir,file))
                                elif file.endswith(".nc"):
                                        os.remove(os.path.join(coastal_dir,file))

