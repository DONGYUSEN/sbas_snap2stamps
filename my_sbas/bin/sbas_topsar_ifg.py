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
import numpy as np
import gdal 
from gdal import ogr
from gdal import osr
import matplotlib.pyplot as plt

temp_baseline = 45
error_flag = 0

bar_message='#####################################################################'

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
				print ('Supper Master data: ', MASTER )
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
			if "temp_baseline"	in line:
				temp_baseline = int(line.split('=')[1].strip())
			if "CropSx"	in line:
				CropSx = line.split('=')[1].strip()
			if "CropSy"	in line:
				CropSy = line.split('=')[1].strip()
			if "CropWx"	in line:
				CropWx = line.split('=')[1].strip()
			if "CropWy"	in line:
				CropWy = line.split('=')[1].strip()
	finally:
		in_file.close()
polygon='POLYGON (('+LONMIN+' '+LATMIN+','+LONMAX+' '+LATMIN+','+LONMAX+' '+LATMAX+','+LONMIN+' '+LATMAX+','+LONMIN+' '+LATMIN+'))'
print ('AOI: ', polygon)
print ('Mulitlook, Ra:Az = ', RGLOOK + ':' + AZLOOK)
print ('Small baseline time: ',  temp_baseline)

############################################
splitmasterfolder=PROJECT+'/MasterSplit'
splitslavefolder=PROJECT+'/SlaveSplit'
graphfolder=PROJECT+'/graphs'
coregfolder=PROJECT+'/coreg'
ifgfolder=PROJECT+'/ifg'
tempfolder=PROJECT+'/temp'
tempcoreg=PROJECT+'/tempcoreg'
finishedcoregfile=tempcoreg+'/finished.txt'
finishedifgfile=ifgfolder+'/finished.txt'
sbas_addfile = PROJECT + '/sbas_add.txt'

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
if not os.path.exists(finishedifgfile):
	Path(finishedifgfile).touch()
if not os.path.exists(sbas_addfile):
	Path(sbas_addfile).touch()	

print (bar_message)
print ('## TOPSAR SBAS Interferometry Processing @@ ##')
print (bar_message)
#########################################################

masterdate = MASTER[0]
suppermasterdate = masterdate[17:25]

temp_list = []
sbas_list = []

with open(finishedcoregfile, "r") as f:
	for line in f.readlines():
		temp_list.append(line.strip('\n'))
with open(sbas_addfile, 'r') as infile :
	addfiledata = infile.read()

temp_date1 = '00000000'
temp_date2 = '00000000'
for files in temp_list:
	files_date1 = files[0:8].strip()
	files_date2 = files[9:17].strip()
	temp_date10 = datetime.datetime(int(files_date1[0:4]),int(files_date1[4:6]),int(files_date1[6:8]))
	temp_date20 = datetime.datetime(int(files_date2[0:4]),int(files_date2[4:6]),int(files_date2[6:8]))
	temp_date_delta = temp_date20 - temp_date10
	if (abs(temp_date_delta.days) < temp_baseline) and (abs(temp_date_delta.days) > 0):
		if  (temp_date1 != files_date1) or (temp_date2 != files_date2) or (files in addfiledata) :
				sbas_list.append(files[0:17])
	temp_date1 = files_date1
	temp_date2 = files_date2

print('-------------Total ' + str(len(sbas_list)) + ' Will be processing now ----------------') 
# show the sbas_list, without IWs.

temp_ifg_file = tempfolder + '/' + 'step1_finished.txt'
if not os.path.exists(temp_ifg_file):
	Path(temp_ifg_file).touch()

