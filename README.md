# sbas_snap2stamps 1.0 

Python scripts for SBAS pre-processing in SNAP




BTW:

https://forum.step.esa.int/t/does-anyone-now-the-data-structure-of-sbas-in-stamps/24389

The Configure File for SNAP:

######### CONFIGURATION FILE ######
###################################
# PROJECT DEFINITION
SOURCEFOLDER=/Volumes/DATA/shanxi/org
PROJECTFOLDER=/Volumes/DATA/shanxi/psinsar
GRAPHSFOLDER=/Users/ysdong/Software/my_sbas/graphs
##################################
# PROCESSING PARAMETERS
IW1=IW2
MASTER=S1A_IW_SLC__1SDV_20191220T104456_20191220T104523_030431_037B99_527B.zip
##################################
#SBAS 
temp_baseline=30
##################################
# AOI AREA , only for splitting master and slave
LONMIN=108.6
LATMIN=33.45
LONMAX=108.7
LATMAX=33.60
#AOI clip area， for data clip， the reference image should be deburst and merged, and small than AOI AREA.
CropSx=1000
CropSy=1
CropWx=5000
CropWy=2800
##################################
# Multilook 
RGLOOK=1
AZLOOK=1
SMOOTH=0
##################################
# SNAP GPT 
GPTBIN_PATH=/Applications/snap/bin/gpt
##################################
# COMPUTING RESOURCES TO EMPLOY
CPU=12
CACHE=32G
Multiproc=1
##################################


For STAMPS: 
(1) import with mt_prep_snap;

(2) run sb_parms_initial in matlab; and set the parameters. 

(3) run stamps in matlab

All of scripts are based on the script of Jose Manuel Delgado Blasco and Michael Foumelis, please find detail in: https://github.com/mdelgadoblasco/snap2stamps



