### Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
# Author Jose Manuel Delgado Blasco
# Date: 21/06/2018
# Version: 1.0

# Step 1 : preparing slaves in folder structure
# Step 2 : TOPSAR Splitting (Assembling) and Apply Orbit
# Step 3 : Coregistration and Interferogram generation
# Step 4 : StaMPS export

# Added option for CACHE and CPU specification by user
# Planned support for DEM selection and ORBIT type selection 


import os
from pathlib import Path
import sys
import glob
import subprocess
import shlex
import time
inputfile = sys.argv[1]

bar_message='#####################################################################'

# Getting configuration variables from inputfile

in_file = open(inputfile, 'r')

try:
    for line in in_file.readlines():
        if "SOURCEFOLDER" in line:
            SOURCEFOLDER = line.split('=')[1].strip()
            print(SOURCEFOLDER) 
        if "MASTER" in line:
            MASTER = line.split('=')[1].strip()
            MASTER = MASTER.replace(' ','')
            MASTER = MASTER.split(',')
            print(MASTER)    
        if "PROJECTFOLDER" in line:
            PROJECT = line.split('=')[1].strip()
            print(PROJECT)
        if "IW1" in line:
            IW = line.split('=')[1].strip()
            IW = IW.replace(' ','')
            IW = IW.split(',')
            print(IW)
        if "LONMIN" in line:
            LONMIN = line.split('=')[1].strip()
        if "LATMIN" in line:
            LATMIN = line.split('=')[1].strip()
        if "LONMAX" in line:
            LONMAX = line.split('=')[1].strip()
        if "LATMAX" in line:
            LATMAX = line.split('=')[1].strip()
        if "GRAPHSFOLDER" in line:
            GRAPH = line.split('=')[1].strip()
            print(GRAPH)
        if "GPTBIN_PATH" in line:
            GPT = line.split('=')[1].strip()
            print(GPT)
        if "CACHE" in line:
            CACHE = line.split('=')[1].strip()
        if "CPU" in line:
            CPU = line.split('=')[1].strip()
        if "Multiproc" in line:
            Multiproc = line.split('=')[1].strip()
            print(Multiproc)             
finally:
    in_file.close()

polygon='POLYGON (('+LONMIN+' '+LATMIN+','+LONMAX+' '+LATMIN+','+LONMAX+' '+LATMAX+','+LONMIN+' '+LATMAX+','+LONMIN+' '+LATMIN+'))'
print(polygon)

#############################################################################
### TOPSAR Splitting (Assembling) and Apply Orbit section ####
############################################################################
splitmasterfolder=PROJECT+'/MasterSplit'
logfolder=PROJECT+'/logs'
graphfolder=PROJECT+'/graphs'
tempfolder=PROJECT+'/temp'
if not os.path.exists(splitmasterfolder):
    os.makedirs(splitmasterfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
if not os.path.exists(graphfolder):
    os.makedirs(graphfolder)
if not os.path.exists(tempfolder):
    os.makedirs(tempfolder) 

graph2run=graphfolder+'/splitgraph2run.xml'
outlog=logfolder+'/split_proc_stdout.log'
out_file = open(outlog, 'a')
err_file=out_file

print(bar_message)
out_file.write(bar_message)
message='## TOPSAR Splitting and Apply Orbit\n'
print(message)
out_file.write(message)
print(bar_message)
out_file.write(bar_message)
k=1
# IWlist=[ 'IW1','IW2','IW3']
IWlist = IW
files = MASTER
for IW in IWlist:
    print(IW)
    head , tailm = os.path.split(files[0])
    outputname=tailm[17:25] +'_'+IW+'.dim'
    graph2run=graphfolder+'/Msplitgraph2run_'+tailm[17:25]+'_'+IW+'.xml'
    timeStarted  =time.time()
    if len(files) == 1:
        graphxml=GRAPH+'/split_applyorbit.xml'
        with open(graphxml, 'r') as file :
            filedata = file.read()
        # Replace the target string
        filedata = filedata.replace('INPUTFILE', SOURCEFOLDER+'/'+files[0])
        filedata = filedata.replace('IWs',IW)
        filedata = filedata.replace('POLARISATION','VV')
        filedata = filedata.replace('OUTPUTFILE',splitmasterfolder+'/'+outputname)
        filedata = filedata.replace('POLYGON',polygon)
       		# # Write the file out again
        with open(graph2run, 'w') as file :
           	file.write(filedata)
    if len(files) == 2 :
        graphxml=GRAPH+'/assemble_split_applyorbit.xml'
        with open(graphxml, 'r') as file :
            filedata = file.read()
        filedata = filedata.replace('INPUTFILE1', SOURCEFOLDER+'/'+files[0])
        filedata = filedata.replace('INPUTFILE2', SOURCEFOLDER+'/'+files[1])
        filedata = filedata.replace('IWs',IW)
        filedata = filedata.replace('POLARISATION','VV')
        filedata = filedata.replace('OUTPUTFILE',splitmasterfolder+'/'+outputname)
        filedata = filedata.replace('POLYGON',polygon)
        	# Write the file out again
    with open(graph2run, 'w') as file:
        file.write(filedata)

    # args = [GPT, graph2run, '-q', CPU, '-c', CACHE]
    args = [GPT, graph2run, '-q', CPU]
    print(args)
    out_file.write(str(args)+'\n')
    # launching the process
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        print(line.rstrip())
    process.stdout.close()
    process.wait()

    timeDelta = time.time() - timeStarted                     # Get execution time.
    if process.returncode != 0 :
        message='Error splitting master, please try again ......................'
        print(message) 
    else: 
        message='Splitting master successfully completed........................'
        print(message)
        out_file.write(message)
        print(bar_message)
    print(('['+str(k)+'] Finished process in '+str(timeDelta/60.0)+' mins.'))
    out_file.write('['+str(k)+'] Finished process in '+str(timeDelta)+' seconds.\n')
    out_file.write(bar_message)
    k = k + 1
out_file.close()
