# rtsPy
A Python library for simulating the HEC-RTS workflow. 

The current paradigm for this workflow is that the models and linkages between models and data have been completed using each model's graphical user interface (GUI). This workflow is just the straw that stirs your modeling drink. 

The workflow currently utilizes the [High-Resolution Rapid Refresh (HRRR)](https://rapidrefresh.noaa.gov/hrrr/) forecast guidance that provides 15-minute time step precipitation estimates at a 3-km horizontal resolution and updates hourly. 

## Set-up Instructions for Linux     
Currently, the workflow is dependent upon Ubuntu 20.04 as its operating system.
1. Install [Miniconda for Linux](https://docs.conda.io/projects/miniconda/en/latest/).
2. If not already installed, install libgfortan5 on your machine for using HEC-DSSVue.
```
sudo apt-get update 
sudo apt-get install libgfortran5
```
3. Use the [provided yml file](https://github.com/jlgutenson/rtsPy/blob/main/pyrts_py39_jdk17.yml) to create your conda environment.
4. Use ```wget``` to download and extract the following Linux versions of the HEC software suite

  - [HEC-DSSVue version 3.3.26](https://www.hec.usace.army.mil/software/hec-dssvue/downloads.aspx)

  - [HEC-HMS version 4.11](https://www.hec.usace.army.mil/software/hec-hms/downloads.aspx)

  - [Vortex version 0.11.x](https://github.com/HydrologicEngineeringCenter/Vortex) - You will currently need to build Vortex from the source code. HEC hasn't released a new Linux version. The previous version had GDAL issues.

  - [HEC-RAS version 6.1.0](https://www.hec.usace.army.mil/software/hec-ras/download.aspx) - This isn't used in the current workflow (as of September 21, 2023). 

5. Make the appopriate references to the data and models in ```run_rts_hrrr_linux.py```.
6. If automating your set-up, edit the crontab on your machine (run ```sudo crontab -e``` or edit the crontab directly by running the command ```sudo vim /etc/crontab```). Point the crontab to your conda environment's Python executable and your run_rts_hrrr_linux.py script.

Congratulations! You should now have an automated instance of HEC-RTS running for your watersheds.

## What's going on in the ```run_rts_hrrr_linux.py``` script
```run_rts_hrrr_linux.py``` is an example of how one can utilize the current workflow to automate HEC-RTS simulations in the cloud. 

The file provides instructions on how to run the simulations, such as whether to download the forecast or where the HEC-HMS is installed locally. The file also illustrates how one can use a Python dictionary to create a profile for each watershed's suite of model instances. 

## References
Gutenson, J. L., Santos, I., Navarro, L., Ernest, A. N. S., Kirkey, W., Fuller, C., Lehman, W. P., & Brauer, T. A. (2024, May). A Case Study of How the Hydrologic Engineering Center (HEC) Suite of Tools Can Be Deployed to Perform Automated Forecasting. World Environmental and Water Resources Congress 2024. https://doi.org/10.1061/9780784485477.04

## Funding
This work was funded by the Texas Water Development Board (TWDB) Flood Infrastructure Fund (FIF) under TWDB Commitment No. G1001288.
