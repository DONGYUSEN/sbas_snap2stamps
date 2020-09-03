# dongyusen@gmail.com  plot SBAS. 
# it's Working fun.
  

import os
from pathlib import Path
import sys
import glob
import shlex
import time
import shutil
import datetime
import re
import matplotlib.pyplot as plt
import numpy as np


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

print (bar_message)
print ('## TOPSAR SBAS Interferometry Processing @@ ##')
print ('## Plot baseline information @@ ##')
print (bar_message)
#########################################################
#<MDATTR name="Perp Baseline" type="float64" mode="rw">74.98091888427734</MDATTR>
#<MDATTR name="Temp Baseline" type="float64" mode="rw">-1325.999755859375</MDATTR>

x_tbaseline = []
y_pbaseline = []

m_x = []
m_y = []


masterdate = MASTER[0]
supermaster = masterdate[17:25]
# print(supermaster)

m_x.append(datetime.datetime(int(supermaster[0:4]),int(supermaster[4:6]),int(supermaster[6:8])))
# m_x.append(np.datetime64(supermaster))
m_y.append(0.0)
i = 0


with open(finishedcoregfile, 'r') as file :
	for files in file.readlines():
		if files[0:8].strip() ==  supermaster :
			slave_date= files[9:17].strip()
			m_x.append(datetime.datetime(int(slave_date[0:4]),int(slave_date[4:6]),int(slave_date[6:8])))
			# m_x.append(np.datetime64(slave_date))
			files2 = files[0:21]
			fullfilename = tempcoreg + '/' + files2.strip() + '_coreg.dim'
			with open(fullfilename, 'r') as infile :
				k = 0
				for line in infile.readlines():
					if "Perp Baseline" in line:
						temp_pbaseline = re.split('[><]', line)
						k = k + 1
						if k == 2:
							m_y.append(float(temp_pbaseline[2].strip()))
							i=i+1
							break	
			plt.plot([m_x[0],m_x[i]],[m_y[0],m_y[i]],color='r',linewidth=1,linestyle=':')
			plt.text(m_x[i],m_y[i],slave_date[4:8])

with open(finishedcoregfile, 'r') as file :
	for files in file.readlines():
		if files[0:8].strip() !=  supermaster :
			master_date = files[0:8].strip()
			master_date = datetime.datetime(int(master_date[0:4]),int(master_date[4:6]),int(master_date[6:8]))
			pm = m_x.index(master_date)

			slave_date  = files[9:17].strip()
			slave_date  = datetime.datetime(int(slave_date[0:4]),int(slave_date[4:6]),int(slave_date[6:8]))
			ps = m_x.index(slave_date)

			plt.plot([m_x[pm], m_x[ps]], [m_y[pm], m_y[ps]],color='skyblue')




#print(m_x, m_y)
plt.plot(m_x, m_y,'.',color='b')
plt.xlabel("Acquire Times of Sentinel-1 dataset (year)")
plt.ylabel("Perp Baseline to the Supermaster (meter)")
plt.title("Baseline and Interferomtric Pairs Information")
plt.grid(True, which='major') #x坐标轴的网格使用主刻度
plt.plot(m_x[0], m_y[0],'*',color='r',markersize=12.)
plt.show()


