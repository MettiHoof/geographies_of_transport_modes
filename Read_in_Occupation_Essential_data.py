##############################################################################################
# -*- coding: utf-8 -*-
# Script to read in the occupation and essential flow data we are going to use to study Covid with Quant
# Written by Maarten Vanhoof, in April 2020.
# Python 3
#
# Source files were given to me by Roberto Murcio and contain:
#
#Flows between MSOAs per occupation and mode
# occupationBus.csv
# occupationBus.csv
# occupationBus.csv
#
# Structure: origin,destination,ObsAllSixModes,O1,...,O9,ObsRoad,ObsBus,ObsRail,%RoadfromTotal,AdjO1,...AdjO9
# ObsAllSixModes total trips between i and j. 
# O1 to O9 are the observed trips by occupation
# ObsRoad, ObsBus, ObsRail are the observed trips by mode. Note that
# ObsAllSixModes > ObsRoad+ObsBus+ObsRail in general as ObsAllSixModes includes bikes and walking too.
# %RoadfromTotal  = ObsRoad/ObsAllSixModes
# AdjO1 = O1*%RoadfromTotal
# The same for bus and rail.
#
#
#Flows between MSOAs per occupation but with NO modes:
# occupationTripsNOmode.csv
#Structure: MSOA_i, MSOA_j, commuters_by_occupation1, commuters_by_occupation2,...
#
#
#Flows between MSOAs with essential workers per occupation. 
# FlowsEssentialBus.csv
# FlowsEssentialBus.csv
# FlowsEssentialBus.csv
# Structure: MSOA_i, MSOA_j, commuters_by_occupation1(O1), commuters_by_occupation2 (O2),..., 
#	essential_workers_by_occupation1(EO1), essential_workers_by_occ2 (EO2), ...,essential_workers_by_occ9 (EO9)
# Essential flows are calculated on a pro-rata basis. For example EO2 is 0.194 of O2, for all MSOAs. 
#
#
# 
# Major Group 1: MANAGERS, DIRECTORS AND SENIOR OFFICIALS
# Major Group 2: PROFESSIONAL OCCUPATIONS
# Major Group 3: ASSOCIATE PROFESSIONAL AND TECHNICAL OCCUPATIONS
# Major Group 4: ADMINISTRATIVE AND SECRETARIAL OCCUPATIONS
# Major Group 5: SKILLED TRADES OCCUPATIONS
# Major Group 6: CARING, LEISURE AND OTHER SERVICE OCCUPATIONS
# Major Group 7: SALES AND CUSTOMER SERVICE OCCUPATIONS
# Major Group 8: PROCESS, PLANT AND MACHINE OPERATIVES
# Major Group 9: ELEMENTARY OCCUPATIONS
#
##############################################################################################

########################################################
#-1. User Decisions.
########################################################

#Put to True if you want to do the preparation for the different modes. 
car=True
bus=False
rail=False

# #Put to True if you want to do the preparation for the different inputs. 
Occ=True
Ess=True
NoMode=True

########################################################
#0. Setup environment
########################################################

############################
#0.1 Import dependencies
############################
import pandas as pd #For data handling
import numpy as np #For matrix handling
import itertools #For quick iterations
import time #For timing 
import math #For math handling
import geopandas as gpd #For geographic work
import matplotlib #for plotting
#matplotlib.use("TkAgg") #matplotlibs needs to use this backend to not crash on the new mac. 
import matplotlib.pylab as plt #For interactive plotting
#import brewer2mpl #Colors for matplotlib
import pickle #For storing data in pickles 

############################
#0.2 Setup in and output paths and iterators
############################

#Where inputdata lives and output will be put
foldername_input ='/Users/Metti_Hoof/Desktop/Quant_Covid_work/Data/' 
foldername_output ='/Users/Metti_Hoof/Desktop/Test' 
# foldername_output_pickle ='/Users/Metti_Hoof/Desktop/Heavy_data/Pickle_storage_baseline/' 
############################
#0.3 Setup iterators
############################

#make a mode_list storing the active modes.
mode_list=[]
while car:
	mode_list.append('car')
	break
while bus:
	mode_list.append('bus')
	break
while rail:
	mode_list.append('rail')
	break


input_list=[]
while Occ:
	input_list.append('Occ')
	break
while Ess:
	input_list.append('Ess')
	break
while NoMode:
	input_list.append('NoMode')
	break

#Set up a dict containing all the inputfiles
available_inputfiles={}
available_inputfiles['Occ']={}
available_inputfiles['Ess']={}
available_inputfiles['NoMode']={}


########################################################
#1. Read in inputfiles
########################################################

############################
#1.1 Set names of inputfiles
############################

# Flows between MSOA-zones per mode, by occupations
# Structure: MSOA_i, MSOA_j, commuters_by_occupation1, commuters_by_occupation2,...
inputfile_Occ_car= foldername_input + 'occupationRoad.csv' 
inputfile_Occ_bus= foldername_input + 'occupationBus.csv' 
inputfile_Occ_rail= foldername_input + 'occupationRail.csv'

