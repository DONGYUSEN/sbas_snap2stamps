
# dongyusen@gmail.com  for slave data preparing.
# it's Working fun.
  

import os
from pathlib import Path
import sys
import glob
import subprocess
import shlex
import time
import multiprocessing
from multiprocessing import Pool

bar_message='#####################################################################'
PROJECT = []
MASTER = []
GRAPH = []
GPT = []
CACHE = []
CPU = []
IWlist = []
slavefolder = []
splitfolder = []
graphfolder = []
splitmasterfolder=[]
splitslavefolder=[]
SOURCEFOLDER=[]
polygon=''
slavelist = [[] for i in range(500)]
totalslave=0

finishedfile=''
finishedlist=[]


def slave_split(inlist):
	files = slavelist[inlist]
	timeStarted = time.time()
	temp_name  = files[1]
	slavedate = temp_name[17:25]
	error_flag = 0
	with open(finishedfile, 'r') as file :
		filedata = file.read()
	tempfilename = slavedate  + '.dim'
	print('**************\033[1;35m Processing ... \033[0m  ' +  str(inlist+1) + '/' + str(totalslave) + ' ' + temp_name[17:25]) 
	# print tempfilename 
	if tempfilename in filedata:
		print(' Alreay processed, Skip it, or Delete the file in MasterSplit/finished.txt to Reprocess it? ..............')
		return


	for IW in IWlist:
		temp_name  = files[1]
		outputname=temp_name[17:25]+'_'+IW+'.dim'
		print('**************\033[1;35m Processing ... \033[0m  ' + IW+ ' of ' + str(inlist+1) + '/' + str(totalslave) + ' ' + temp_name[17:25])
		graph2run=graphfolder+'/Ssplitgraph2run_'+temp_name[17:25]+'_'+IW+'.xml'
		if len(files) == 2 :
				graphxml=GRAPH+'/split_applyorbit.xml'
				with open(graphxml, 'r') as file :
					filedata = file.read()
				filedata = filedata.replace('INPUTFILE', SOURCEFOLDER+'/'+files[1])
				filedata = filedata.replace('IWs',IW)
				filedata = filedata.replace('POLARISATION','VV')
				filedata = filedata.replace('OUTPUTFILE',splitslavefolder+'/'+outputname)
				filedata = filedata.replace('POLYGON',polygon)
				with open(graph2run, 'w') as file:
					file.write(filedata)
		if len(files) == 3 :
				graphxml=GRAPH+'/assemble_split_applyorbit.xml'
				with open(graphxml, 'r') as file :
					filedata = file.read()
				# Replace the target string
				filedata = filedata.replace('INPUTFILE1', SOURCEFOLDER+'/'+files[1])
				filedata = filedata.replace('INPUTFILE2', SOURCEFOLDER+'/'+files[2])
				filedata = filedata.replace('IWs',IW)
				filedata = filedata.replace('POLARISATION','VV')
				filedata = filedata.replace('OUTPUTFILE',splitslavefolder+'/'+outputname)
				filedata = filedata.replace('POLYGON',polygon)
				# Write the file out again
				with open(graph2run, 'w') as file:
					file.write(filedata)
		args = [ GPT, '-x', graph2run, '-c', CACHE, '-q', CPU]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print(line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			message='\033[1;35m Error in splitting \033[0m slave '+str(temp_name[17:25])
			error_flag = 1
		else :
			message='\033[1;35m Successfully in splitting \033[0m slave '+str(temp_name[17:25])
		print(message)

	if error_flag == 0 :
		with open(finishedfile, 'a') as file :
			file.write(slavedate +'.dim\n')

	timeDelta = time.time() - timeStarted 
	print(('Splitting  of '+ str(temp_name[17:25])+ ' in '+str(timeDelta/60.0)+' mins.'))
	print(time.asctime( time.localtime(time.time())))
	print(bar_message)

## main part:
if __name__ == "__main__":

	# Getting configuration variables from inputfile
	inputfile = sys.argv[1]
	try:
		in_file = open(inputfile, 'r')
		for line in in_file.readlines():
			if "SOURCEFOLDER" in line:
				SOURCEFOLDER = line.split('=')[1].strip()
				print('Source Path:   ', SOURCEFOLDER) 
			if "MASTER" in line:
				MASTER = line.split('=')[1].strip()
				MASTER = MASTER.replace(' ','')
				MASTER = MASTER.split(',')
				print('Master data: ', MASTER) 
			if "PROJECTFOLDER" in line:
				PROJECT = line.split('=')[1].strip()
				print('Project path:  ', PROJECT)
			if "IW1" in line:
				IWlist = line.split('=')[1].strip()
				IWlist = IWlist.replace(' ','')
				IWlist = IWlist.split(',')
				print('Used IW:  ', IWlist)
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
				# print GRAPH
			if "GPTBIN_PATH" in line:
				GPT = line.split('=')[1].strip()
				# print GPT			
			if "CACHE" in line:
				CACHE = line.split('=')[1].strip()
				# print CACHE
			if "CPU" in line:
				CPU = line.split('=')[1].strip()
				# print CPU
			if "Multiproc" in line:
				Multiproc = int(line.split('=')[1].strip())
				# print Multiproc				
	finally:
		in_file.close()
polygon='POLYGON (('+LONMIN+' '+LATMIN+','+LONMAX+' '+LATMIN+','+LONMAX+' '+LATMAX+','+LONMIN+' '+LATMAX+','+LONMIN+' '+LATMIN+'))'
print('AOI: ', polygon)
	#############################################################################
	### TOPSAR Splitting (Assembling) and Apply Orbit section ####
	############################################################################
splitmasterfolder=PROJECT+'/MasterSplit'
splitslavefolder=PROJECT+'/SlaveSplit'
graphfolder=PROJECT+'/graphs'
tempfolder=PROJECT+'/temp'
finishedfile=splitslavefolder+'/finished.txt'

if not os.path.exists(splitslavefolder):
	os.makedirs(splitslavefolder)
if not os.path.exists(graphfolder):
	os.makedirs(graphfolder)
if not os.path.exists(tempfolder):
    os.makedirs(tempfolder) 
if not os.path.exists(finishedfile):
	Path(finishedfile).touch()

print(bar_message)
print('## TOPSAR Splitting and Apply Orbit ##')
print(bar_message)

## get the slavelist

slavedatelist = []
for filename in sorted(os.listdir(SOURCEFOLDER)):
	if filename.endswith(".zip") : 
		if ((filename in MASTER)!= True):
			slavedatelist.append(filename)
k=0
for datelist in slavedatelist:
	if  k == 0 :
		slavelist[k].append(datelist[17:25])
		slavelist[k].append(datelist)
		k = k + 1
	else :
		mflag = 0
		for i in range(k):
			if (datelist[17:25] in slavelist[i]):
				#slavelist[i].append(datelist[17:25])
				slavelist[i].append(datelist)
				mflag = 1
		if mflag == 0 :
			slavelist[k].append(datelist[17:25])
			slavelist[k].append(datelist)
			k = k + 1
totalslave = k
print('Totally ' + str(k) + ' slaves!!!')
newlist = [x for x in slavelist if x] 
slavelist = newlist
del newlist
# print slavelist

# multiprocessing:
inputlist  = list(range(k))

pool = Pool(processes = Multiproc)
result = pool.map(slave_split, inputlist)
#print result







