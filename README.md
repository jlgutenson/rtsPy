# rtsPy
A Python library for simulating the HEC-RTS workflow. 
## Set-up Instructions for Linux
Currently, the workflow is dependent upon Ubuntu 20.04 as its operating system.
1. Install [Miniconda for Linux](https://docs.conda.io/projects/miniconda/en/latest/).
2. If not already installed, install libgfortan5 on your machine for using HEC-DSSVue.
```
sudo apt-get update 
sudo apt-get install libgfortran5
```
3. Use the [provided yml file](https://github.com/jlgutenson/rtsPy/blob/main/pyrts_py39_jdk17.yml) to create your conda environment.
4. Make the appopriate references to the data and models in run_rts_hrrr_linux.py.
5. If automating your set-up, edit the crontab on your machine (run ```sudo crontab -e``` or edit the crontab directly by running the command ```sudo vim /etc/crontab```). Point the crontab to your conda environment's Python executable and your run_rts_hrrr_linux.py script.

Congratulations! You should now have an automated instance of HEC-RTS running for your watersheds.
