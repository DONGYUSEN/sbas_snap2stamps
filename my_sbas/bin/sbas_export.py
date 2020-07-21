### Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
# Author Jose Manuel Delgado Blasco
# Date: 21/06/2018
# Version: 1.0

# modify by dongyusen@gmail.com 2020.07.21



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
import shutil  
inputfile = sys.argv[1]
bar_message='\n#####################################################################\n'

# Getting configuration variables from inputfile
try:
    in_file = open(inputfile, 'r')
    for line in in_file.readlines():
        if "PROJECTFOLDER" in line:
            PROJECT = line.split('=')[1].strip()
            print(PROJECT)
        if "IW1" in line:
            IW = line.split('=')[1].strip()
            print(IW)
        if "MASTER" in line:
            MASTER = line.split('=')[1].strip()
            print(MASTER)
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
finally:
        in_file.close()


finishedfile=''
finishedlist=[]
file1=[]
file2=[]



###################################################################################
##### StaMPS PSI export ##################
###################################################################################
coregfolder=PROJECT+'/coreg'
ifgfolder=PROJECT+'/ifg'
head, tail = os.path.split(MASTER)
print(tail)
logfolder=PROJECT+'/logs'


masterdate = tail[17:25]
# print('masterdate: ', masterdate)

outputexportfolder = PROJECT+'/INSAR_'+tail[17:25]
outputexportfolder1 = outputexportfolder + '/SMALL_BASELINES'
finishedfile=outputexportfolder+'/finished.txt'
finished_insar=PROJECT+'/ifg/finished.txt'

# print(finished_insar)

print('Checking finished files in /ifg')
with open(finished_insar, 'r') as f :
    for line in f.readlines():
        file1.append(line[0:8].strip())
        file2.append(line[9:17].strip())
maxfile_date = max(max(file1), max(file2))
minfile_date = min(min(file1), min(file2))

outputexportfolder2 = outputexportfolder1 + '/' + minfile_date + '_' + maxfile_date
outgeo = outputexportfolder + '/geo'



if not os.path.exists(outputexportfolder):
    os.makedirs(outputexportfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
if not os.path.exists(finishedfile):
    Path(finishedfile).touch()


if not os.path.exists(outputexportfolder1):
    os.makedirs(outputexportfolder1)
if not os.path.exists(outputexportfolder2):
    os.makedirs(outputexportfolder2)
if not os.path.exists(outgeo):
    os.makedirs(outgeo)


outlog=logfolder+'/export_proc_stdout.log'
out_file = open(outlog, 'a')
err_file=out_file
graphxml=GRAPH+'/sbas_export.xml'
graph2run=PROJECT+'/graphs/export2run.xml'
print(bar_message)
out_file.write(bar_message)
message='## StaMPS PSI export started:\n'
print(message)
out_file.write(message)
print(bar_message)
out_file.write(bar_message)


k=0
for dimfile in glob.iglob(coregfolder + '/*.dim'):
    head, tail = os.path.split(os.path.join(coregfolder, dimfile))
    k=k+1
    message='['+str(k)+'] Exporting pair: master-slave pair '+tail+'\n'
    ifgdim = Path(ifgfolder+'/'+tail)
    # print(ifgdim)
    if ifgdim.is_file():
        print(message)
        out_file.write(message)

    with open(finishedfile, 'r') as file :
        filedata = file.read()
    if dimfile in filedata:
        print(' Alreay processed, Check InSAR_XXXX/finished.txt ..............')
        continue


    with open(graphxml, 'r') as file :
        filedata = file.read()

        # Replace the target string
    filedata = filedata.replace('COREGFILE',dimfile)
    filedata = filedata.replace('IFGFILE', str(ifgdim))
    filedata = filedata.replace('OUTPUTFOLDER',outputexportfolder2)
    # Write the file out again
    with open(graph2run, 'w') as file:
        file.write(filedata)
    # args = [ GPT, graph2run, '-c', CACHE, '-q', CPU]
    args = [ GPT, graph2run, '-q', CPU]
    # print(args)

    # Launching process
    process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    timeStarted = time.time()
    stdout = process.communicate()[0]
    print('SNAP STDOUT:{}'.format(stdout))
    timeDelta = time.time() - timeStarted     # Get execution time.
    print(('['+str(k)+'] Finished process in '+str(timeDelta/60.0)+' mins.'))
    out_file.write('['+str(k)+'] Finished process in '+str(timeDelta)+' seconds.\n')
    if process.returncode != 0 :
        message='Error exporting '+str(tail)+'\n' 
        err_file.write(message)
    else:
        message='Stamps export of '+str(tail)+' successfully completed.\n'
        print(message)
        out_file.write(message)
        with open(finishedfile, 'a') as file :
            file.write(dimfile+'\n')
    if os.path.isfile('target.dim'):
        shutil.rmtree('target.data') 
        os.remove('target.dim')
    print(bar_message)
    out_file.write(bar_message)
out_file.close()
err_file.close()

args = [ 'cp', outputexportfolder2 + '/dem/projected_dem.par', outputexportfolder +'/geo/' + masterdate +'_dem.par']
process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
for line in iter(process.stdout.readline, b''):
    print(line.rstrip())
process.stdout.close()
process.wait()
args = [ 'cp', outputexportfolder2 + '/dem/projected_dem.rslc', outputexportfolder +'/geo/' + masterdate +'_dem.rslc']
process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
for line in iter(process.stdout.readline, b''):
    print(line.rstrip())
process.stdout.close()
process.wait()
args = [ 'cp', outputexportfolder2 + '/geo/'+ masterdate + '.lat', outputexportfolder +'/geo/']
process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
for line in iter(process.stdout.readline, b''):
    print(line.rstrip())
process.stdout.close()
process.wait()
args = [ 'cp', outputexportfolder2 + '/geo/'+ masterdate + '.lat.par', outputexportfolder +'/geo/']
process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
for line in iter(process.stdout.readline, b''):
    print(line.rstrip())
process.stdout.close()
process.wait()
args = [ 'cp', outputexportfolder2 + '/geo/'+ masterdate + '.lon', outputexportfolder +'/geo/']
process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
for line in iter(process.stdout.readline, b''):
    print(line.rstrip())
process.stdout.close()
process.wait()
args = [ 'cp', outputexportfolder2 + '/geo/'+ masterdate + '.lon.par', outputexportfolder +'/geo/']
process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
for line in iter(process.stdout.readline, b''):
    print(line.rstrip())
process.stdout.close()
process.wait()
print('-------------Finish exporting')
print('-------------First, run mt_prep_snap ' + masterdate +  ' ' + outputexportfolder2  + ' 0.6 .......' + ' in ' + outputexportfolder)
print('-------------Then run sb_parms_initial in matlab')
print('               Good luck  :)                    ')