num_ifg = len(sbas_list)
num_now = 1
for files in sbas_list:  # starting processing 
	## checking dataset in processed list:
	#print(files + '\n')	
	print('\n')
	print('\n')
	print('......[No. ' + str(num_now) +' of total ' + str(num_ifg) + ',    ' + files + ' will be processing ...........\n')

	with open(finishedifgfile, 'r') as file :
		filedata = file.read()
	tempfilename = files +'.dim'
	if tempfilename in filedata:
		print (' Alreay processed, Skip it, or Delete the file in ifgfolder/step1_finished.txt to Reprocess it? ..............')
		num_now = num_now + 1
		continue

	timeStarted_func = time.time() # check time.


	for IW in IWlist:
	####
		graphxml=GRAPH+'/sbas_topsar_1iw-seamask.xml' #will be changed in mergering !
		graph2run=PROJECT+'/graphs/sbas_ifg2run.xml' #will be changed in mergering !
		print ('\n*****' + IW + ' of ' + str(len(IWlist)) +'IWs :'+ files + ' interferometry\n')
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT',	tempcoreg  + '/' + files + '_' + IW  + '_' + 'coreg.dim')
			# filedata = filedata.replace('OUTCOREG',	tempfolder + '/' + files + '_' + IW  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTIFG', 	tempfolder + '/' + files + '_' + IW  + '_' + 'ifg.dim')
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
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
			print ('033[1;35m Error in processing ... \033[0m  sbas_ifg2run\n')
			continue


	print('\n*****' + files + ' will be mosaicing and subsetting  ........')

	if len(IWlist) == 1: 
		IW=IWlist[0]
		print('***** One Swath Used ***** \n')
		if SMOOTH=='1':
			graphxml=GRAPH+'/topsar_1iw-f1sm.xml' #will be changed in mergering !
		else:
			graphxml=GRAPH+'/topsar_1iw-f1.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run_exportifg.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + files + '_' + IW  + '_' + 'ifg.dim')
			filedata = filedata.replace('OUTPUT0', 	ifgfolder  + '/' + files  + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
			filedata = filedata.replace('CropSx', 	CropSx)
			filedata = filedata.replace('CropSy', 	CropSy)
			filedata = filedata.replace('CropWx', 	CropWx)
			filedata = filedata.replace('CropWy', 	CropWy)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print(line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print('033[1;35m Error in processing ... \033[0m  topsar_1iw-f1\n')
			continue

		graphxml=GRAPH+'/topsar_1iw-f1c.xml' #will be changed in mergering !
		graph2run=PROJECT+'/graphs/coreg_ifg2run_exportcoreg.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempcoreg  + '/' + files + '_' + IW  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTPUT0', 	coregfolder+ '/' + files + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
			filedata = filedata.replace('CropSx', 	CropSx)
			filedata = filedata.replace('CropSy', 	CropSy)
			filedata = filedata.replace('CropWx', 	CropWx)
			filedata = filedata.replace('CropWy', 	CropWy)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print(line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print('033[1;35m Error in processing ... \033[0m  topsar_1iw-f1c\n')
			continue


	if len(IWlist) == 2:
		print('***** Two Swathes Used ***** \n')
		if SMOOTH=='1':
			graphxml=GRAPH+'/topsar_1iw-f2sm.xml' #will be changed in mergering !
		else:
			graphxml=GRAPH+'/topsar_1iw-f2.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run_exportifg.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + files + '_' + IWlist[0]  + '_' + 'ifg.dim')
			filedata = filedata.replace('INPUT1',	tempfolder + '/' + files + '_' + IWlist[1]  + '_' + 'ifg.dim')
			filedata = filedata.replace('OUTPUT0', 	ifgfolder  + '/' + files + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
			filedata = filedata.replace('CropSx', 	CropSx)
			filedata = filedata.replace('CropSy', 	CropSy)
			filedata = filedata.replace('CropWx', 	CropWx)
			filedata = filedata.replace('CropWy', 	CropWy)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print(line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print('033[1;35m Error in processing ... \033[0m  topsar_1iw-f2\n')
			continue


		graphxml=GRAPH+'/topsar_1iw-f2c.xml' #will be changed in mergering !
		graph2run=PROJECT+'/graphs/coreg_ifg2run_exportcoreg.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempcoreg + '/' + files + '_' + IWlist[0]  + '_' + 'coreg.dim')
			filedata = filedata.replace('INPUT1',	tempcoreg + '/' + files + '_' + IWlist[1]  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTPUT0', 	coregfolder+ '/' + files + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
			filedata = filedata.replace('CropSx', 	CropSx)
			filedata = filedata.replace('CropSy', 	CropSy)
			filedata = filedata.replace('CropWx', 	CropWx)
			filedata = filedata.replace('CropWy', 	CropWy)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print(line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print('033[1;35m Error in processing ... \033[0m  topsar_1iw-f2c\n')
			continue

	if len(IWlist) == 3:
		print('***** Three Swathes Used ***** \n')
		if SMOOTH=='1':
			graphxml=GRAPH+'/topsar_1iw-f3sm.xml' #will be changed in mergering !
		else:
			graphxml=GRAPH+'/topsar_1iw-f3.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run_exportifg.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + files + '_' + IWlist[0]  + '_' + 'ifg.dim')
			filedata = filedata.replace('INPUT1',	tempfolder + '/' + files + '_' + IWlist[1]  + '_' + 'ifg.dim')
			filedata = filedata.replace('INPUT2',	tempfolder + '/' + files + '_' + IWlist[2]  + '_' + 'ifg.dim')
			filedata = filedata.replace('OUTPUT0', 	ifgfolder  + '/' + files + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
			filedata = filedata.replace('CropSx', 	CropSx)
			filedata = filedata.replace('CropSy', 	CropSy)
			filedata = filedata.replace('CropWx', 	CropWx)
			filedata = filedata.replace('CropWy', 	CropWy)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print(line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print('033[1;35m Error in processing ... \033[0m  topsar_1iw-f3\n')
			continue

		graphxml=GRAPH+'/topsar_1iw-f3c.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run_exportcoreg.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempcoreg + '/' + files + '_' + IWlist[0]  + '_' + 'coreg.dim')
			filedata = filedata.replace('INPUT1',	tempcoreg + '/' + files + '_' + IWlist[1]  + '_' + 'coreg.dim')
			filedata = filedata.replace('INPUT2',	tempcoreg + '/' + files + '_' + IWlist[2]  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTPUT0', 	coregfolder+ '/' + files + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
			filedata = filedata.replace('CropSx', 	CropSx)
			filedata = filedata.replace('CropSy', 	CropSy)
			filedata = filedata.replace('CropWx', 	CropWx)
			filedata = filedata.replace('CropWy', 	CropWy)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print(line.rstrip())
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print('033[1;35m Error in processing ... \033[0m  topsar_1iw-f3c\n')
			continue

	##########################
	shutil.rmtree(tempfolder)
	os.mkdir(tempfolder) 
	
	if error_flag == 0:
		with open(finishedifgfile, 'a') as file :
			file.write(files +'.dim\n')
		# write file to png
		pngpath = ifgfolder  + '/' + files + '.data'
		for filename in sorted(os.listdir(pngpath)):
			if filename.endswith(".img") : 
				if filename.startswith("i_"):
					i_file = pngpath + '/' + filename
				if filename.startswith("q_"):
					q_file = pngpath + '/' + filename
		ds = gdal.Open(i_file, gdal.GA_ReadOnly)
		i_ifg = ds.GetRasterBand(1).ReadAsArray()
		ds = None
		ds = gdal.Open(q_file, gdal.GA_ReadOnly)
		q_ifg = ds.GetRasterBand(1).ReadAsArray()
		transform = ds.GetGeoTransform()
		ds = None
		i_ifg[i_ifg == 0 ] = np.nan
		fig = plt.figure(figsize=(24,24))
		ax = fig.add_subplot(111)
		ax.imshow(np.arctan(q_ifg/i_ifg), cmap='jet')
		ax.set_aspect('auto')    
		plt.axis('off')
		plt.savefig(ifgfolder+ '/' + files + '.png')
		plt.close(fig)


			
	print(time.asctime( time.localtime(time.time())))
	timeDelta = time.time() - timeStarted_func
	print('\n\033[1;35m Finished interferometry, mosaic and subset processing of \033[0m'+ files +' in ' +  str(timeDelta/60.0) + ' mins.\n')
	num_now = num_now + 1
	print(bar_message)
	print('\n')



	