# Flows between MSOA-zones by occupations for all modes, including bike and walking (so these will differ from the quant data)
# Structure: MSOA_i, MSOA_j, commuters_by_occupation1, commuters_by_occupation2,...
inputfile_Occ_NoMode= foldername_input + 'occupationTripsNOmode.csv' 

# Flows between MSOA-zones per mode, by occupations and by essential workers per occupation
#Structure: MSOA_i, MSOA_j, commuters_by_occupation1, commuters_by_occupation2,..., essential_workers_by_occupation1, essential_workers_by_occ2, ...
inputfile_Ess_car= foldername_input + 'FlowsEssentialRoad.csv' 
inputfile_Ess_bus= foldername_input + 'FlowsEssentialBus.csv'
inputfile_Ess_rail= foldername_input + 'FlowsEssentialRail.csv' 


#Shapefile with MSOA locations
inputfile_shapefile_MSOA= '/Users/Metti_Hoof/Desktop/Quant Developing/data/shapefiles/EPSG7405_MSOA_2011/EPSG7405_MSOA_2011.shp'

#Csv file with all unique MSOAs
inputfile_unique_MSOA='/Users/Metti_Hoof/Desktop/Quant Developing/data/Signatures/MSOA11_unique.csv'

########################################################
#2. Read in and pre-process data
########################################################

# Our aim is read in these data and store them in formats that can easily be used in further analysis.

############################
#2.1 Read in data
############################

######################
#2.1.1 Read in the Occ files 
######################

while Occ:
	print("\nWe are treating the flows per occupation")

	while car:
		start_time = time.time()

		print("\nReading in the flows per occupation for car: " + '\n' + str(inputfile_Occ_car))
		
		header_names_car=['Origin', 'Destination', 'ObsAllSixModes','O1','O2','O3','O4','O5','O6','O7','O8','O9',
		'ObsRoad','ObsBus','ObsRail','Share_Car_from_SixModes','Adj_Car_01','Adj_Car_02','Adj_Car_03','Adj_Car_04',
		'Adj_Car_05','Adj_Car_06','Adj_Car_07','Adj_Car_08','Adj_Car_09']
		df_Occ_car=pd.read_csv(inputfile_Occ_car, sep=',', lineterminator='\n',names=header_names_car) 

		print ('\n The number of rows and columns in the Occ_car dataframe are:')
		print(df_Occ_car.shape)

		print ('\n The first five lines of the Occ_car dataframe look like this:')
		print(df_Occ_car.head())

		available_inputfiles['Occ']['car']=df_Occ_car

		print ("\nRead in time for flows per occupation by car:", time.time()-start_time)
		break


	while bus:
		start_time = time.time()

		print("\nReading in the flows per occupation for bus: " + '\n' + str(inputfile_Occ_bus))
		
		header_names_bus=['Origin', 'Destination', 'ObsAllSixModes','O1','O2','O3','O4','O5','O6','O7','O8','O9',
		'ObsRoad','ObsBus','ObsRail','Share_Bus_from_SixModes','Adj_Bus_01','Adj_Bus_02','Adj_Bus_03','Adj_Bus_04',
		'Adj_Bus_05','Adj_Bus_06','Adj_Bus_07','Adj_Bus_08','Adj_Bus_09']
		df_Occ_bus=pd.read_csv(inputfile_Occ_bus, sep=',', lineterminator='\n',names=header_names_bus)
		# df_Occ_bus=df_Occ_bus.rename(columns={'data\r': 'Occ_bus'}) 

		print ('\n The number of rows and columns in the Occ_bus dataframe are:')
		print(df_Occ_bus.shape)

		print ('\n The first five lines of the Occ_bus dataframe look like this:')
		print(df_Occ_bus.head())

		print ("\nRead in time for Occ_bus:", time.time()-start_time)

		available_inputfiles['Occ']['bus']=df_Occ_bus

		break


	while rail:
		start_time = time.time()
		
		print("\nReading in the flows per occupation for rail: " + '\n' + str(inputfile_Occ_rail))
		
		header_names_rail=['Origin', 'Destination', 'ObsAllSixModes','O1','O2','O3','O4','O5','O6','O7','O8','O9',
		'ObsRoad','ObsBus','ObsRail','Share_Rail_from_SixModes','Adj_Rail_01','Adj_Rail_02','Adj_Rail_03','Adj_Rail_04',
		'Adj_Rail_05','Adj_Rail_06','Adj_Rail_07','Adj_Rail_08','Adj_Rail_09']
		df_Occ_rail=df_Occ_rail=pd.read_csv(inputfile_Occ_rail, sep=',', lineterminator='\n',names=header_names_rail) 
		# df_Occ_rail=df_Occ_rail.rename(columns={'data\r': 'Occ_rail'})
		
		print ('\n The number of rows and columns in the Occ_rail dataframe are:')
		print(df_Occ_rail.shape)

		print ('\n The first five lines of the Occ_rail dataframe look like this:')
		print(df_Occ_rail.head())

		print ("\nRead in time for Occ_rail:", time.time()-start_time)

		available_inputfiles['Occ']['rail']=df_Occ_rail

		break

	break


