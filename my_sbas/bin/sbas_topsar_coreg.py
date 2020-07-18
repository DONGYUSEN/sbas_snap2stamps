# dongyusen@gmail.com  for coregistration data. 
# it's Working fun.
  

import os
from pathlib import Path
import sys
import glob
import subprocess
import shlex
import time
import shutil
import multiprocessing
from multiprocessing import Pool
import datetime


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
coregfolder=[]
ifgfolder=[]
tempfolder=[]
SOURCEFOLDER=[]
polygon=''
slavelist = [[] for i in range(500)]
total_slave=0
finishedfile=''
finishedlist=[]
error_flag = 0
coreglist = [[] for i in range(2)] 
temp_baseline = 45
suppermasterdate = []


def test(inlist):
	
	masterdate = coreglist[0][inlist]
	slavedate = coreglist[1][inlist]
	print (inlist, masterdate, slavedate)


# data process part: 
def interferometry(inlist):
	masterdate = coreglist[0][inlist]
	slavedate = coreglist[1][inlist]
# 	print (inlist, masterdate, slavedate)

	timeStarted_func = time.time()
	error_flag = 0
	print ('\n')
	print ('\033[1;35m Processing ... \033[0m' + str(inlist+1) + ' of ' + str(total_slave) + ' dataset..............')
	print (' Processing ...' + masterdate + '_' + slavedate + '.....................')

	## start processing:

	for IW in IWlist:

		## checking dataset in processed list:
		with open(finishedfile, 'r') as file :
			filedata = file.read()
		tempfilename = masterdate + '_' + slavedate  + '_' + IW + '.dim'
		# print tempfilename 
		if tempfilename in filedata:
			print (' Alreay processed, Skip it, or Delete the file in ifg/finished.txt to Reprocess it? ..............')
			return

		graphxml=GRAPH+'/sbas_topsar_coreg.xml' #will be changed in mergering !
		graph2run=PROJECT+'/graphs/sbas_topsar_coreg2run'  + '_' + masterdate + '_' + slavedate + '_' + IW + '.xml' #will be changed in mergering !
		print ('\n*****' + IW + ' of ' + str(len(IWlist)) +'IWs :'+ masterdate + '_' + slavedate + ' coregistration\n')
		with open(graphxml, 'r') as file :
			filedata = file.read()
			if os.path.isfile(splitmasterfolder+'/'+masterdate +'_'+ IW +'.dim'):
				filedata = filedata.replace('iMASTER',	splitmasterfolder + '/' + masterdate + '_' + IW 		+ '.dim')
			else:
				filedata = filedata.replace('iMASTER',	splitslavefolder + '/' + masterdate + '_' + IW 		+ '.dim')
			filedata = filedata.replace('iSLAVE', 	splitslavefolder  + '/' + slavedate  + '_' + IW 		+ '.dim')
			filedata = filedata.replace('iOUTPUT',	tempcoreg   	  + '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.dim')
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print (line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print ('033[1;35m Error in processing ... \033[0m  coreg_ifg2run\n')
			return
		
		if suppermasterdate.strip() != masterdate.strip():
			print('\n----Sub-master pairs:--------------\n')
			master_source = tempcoreg+ '/' + suppermasterdate + '_' + masterdate + '_' + IW  + '_' + 'coreg.data/'
			slave_source = tempcoreg+ '/' + suppermasterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.data/'
			result_source = tempcoreg+ '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.data/'
			shutil.rmtree(tempcoreg+ '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.data')
			os.mkdir(tempcoreg+ '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.data')
			# print(master_source, slave_source, result_source)
			for source_file in glob.iglob(master_source + '*slv1*'):
				(source_path, source_filename) = os.path.split(source_file)
				purpse_file = result_source + source_filename.replace('slv1', 'mst')
				my_command = ['cp', '-f', source_file, purpse_file]
				#print (my_command)
				process = subprocess.Popen(my_command, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				for line in iter(process.stdout.readline, b''):
					print (line.rstrip())
				process.stdout.close()
				process.wait()
			for source_file in glob.iglob(slave_source + '*slv1*'):
				(source_path, source_filename) = os.path.split(source_file)
				purpse_file = result_source + source_filename
				my_command = ['cp', '-f', source_file,  purpse_file] 
				#print(my_command)
				process = subprocess.Popen(my_command, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
				for line in iter(process.stdout.readline, b''):
					print (line.rstrip())
				process.stdout.close()
				process.wait()

			my_command = ['cp', '-R', slave_source+'tie_point_grids', result_source]
			#print(my_command)
			process = subprocess.Popen(my_command, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			for line in iter(process.stdout.readline, b''):
				print (line.rstrip())
			process.stdout.close()
			process.wait()
			my_command = ['cp', '-R', slave_source+'vector_data', result_source]
			#print(my_command)
			process = subprocess.Popen(my_command, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
			for line in iter(process.stdout.readline, b''):
				print (line.rstrip())
			process.stdout.close()
			process.wait()
			# modify the .dim file:
			dimfile = tempcoreg+ '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.dim'
			# print(dimfile)
			with open(dimfile, 'r') as file :
				filedata = file.read()
			filedata = filedata.replace('<DATA_TYPE>int16</DATA_TYPE>',	'<DATA_TYPE>float32</DATA_TYPE>', 2)
			with open(dimfile, 'w') as file:
				file.write(filedata)
			print ('Finish linking data....\n')	

			if process.returncode != 0 :
				error_flag = 1
				print ('033[1;35m Error in processing ... \033[0m  coreg2run\n')
				return		


	if error_flag == 0:
		with open(finishedfile, 'a') as file :
			file.write(masterdate + '_' + slavedate + '_' + IW + '.dim\n')
			
	print (time.asctime( time.localtime(time.time())))
	timeDelta = time.time() - timeStarted_func
	print ('\n\033[1;35m Finished coregistration processing of \033[0m'+ masterdate + '_' + slavedate +' in ' +  str(timeDelta/60.0) + ' mins.\n')
	print (bar_message)
	print ('\n')

## main part:
if __name__ == "__main__":

	# Getting configuration variables from inputfile
	inputfile = sys.argv[1]
	print ('\n\033[1;35m Some necessary information of this work:\033[0m \n')
	try:
		in_file = open(inputfile, 'r')
		for line in in_file.readlines():
			if "SOURCEFOLDER" in line:
				SOURCEFOLDER = line.split('=')[1].strip()
				print ('Source Path:   ', SOURCEFOLDER )
			if "MASTER" in line:
				MASTER = line.split('=')[1].strip()
				MASTER = MASTER.replace(' ','')
				MASTER = MASTER.split(',')
				print ('Master data: ', MASTER )
			if "PROJECTFOLDER" in line:
				PROJECT = line.split('=')[1].strip()
				print ('Project path:  ', PROJECT)
			if "IW1" in line:
				IWlist = line.split('=')[1].strip()
				IWlist = IWlist.replace(' ','')
				IWlist = IWlist.split(',')
				print ('Used IW:  ', IWlist)
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
			if "RGLOOK" in line:
				RGLOOK = line.split('=')[1].strip()
			if "AZLOOK" in line:
				AZLOOK = line.split('=')[1].strip()
			if "SMOOTH" in line:
				SMOOTH = line.split('=')[1].strip()
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
print ('AOI: ', polygon)
print ('Mulitlook, Ra:Az = ', RGLOOK + ':' + AZLOOK)
	#############################################################################
	### TOPSAR Splitting (Assembling) and Apply Orbit section ####
	############################################################################
splitmasterfolder=PROJECT+'/MasterSplit'
splitslavefolder=PROJECT+'/SlaveSplit'
graphfolder=PROJECT+'/graphs'
coregfolder=PROJECT+'/coreg'
ifgfolder=PROJECT+'/ifg'
tempfolder=PROJECT+'/temp'
tempcoreg=PROJECT+'/tempcoreg'
finishedfile=tempcoreg+'/finished.txt'

if not os.path.exists(splitslavefolder):
	os.makedirs(splitslavefolder)
if not os.path.exists(graphfolder):
	os.makedirs(graphfolder)
if not os.path.exists(coregfolder):
	os.makedirs(coregfolder)
if not os.path.exists(ifgfolder):
	os.makedirs(ifgfolder)
if not os.path.exists(tempfolder):
	os.makedirs(tempfolder)	
if not os.path.exists(tempcoreg):
	os.makedirs(tempcoreg)	
if not os.path.exists(finishedfile):
	Path(finishedfile).touch()

print (bar_message)
print ('## TOPSAR SBAS coregistration @@ ##')
print (bar_message)

## get the coreglist
slavedatelist = []

for filename in sorted(os.listdir(splitslavefolder)):
	if filename.endswith(".dim") : 
		slavedatelist.append(filename)
k=0
for datelist in slavedatelist:
	if  k == 0 :
		slavelist[k].append(datelist[0:8])
		slavelist[k].append(datelist)
		k = k + 1
	else :
		mflag = 0
		for i in range(k):
			if (datelist[0:8] in slavelist[i]):
				slavelist[i].append(datelist)
				mflag = 1
		if mflag == 0 :
			slavelist[k].append(datelist[0:8])
			slavelist[k].append(datelist)
			k = k + 1

newlist = [x for x in slavelist if x] 
slavelist = newlist
del newlist

total_slave = len(slavelist[:])

masterdate = MASTER[0]
masterdate = masterdate[17:25]
suppermasterdate = masterdate

for i in range(total_slave-1):
	coreglist[0].append(masterdate)
	coreglist[1].append(slavelist[i][0])

for i in range(total_slave-1):
	for j in range(i+1,total_slave-1):
		#check temp_baseline
		temp_date1 = str(slavelist[i][0])
		temp_date2 = str(slavelist[j][0])
		# print temp_date1, temp_date1[4:6] 
		temp_date10 = datetime.datetime(int(temp_date1[0:4]),int(temp_date1[4:6]),int(temp_date1[6:8]))
		temp_date20 = datetime.datetime(int(temp_date2[0:4]),int(temp_date2[4:6]),int(temp_date2[6:8]))
		temp_date_delta = temp_date20 - temp_date10
		if abs(temp_date_delta.days) < temp_baseline:
			coreglist[0].append(slavelist[i][0])
			coreglist[1].append(slavelist[j][0])

inputlist = list(range(len(coreglist[0])))
total_slave = len(coreglist[0])
print ('\n*****  Totally ' + str(len(coreglist[0])) + ' pairs !!!  ****\n')


# multiprocessing:
pool = Pool(processes = Multiproc)

# result = pool.map(test, inputlist0)
result = pool.map(interferometry, inputlist)
print (result)