######################
#2.1.2 Read in the Ess files.
######################

while Ess:
	print("\nWe are treating the Ess input")

	while car:
		start_time = time.time()

		print("\nReading in the Ess file for car: " + '\n' + str(inputfile_Ess_car))

		df_Ess_car=pd.read_csv(inputfile_Ess_car, sep=',', lineterminator='\n') 
		df_Ess_car=df_Ess_car.rename(columns={'o': 'Origin','d':'Destination'})
		df_Ess_car=df_Ess_car.drop(columns=['Unnamed: 0'])

		print ('\n The number of rows and columns in the Ess_car dataframe are:')
		print(df_Ess_car.shape)

		print ('\n The first five lines of the Ess_car dataframe look like this:')
		print(df_Ess_car.head())

		print ("\nRead in time for Ess_car:", time.time()-start_time)

		available_inputfiles['Ess']['car']=df_Ess_car

		break

	while bus:
		start_time = time.time()

		print("\nReading in the Ess file for bus: " + '\n' + str(inputfile_Ess_bus))
		
		df_Ess_bus=pd.read_csv(inputfile_Ess_bus, sep=',', lineterminator='\n')
		df_Ess_bus=df_Ess_bus.rename(columns={'o': 'Origin','d':'Destination'})
		df_Ess_bus=df_Ess_bus.drop(columns=['Unnamed: 0'])

		print ('\n The number of rows and columns in the Ess_bus dataframe are:')
		print(df_Ess_bus.shape)

		print ('\n The first five lines of the Ess_bus dataframe look like this:')
		print(df_Ess_bus.head())

		print ("\nRead in time for Ess_bus:", time.time()-start_time)

		available_inputfiles['Ess']['bus']=df_Ess_bus

		break

	while rail:
		start_time = time.time()

		print("\nReading in the Ess file for rail: " + '\n' + str(inputfile_Ess_rail))
		
		df_Ess_rail=df_Ess_rail=pd.read_csv(inputfile_Ess_rail, sep=',', lineterminator='\n') 
		df_Ess_rail=df_Ess_rail.rename(columns={'o': 'Origin','d':'Destination'})
		df_Ess_rail=df_Ess_rail.drop(columns=['Unnamed: 0'])
		
		print ('\n The number of rows and columns in the Ess_rail dataframe are:')
		print(df_Ess_rail.shape)

		print ('\n The first five lines of the Ess_rail dataframe look like this:')
		print(df_Ess_rail.head())

		available_inputfiles['Ess']['rail']=df_Ess_rail

		print ("\nRead in time for Ess_rail:", time.time()-start_time)

		break

	break

######################
#2.1.3 Read in the NoMode files 
######################

while NoMode:
	print("\nWe are treating the NoMode input")

	start_time = time.time()

	print("\nReading in the NoMode file: " + '\n' + str(inputfile_Occ_NoMode))

	df_NoMode=pd.read_csv(inputfile_Occ_NoMode, sep=',', lineterminator='\n')
	df_NoMode=df_NoMode.rename(columns={'NameOrigen': 'NameOrigin','09\r': '09'}) 
	df_NoMode=df_NoMode.drop(columns=['Unnamed: 0'])

	print ('\n The number of rows and columns in the NoMode dataframe are:')
	print(df_NoMode.shape)

	print ('\n The first five lines of the NoMod dataframe look like this:')
	print(df_NoMode.head())

	print ("\nRead in time for NoMode:", time.time()-start_time)

	available_inputfiles['NoMode']=df_NoMode

	break

######################
#1.2.4 MSOA Shapefile
######################

#Read in shapefile in geopandas
gp_MSOA=gpd.read_file(inputfile_shapefile_MSOA)


#Plot map from shapefile
print ('\n We are now plotting the MSOAs of GB')
print(gp_MSOA.plot())
plt.show()
plt.close("all")

#Have a look at the database behind the shapefile
print ('\n The number of rows and columns in the Occ_car dataframe are:')
print(gp_MSOA.shape)

print ('\n The first five lines of the shapefile on MSOA look like this')
print(gp_MSOA.head())#Get first 10 lines to be printed


######################
#1.2.4 MSOA Unique values file
######################

#Read in file.
df_MSOA_unique_values=pd.read_csv(inputfile_unique_MSOA,sep=',', lineterminator='\n') 

#Drop unneccesary line
df_MSOA_unique_values=df_MSOA_unique_values.drop(columns=['Unnamed: 0'])

print ('\n The number of rows and columns in the MSOA unique values dataframe are:')
print(df_MSOA_unique_values.shape)

print ('\n The first five lines of the MSOA unique values dataframe look like this:')
print(df_MSOA_unique_values.head())

MSOA_list=list(df_MSOA_unique_values['MSOA'])


