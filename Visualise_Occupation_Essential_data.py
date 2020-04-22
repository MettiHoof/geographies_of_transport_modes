##############################################################################################
# -*- coding: utf-8 -*-
# Script to read in the occupation and essential flow data we are going to use to study Covid with Quant
# Written by Maarten Vanhoof, in April 2020.
# Python 3
#
# Source files were given to me by Roberto Murcio and contain:
#
#Flows between MSOAs per occupation and mode
# occupationRoad.csv
# occupationBus.csv
# occupationRail.csv
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
#  ##### BE CAREFUL, MAARTEN BELIEVES THATE FOR NOMODES: ORIGIN=HOME, DESTINATION=WORK, this was confirmed by Roberto ######
#
#
#
#Flows between MSOAs with essential workers per occupation. 
#
# Structure: MSOA_i, MSOA_j, commuters_by_occupation1(O1), commuters_by_occupation2 (O2),..., 
#	essential_workers_by_occupation1(EO1), essential_workers_by_occ2 (EO2), ...,essential_workers_by_occ9 (EO9)
# Essential flows are calculated on a pro-rata basis. For example EO2 is 0.194 of O2, for all MSOAs. 
#
# ##### BE CAREFUL, MAARTEN BELIEVES THATE FOR ESSENTIAL: ORIGIN=WORK, DESTINATION=HOME, this was confirmed by Roberto ######
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
#
#
#
#Csv file with average trip length by MSOAs per occupation
#
#avg_trip_length_by_occ_by_region.csv was prepared by Iacopo and gives the mean trip length per msoa, occupation, and mode.
#

##############################################################################################

########################################################
#-1. User Decisions.
########################################################

#Put to True if you want to do the preparation for the different modes. 
car=True
bus=True
rail=True

# #Put to True if you want to do the preparation for the different inputs. 
Occ=False
Ess=True
NoMode=False

########################################################
#0. Setup environment
########################################################

############################
#0.1 Import dependencies
############################
import pandas as pd #For data handling
import numpy as np #For matrix handling
#§import itertools #For quick iterations
import time #For timing 
#import math #For math handling
import geopandas as gpd #For geographic work
import matplotlib #for plotting
#matplotlib.use("TkAgg") #matplotlibs needs to use this backend to not crash on the new mac. 
import matplotlib.pylab as plt #For interactive plotting
import matplotlib.colors as clr #For colors
from mpl_toolkits.axes_grid1 import make_axes_locatable #For help with the legend locations
import mapclassify #To make chloropleth maps.
#import brewer2mpl #Colors for matplotlib
#import pickle #For storing data in pickles 

############################
#0.2 Setup in and output paths and iterators
############################

#Where inputdata lives and output will be put
foldername_input ='/Users/Metti_Hoof/Desktop/Quant_Covid_work/Data/' 
foldername_output ='/Users/Metti_Hoof/Desktop/Test/' 
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


############################
#0.4 Setup figure specifications
############################
plot_titles={	'O1': 'Managers, directors and senior officials (O1)',
				'O2': 'Professional occupations (O2)',
				'O3': 'Associate professional and technical occupations (O3)',
				'O4': 'Administrative and secretarial occupations (O4)',
				'O5': 'Skilled trades occupations (O5)',
				'O6': 'Caring, leisure and other service occupations (O6)',
				'O7': 'Sales and customer service occupations (O7)',
				'O8': 'Process, plant, and machine operatives (O8)',
				'O9': 'Elementary occupations (O9)'}



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

#Csv file with MSOAs in London
inputfile_MSOA_london='/Users/Metti_Hoof/Desktop/Quant_Covid_work/Data/MSOA_London.csv'

#Csv file with average trip length by MSOAs per occupation
inputfile_trip_length='/Users/Metti_Hoof/Desktop/Quant_Covid_work/Data/avg_trip_length_by_occ_by_region.csv'

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
	df_NoMode=df_NoMode.rename(columns={'NameOrigen': 'NameOrigin',
										'05':'O5',
										'06':'O6',
										'07':'O7',
										'08':'O8',
										'09\r': 'O9'}) 
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

"""
#Plot map from shapefile
print ('\n We are now plotting the MSOAs of GB')
print(gp_MSOA.plot())
plt.show()
plt.close("all")
"""

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



######################
#1.2.4 MSOA in london file
######################

#Read in file.
df_MSOA_london=pd.read_csv(inputfile_MSOA_london,sep=',', lineterminator='\n') 


print ('\n The number of rows and columns in the MSOA london dataframe are:')
print(df_MSOA_london.shape)

print ('\n The first five lines of the MSOA london dataframe look like this:')
print(df_MSOA_london.head())

MSOA_list_london=list(df_MSOA_london['MSOA'])



######################
#1.2.4 Average trip lengths by occupation
######################

#Read in file.
df_MSOA_trip_length=pd.read_csv(inputfile_trip_length,sep=',', lineterminator='\n') 

print ('\n The number of rows and columns in the MSOA unique values dataframe are:')
print(df_MSOA_trip_length.shape)

print ('\n The first five lines of the MSOA unique values dataframe look like this:')
print(df_MSOA_trip_length.head())



########################################################
#3. Visualise the different occupation categories at home and work.
########################################################
'''
# We use the NoMode dataset to do so. 
##### BE CAREFUL, MAARTEN BELIEVES THATE FOR NOMODES: ORIGIN=HOME, DESTINATION=WORK ######

############################
#3.1 Aggregate the occupation numbers per MSOA. 
############################

# For the origin, which in our data is the location of the workplace
df_to_aggregate_origin=df_NoMode[['Origin','OccupationAll','O1','O2','O3','O4','O5','O6','O7','O8','O9']]
df_aggregated_origin=df_to_aggregate_origin.groupby(['Origin'])[['OccupationAll','O1','O2','O3','O4','O5','O6','O7','O8','O9']].agg('sum')


# For the destination, which in our data is the loication of the home
df_to_aggregate_destination=df_NoMode[['Destination','OccupationAll','O1','O2','O3','O4','O5','O6','O7','O8','O9']]
df_aggregated_destination=df_to_aggregate_destination.groupby(['Destination'])[['OccupationAll','O1','O2','O3','O4','O5','O6','O7','O8','O9']].agg('sum')

# Get relative values for aggregated numbers. 
df_aggregated_origin['relO1']=df_aggregated_origin.O1/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO2']=df_aggregated_origin.O2/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO3']=df_aggregated_origin.O3/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO4']=df_aggregated_origin.O4/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO5']=df_aggregated_origin.O5/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO6']=df_aggregated_origin.O6/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO7']=df_aggregated_origin.O7/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO8']=df_aggregated_origin.O8/df_aggregated_origin.OccupationAll
df_aggregated_origin['relO9']=df_aggregated_origin.O9/df_aggregated_origin.OccupationAll

df_aggregated_destination['relO1']=df_aggregated_destination.O1/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO2']=df_aggregated_destination.O2/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO3']=df_aggregated_destination.O3/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO4']=df_aggregated_destination.O4/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO5']=df_aggregated_destination.O5/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO6']=df_aggregated_destination.O6/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO7']=df_aggregated_destination.O7/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO8']=df_aggregated_destination.O8/df_aggregated_destination.OccupationAll
df_aggregated_destination['relO9']=df_aggregated_destination.O9/df_aggregated_destination.OccupationAll


############################
#3.2 Enrich the geopandas shapefile of GM with data on occupation numbers
############################

#For origin
gp_MSOA_Occ_NoMode_aggregated_origin = gp_MSOA.merge(df_aggregated_origin, left_on='MSOA11CD', right_on='Origin')

#Check whether dimensions are still the same after the merge. 
if gp_MSOA_Occ_NoMode_aggregated_origin.shape[0] != df_aggregated_origin.shape[0]:
	print ('\n The merge we just performed has reduced the dimensions of your inputdata that was aggregated on origin. The shapes of both datasets are:')
	print (gp_MSOA_Occ_NoMode_aggregated_origin.shape)
	print (df_aggregated_origin.shape)
else:
	print ('\nThis merge has not reduced the dimensions of your inputdata inputdata that was aggregated on origin.')
 

#For destination
gp_MSOA_Occ_NoMode_aggregated_destination = gp_MSOA.merge(df_aggregated_destination, left_on='MSOA11CD', right_on='Destination')    

#Check whether dimensions are still the same after the merge. 
if gp_MSOA_Occ_NoMode_aggregated_destination.shape[0] != df_aggregated_destination.shape[0]:
	print ('\n The merge we just performed has reduced the dimensions of your inputdata that was aggregated on destinations. The shapes of both datasets are:')
	print (gp_MSOA_Occ_NoMode_aggregated_destination.shape)
	print (df_aggregated_destination.shape)
else:
	print ('\nThis merge has not reduced the dimensions of your inputdata inputdata that was aggregated on destinations.')


############################
#3.3 Visualise the information per occupation
############################


####################
#3.3.1  Individual maps of absolute and relative worker counts in home and work locations
####################


print ('\n We are now plotting the individual maps of different occupations')


#Set up iteration lists
occupation_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9']
direction_list=['work'] #'work' and or 'home'
values_list=['absolute'] #'relative' and or 'absolute'


for direction in direction_list:
	for value in values_list:
		for occ in occupation_list:
			print(direction,value,occ)


			#Setup figure
			figsize_x_cm=14 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
			figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
			figsize_y_cm=22
			figsize_y_inches=figsize_y_cm/2.54

			fig, ax = plt.subplots(1,figsize=(figsize_x_inches,figsize_y_inches))

			left   =  0.00  # the left side of the subplots of the figure
			right  =  1  # the right side of the subplots of the figure
			bottom =  0.07  # the bottom of the subplots of the figure
			top    =  0.93  # the top of the subplots of the figure
			wspace =  .00   # the amount of width reserved for blank space between subplots
			hspace =  .00   # the amount of height reserved for white space between subplots

			# This function actually adjusts the sub plots using the above paramters
			plt.subplots_adjust(
			left    =  left, 
			bottom  =  bottom, 
			right   =  right, 
			top     =  top, 
			wspace  =  wspace, 
			hspace  =  hspace
				)

			#Make a position for the legend ax (cax)
			divider = make_axes_locatable(ax)
			cax_by_us= divider.append_axes("bottom", size="2%", pad=0)

			#Create position for historgram
			axin = ax.inset_axes([0.0, 0.00, 1, 0.04])
			axin_london=ax.inset_axes([0.62, 0.52, 0.38, 0.14])

			if direction=='home':
				if value=='absolute':
					# Plot absolute values 
					gp_MSOA_Occ_NoMode_aggregated_origin.plot(ax=ax,column=occ,legend=True,cax=cax_by_us,
					legend_kwds={'label': "Residents in this occupation",'orientation': "horizontal"},cmap='YlOrBr')

					# Create london inset
					gp_MSOA_Occ_NoMode_aggregated_origin.loc[gp_MSOA_Occ_NoMode_aggregated_origin['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=occ,cmap='YlOrBr')
					
					#Set figure title 
					title= 'Residents in \n "{0}"'.format(plot_titles[occ])
					title=str(title)
					plt.suptitle(title, fontsize=15)

					#Create histogram, draw within inset.
					a=np.array(gp_MSOA_Occ_NoMode_aggregated_origin[occ])
					#Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					#Set x limits
					max_x=max(a)
					axin.set_xlim(0,max_x)
					axin.set_axis_off()


				elif value=='relative':
					# Plot relative values
					to_plot='rel'+occ
					gp_MSOA_Occ_NoMode_aggregated_origin.plot(ax=ax,column=to_plot,legend=True,cax=cax_by_us,
						legend_kwds={'label': "Percentage of residents in this occupation",'orientation': "horizontal"},cmap='GnBu')

					# Create london inset
					gp_MSOA_Occ_NoMode_aggregated_origin.loc[gp_MSOA_Occ_NoMode_aggregated_origin['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=to_plot,cmap='GnBu')
					

					#Set figure title 
					title= 'Share of residents in \n "{0}"'.format(plot_titles[occ])
					title=str(title)
					plt.suptitle(title, fontsize=15)

					#Create histogram, draw within inset.
					a=np.array(gp_MSOA_Occ_NoMode_aggregated_origin[to_plot])
					#Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					#Set x limits
					max_x=max(a)
					axin.set_xlim(0,max_x)
					axin.set_axis_off()


			elif direction=='work':
				if value=='absolute':
					# Plot absolute values
					gp_MSOA_Occ_NoMode_aggregated_destination.plot(ax=ax,column=occ,legend=True,cax=cax_by_us,
						legend_kwds={'label': "Workers in this occupation",'orientation': "horizontal"},cmap='YlOrBr')

					# Create london inset
					gp_MSOA_Occ_NoMode_aggregated_destination.loc[gp_MSOA_Occ_NoMode_aggregated_destination['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=occ,cmap='YlOrBr')
					
					#Set figure title 
					title= 'Workers in \n "{0}"'.format(plot_titles[occ])
					title=str(title)
					plt.suptitle(title, fontsize=15)


					#Create histogram, draw within inset.
					a=np.array(gp_MSOA_Occ_NoMode_aggregated_destination[occ])
					#Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					#Set x limits
					max_x=max(a)
					axin.set_xlim(0,max_x)
					axin.set_axis_off()

				elif value=='relative':
					# Plot relative values
					to_plot='rel'+occ
					gp_MSOA_Occ_NoMode_aggregated_destination.plot(ax=ax,column=to_plot,legend=True,cax=cax_by_us,
						legend_kwds={'label': "Percentage of workers in this occupation",'orientation': "horizontal"},cmap='GnBu')

					# Create london inset
					gp_MSOA_Occ_NoMode_aggregated_destination.loc[gp_MSOA_Occ_NoMode_aggregated_destination['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=to_plot,cmap='GnBu')
					
					#Set figure title 
					title= 'Share of workers in \n "{0}"'.format(plot_titles[occ])
					title=str(title)
					plt.suptitle(title, fontsize=15)


					#Create histogram, draw within inset.
					a=np.array(gp_MSOA_Occ_NoMode_aggregated_destination[to_plot])
					#Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					#Set x limits
					max_x=max(a)
					axin.set_xlim(0,max_x)
					axin.set_axis_off()


			# set aspect to equal. This is done automatically when using *geopandas* plot on it's own, but not when working with pyplot directly. 
			ax.set_aspect('equal')

			#Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
			ax.set_axis_off()
			
			#Set axin_london up
			axin_london.set_aspect('equal')
			axin_london.set_title('Greater London Area', fontsize=6,color='0.3')

			for pos in ['top','bottom','left','right']:
				axin_london.spines[pos].set_linewidth(0.1)
				axin_london.spines[pos].set_color('0.2')

			# Set ticks parameters so they do not show
			axin_london.tick_params(
    			axis='x',          # changes apply to the x-axis
    			which='both',      # both major and minor ticks are affected
    			bottom=False,      # ticks along the bottom edge are off
    			top=False,         # ticks along the top edge are off
    			labelbottom=False) # labels along the bottom edge are officials
			axin_london.tick_params(axis='y',which='both',left=False,right=False, labelleft=False) 

			#Set up north arrow
			x, y, arrow_length = 0.95, 0.1, 0.03
			ax.annotate('N', color='0.8',xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='0.6',edgecolor='0.6', width=1, headwidth=3,headlength=5),
            ha='center', va='center', fontsize=8,
            xycoords=ax.transAxes)


			#save or show
			#plt.show()

			#save or show
			outputname='Occ_{0}_by_{1}_location_{2}_values.png'.format(occ,direction,value)
			output=foldername_output+outputname
			plt.savefig(output)
			axin.clear()
			axin_london.clear()
			plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
			plt.clf() #clear the entire figure. Since we define the figure inside the loop, this is ok. We do this because otherwise there is some overlap of colors in themain figure..
			print ('Figure saved')

'''



########################################################
#4. Visualise the use of different transport modes for different occupation categories and related essential workers at home and work.
########################################################

# We use the Ess dataset to do so. 
##### BE CAREFUL, MAARTEN BELIEVES THATE FOR ESSENTIAL: ORIGIN=WORK, DESTINATION=HOME, this was confirmed by Roberto. ######

############################
#4.1 Aggregate the occupation numbers per MSOA. 
############################

#For car
if car:
	# For the origin, which in our data is the location of the workplace
	df_aggregated_Ess_car_origin=df_Ess_car.groupby(['Origin'])[['O1','O2','O3','O4','O5','O6','O7','O8','O9','EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].agg('sum').copy()
	df_aggregated_Ess_car_origin['sum_occ']=df_aggregated_Ess_car_origin[['O1','O2','O3','O4','O5','O6','O7','O8','O9']].sum(axis=1)
	df_aggregated_Ess_car_origin['sum_occ_ess']=df_aggregated_Ess_car_origin[['EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].sum(axis=1)
	
	# For the destination, which in our data is the loication of the home
	df_aggregated_Ess_car_destination=df_Ess_car.groupby(['Destination'])[['O1','O2','O3','O4','O5','O6','O7','O8','O9','EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].agg('sum').copy()
	df_aggregated_Ess_car_destination['sum_occ']=df_aggregated_Ess_car_destination[['O1','O2','O3','O4','O5','O6','O7','O8','O9']].sum(axis=1)
	df_aggregated_Ess_car_destination['sum_occ_ess']=df_aggregated_Ess_car_destination[['EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].sum(axis=1)
	


if bus:
	# For the origin, which in our data is the location of the workplace
	df_aggregated_Ess_bus_origin=df_Ess_bus.groupby(['Origin'])[['O1','O2','O3','O4','O5','O6','O7','O8','O9','EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].agg('sum').copy()
	df_aggregated_Ess_bus_origin['sum_occ']=df_aggregated_Ess_bus_origin[['O1','O2','O3','O4','O5','O6','O7','O8','O9']].sum(axis=1)
	df_aggregated_Ess_bus_origin['sum_occ_ess']=df_aggregated_Ess_bus_origin[['EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].sum(axis=1)	
	
	# For the destination, which in our data is the loication of the home
	df_aggregated_Ess_bus_destination=df_Ess_bus.groupby(['Destination'])[['O1','O2','O3','O4','O5','O6','O7','O8','O9','EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].agg('sum').copy()
	df_aggregated_Ess_bus_destination['sum_occ']=df_aggregated_Ess_bus_destination[['O1','O2','O3','O4','O5','O6','O7','O8','O9']].sum(axis=1)
	df_aggregated_Ess_bus_destination['sum_occ_ess']=df_aggregated_Ess_bus_destination[['EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].sum(axis=1)
	

if rail:
	# For the origin, which in our data is the location of the workplace
	df_aggregated_Ess_rail_origin=df_Ess_rail.groupby(['Origin'])[['O1','O2','O3','O4','O5','O6','O7','O8','O9','EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].agg('sum').copy()
	df_aggregated_Ess_rail_origin['sum_occ']=df_aggregated_Ess_rail_origin[['O1','O2','O3','O4','O5','O6','O7','O8','O9']].sum(axis=1)
	df_aggregated_Ess_rail_origin['sum_occ_ess']=df_aggregated_Ess_rail_origin[['EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].sum(axis=1)	

	# For the destination, which in our data is the loication of the home
	df_aggregated_Ess_rail_destination=df_Ess_rail.groupby(['Destination'])[['O1','O2','O3','O4','O5','O6','O7','O8','O9','EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].agg('sum').copy()
	df_aggregated_Ess_rail_destination['sum_occ']=df_aggregated_Ess_rail_destination[['O1','O2','O3','O4','O5','O6','O7','O8','O9']].sum(axis=1)
	df_aggregated_Ess_rail_destination['sum_occ_ess']=df_aggregated_Ess_rail_destination[['EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']].sum(axis=1)
	


############################
#4.2 Create a masterdf combining information from all three modes. 
############################

###### NOTE : to have this section working you need to put all three modes to true in the beginning of the script. #######

#I do not think we need this security check since we do an outer join in the merge. 
#if (df_aggregated_Ess_car_origin.shape[0] < df_aggregated_Ess_bus_origin.shape[0]) or (df_aggregated_Ess_car_origin.shape[0] < df_aggregated_Ess_rail_origin.shape[0]):
#	print ('We have a problem for the Origins, the join will exclude some MSOAs')

#if (df_aggregated_Ess_car_destination.shape[0] < df_aggregated_Ess_bus_destination.shape[0]) or (df_aggregated_Ess_car_destination.shape[0] < df_aggregated_Ess_rail_destination.shape[0]):
#	print ('We have a problem for the Origins, the join will exclude some MSOAs')

df_aggregated_Ess_origin_tussen=pd.merge(df_aggregated_Ess_car_origin, df_aggregated_Ess_bus_origin, how='outer', on='Origin',suffixes=('','_bus'))
df_aggregated_Ess_origin=pd.merge(df_aggregated_Ess_origin_tussen, df_aggregated_Ess_rail_origin, how='outer', on='Origin',suffixes=('_car','_rail'))

df_aggregated_Ess_destination_tussen=pd.merge(df_aggregated_Ess_car_destination, df_aggregated_Ess_bus_destination, how='outer', on='Destination',suffixes=('','_bus'))
df_aggregated_Ess_destination=pd.merge(df_aggregated_Ess_destination_tussen, df_aggregated_Ess_rail_destination, how='outer', on='Destination',suffixes=('_car','_rail'))


###############
#4.2.1 Join the masterdf's with the geopandas.
###############

#For origin
gp_MSOA_Ess_aggregated_origin = gp_MSOA.merge(df_aggregated_Ess_origin, left_on='MSOA11CD', right_on='Origin')

#Check whether dimensions are still the same after the merge. 
if gp_MSOA_Ess_aggregated_origin.shape[0] != df_aggregated_Ess_origin.shape[0]:
	print ('\n The merge we just performed has reduced the dimensions of your inputdata that was aggregated on origin. The shapes of both datasets are:')
	print (gp_MSOA_Ess_aggregated_origin.shape)
	print (df_aggregated_Ess_origin.shape)
else:
	print ('\nThis merge has not reduced the dimensions of your inputdata inputdata that was aggregated on origin.')
 

#For destination
gp_MSOA_Ess_aggregated_destination = gp_MSOA.merge(df_aggregated_Ess_destination, left_on='MSOA11CD', right_on='Destination')

#Check whether dimensions are still the same after the merge. 
if gp_MSOA_Ess_aggregated_destination.shape[0] != df_aggregated_Ess_destination.shape[0]:
	print ('\n The merge we just performed has reduced the dimensions of your inputdata that was aggregated on destination. The shapes of both datasets are:')
	print (gp_MSOA_Ess_aggregated_destination.shape)
	print (df_aggregated_Ess_destination.shape)
else:
	print ('\nThis merge has not reduced the dimensions of your inputdata inputdata that was aggregated on destinations.')



############################
#4.3 Visualise the information of amount of workers or residents per occupation that use a certain transport mode
############################

# We will thus have three maps (three modes, next to eachother)


####################
##4.3.1  Individual maps of absolute commuter counts by mode in home and work locations
####################
'''

print ('\n We are now plotting the maps of different occupations and essential workers per mode.')


#Set up iteration lists
occupation_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9']
direction_list=['home','work'] #'work' and or 'home'
ess_list=['essential_workers'] #'essential_workers' and or'all_workers' 


for direction in direction_list:
	for ess in ess_list:
		for occ in occupation_list:
			print(direction,ess,occ)


			#Setup figure
			figsize_x_cm=42 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
			figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
			figsize_y_cm=22
			figsize_y_inches=figsize_y_cm/2.54

			#define number of subplots.
			ncols=3
			nrows=1

			#Set up fig and ax
			fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
			#axarr[row][col] if row>1
			#axarr[col] if row=1

			left   =  0.00  # the left side of the subplots of the figure
			right  =  1 	# the right side of the subplots of the figure
			bottom =  0.07  # the bottom of the subplots of the figure
			top    =  0.93  # the top of the subplots of the figure
			wspace =  .02   # the amount of width reserved for blank space between subplots
			hspace =  .00   # the amount of height reserved for white space between subplots

			# This function actually adjusts the sub plots using the above paramters
			plt.subplots_adjust(
			left    =  left, 
			bottom  =  bottom, 
			right   =  right, 
			top     =  top, 
			wspace  =  wspace, 
			hspace  =  hspace
				)

			#We will be making a figure with mutliple columns. 
			col_counter=0
			col_suffix=['_car','_bus','_rail']
			col_name=['car','bus','rail']
			
			for col in range(ncols):

				#Setup the col name you want to plot
				if ess=='all_workers':
					col_to_plot=occ+col_suffix[col]
				elif ess=='essential_workers':
					col_to_plot='E'+occ+col_suffix[col]

				print(col_to_plot)

				#Setup insets
				#Make a position for the legend ax (cax)
				divider = make_axes_locatable(axarr[col])
				cax_by_us = divider.append_axes("bottom", size="2%", pad=0)

				#Create position for histogram
				axin = axarr[col].inset_axes([0.0, 0.00, 1, 0.04])
				axin_london = axarr[col].inset_axes([0.62, 0.52, 0.38, 0.14])

				if direction=='home':
					# Label for legend
					label='Residents that commute by {0}'.format(col_name[col]) 
					
					# Plot main figure
					gp_MSOA_Ess_aggregated_destination.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')
					
					# Plot London inset
					gp_MSOA_Ess_aggregated_destination.loc[gp_MSOA_Ess_aggregated_destination['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					a=np.array(gp_MSOA_Ess_aggregated_destination[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)

				elif direction=='work':
					# Label for legend
					label='Workers that commute by {0}'.format(col_name[col]) 

					# Plot main figure
					gp_MSOA_Ess_aggregated_origin.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')

					# Plot London inset
					gp_MSOA_Ess_aggregated_origin.loc[gp_MSOA_Ess_aggregated_origin['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					a=np.array(gp_MSOA_Ess_aggregated_origin[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)

				# Titelke dabei
				extra_title='Commuting by {0}'.format(col_name[col]) 
				axarr[col].text(.03, .97, extra_title, ha='left', va='top', rotation=0, fontsize=11, color='black',
					transform=axarr[col].transAxes,bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':'black'})

				#Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
				axarr[col].set_axis_off()

				#Set axin_london up
				axin_london.set_aspect('equal')
				axin_london.set_title('Greater London Area', fontsize=6,color='0.3')

				for pos in ['top','bottom','left','right']:
					axin_london.spines[pos].set_linewidth(0.1)
					axin_london.spines[pos].set_color('0.2')

				# Set ticks parameters so they do not show
				axin_london.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
				axin_london.tick_params(axis='y',which='both',left=False,right=False, labelleft=False) 
				
				#Set x limits for histogram
				max_x=max(a)
				axin.set_xlim(0,max_x)
				axin.set_axis_off()

				#Set up north arrow
				x, y, arrow_length = 0.95, 0.1, 0.03
				axarr[col].annotate('N', color='0.8',xy=(x, y), xytext=(x, y-arrow_length),
					arrowprops=dict(facecolor='0.6',edgecolor='0.6', width=1, headwidth=3,headlength=5),
					ha='center', va='center', fontsize=8,xycoords=axarr[col].transAxes)

				col_counter=col_counter+1				

			#Set figure title 
			if direction=='home':
				title= 'Residents in "{0}" commuting by different modes'.format(plot_titles[occ])
			elif direction=='work':
				title= 'Workers in "{0}" commuting by different modes'.format(plot_titles[occ])			 
			plt.suptitle(title, fontsize=15)

			#save or show
			# plt.show()

			#Set figure names
			if direction=='home':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_absolute_values.png'.format(occ,direction,ess)
			elif direction=='work':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_absolute_values.png'.format(occ,direction,ess)
			output=foldername_output+outputname
			plt.savefig(output)
			axin.clear()
			axin_london.clear()
			plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
			plt.clf() #clear the entire figure. Since we define the figure inside the loop, this is ok. We do this because otherwise there is some overlap of colors in themain figure..
			print ('Figure saved')

'''
####################
#4.3.2  Individual maps of absolute commuter counts by mode in home and work locations but with maximum for residents and workers
####################
'''

#We do exactly the same as before but limit workers and resident numbers so the maps reveal more information
#Limits were chosen upon visual inspection and will be the same for all occupations

#Hard-coded limit.
residents_limit={}
workers_limit={}
residents_limit['all_workers']={'car':500,'bus':100,'rail':100}
workers_limit['all_workers']={'car':500,'bus':100,'rail':100}
residents_limit['essential_workers']={'car':100,'bus':50,'rail':50}
workers_limit['essential_workers']={'car':100,'bus':50,'rail':50}

print ('\n We are now plotting the maps of different occupations and essential workers per mode but with limits..')


#Set up iteration lists
occupation_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9']
direction_list=['work'] #'work' and or 'home'
ess_list=['essential_workers'] #'essential_workers' and or 'all_workers'


for direction in direction_list:
	for ess in ess_list:
		for occ in occupation_list:
			print(direction,ess,occ)


			#Setup figure
			figsize_x_cm=42 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
			figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
			figsize_y_cm=22
			figsize_y_inches=figsize_y_cm/2.54

			#define number of subplots.
			ncols=3
			nrows=1

			#Set up fig and ax
			fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
			#axarr[row][col] if row>1
			#axarr[col] if row=1

			left   =  0.00  # the left side of the subplots of the figure
			right  =  1 	# the right side of the subplots of the figure
			bottom =  0.07  # the bottom of the subplots of the figure
			top    =  0.93  # the top of the subplots of the figure
			wspace =  .02   # the amount of width reserved for blank space between subplots
			hspace =  .00   # the amount of height reserved for white space between subplots

			# This function actually adjusts the sub plots using the above paramters
			plt.subplots_adjust(
			left    =  left, 
			bottom  =  bottom, 
			right   =  right, 
			top     =  top, 
			wspace  =  wspace, 
			hspace  =  hspace
				)

			#We will be making a figure with mutliple columns. 
			col_counter=0
			col_suffix=['_car','_bus','_rail']
			col_name=['car','bus','rail']
			
			for col in range(ncols):

				#Setup the col name you want to plot
				if ess=='all_workers':
					col_to_plot=occ+col_suffix[col]
				elif ess=='essential_workers':
					col_to_plot='E'+occ+col_suffix[col]

				print(col_to_plot)

				#Setup insets
				#Make a position for the legend ax (cax)
				divider = make_axes_locatable(axarr[col])
				cax_by_us = divider.append_axes("bottom", size="2%", pad=0)

				#Create position for historgram
				axin = axarr[col].inset_axes([0.0, 0.00, 1, 0.04])
				axin_london = axarr[col].inset_axes([0.62, 0.52, 0.38, 0.14])

				if direction=='home':
					# Label for legend
					label='Residents that commute by {0} \n (the {1} value covers {1} residents and more)'.format(col_name[col],residents_limit[ess][col_name[col]]) 
					
					# Plot main figure
					gp_MSOA_Ess_aggregated_destination.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=residents_limit[ess][col_name[col]],
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')
					
					# Plot London inset
					gp_MSOA_Ess_aggregated_destination.loc[gp_MSOA_Ess_aggregated_destination['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					#Set all values higher than limit to be the limit so that they pop up in the histogram.
					gp_MSOA_Ess_aggregated_destination.loc[gp_MSOA_Ess_aggregated_destination[col_to_plot] > residents_limit[ess][col_name[col]], col_to_plot] = residents_limit[ess][col_name[col]]
					a=np.array(gp_MSOA_Ess_aggregated_destination[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)

					#Set x limits for histogram
					# max_x=max(a)
					axin.set_xlim(0,residents_limit[ess][col_name[col]])
					axin.set_axis_off()


				elif direction=='work':
					# Label for legend
					label='Workers that commute by {0} \n (the {1} value covers {1} workers and more)'.format(col_name[col],workers_limit[ess][col_name[col]])

					# Plot main figure
					gp_MSOA_Ess_aggregated_origin.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=workers_limit[ess][col_name[col]],
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')

					# Plot London inset
					gp_MSOA_Ess_aggregated_origin.loc[gp_MSOA_Ess_aggregated_origin['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					#Set all values higher than limit to be the limit so that they pop up in the histogram.
					gp_MSOA_Ess_aggregated_origin.loc[gp_MSOA_Ess_aggregated_origin[col_to_plot] > workers_limit[ess][col_name[col]], col_to_plot] = workers_limit[ess][col_name[col]]
					# Get data for histogram
					a=np.array(gp_MSOA_Ess_aggregated_origin[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)

					#Set x limits for histogram
					# max_x=max(a)
					axin.set_xlim(0,workers_limit[ess][col_name[col]])
					axin.set_axis_off()


				# Titelke dabei
				extra_title='Commuting by {0}'.format(col_name[col]) 
				axarr[col].text(.03, .97, extra_title, ha='left', va='top', rotation=0, fontsize=11, color='black',
					transform=axarr[col].transAxes,bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':'black'})


				#Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
				axarr[col].set_axis_off()

				#Set axin_london up
				axin_london.set_aspect('equal')
				axin_london.set_title('Greater London Area', fontsize=6,color='0.3')

				for pos in ['top','bottom','left','right']:
					axin_london.spines[pos].set_linewidth(0.1)
					axin_london.spines[pos].set_color('0.2')

				# Set ticks parameters so they do not show
				axin_london.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
				axin_london.tick_params(axis='y',which='both',left=False,right=False, labelleft=False) 

				#Set up north arrow
				x, y, arrow_length = 0.95, 0.1, 0.03
				axarr[col].annotate('N', color='0.8',xy=(x, y), xytext=(x, y-arrow_length),
					arrowprops=dict(facecolor='0.6',edgecolor='0.6', width=1, headwidth=3,headlength=5),
					ha='center', va='center', fontsize=8,xycoords=axarr[col].transAxes)

				col_counter=col_counter+1				

			#Set figure title 
			if direction=='home':
				title= 'Residents in "{0}" commuting by different modes with a maximum limit for each mode'.format(plot_titles[occ])
				if ess=="essential_workers":
					title= 'Essential workers: \n' + title 
			elif direction=='work':
				title= 'Workers in "{0}" commuting by different modes with a maximum limit for each mode'.format(plot_titles[occ])
				if ess=="essential_workers":
					title= 'Essential workers: \n' + title 			 
			plt.suptitle(title, fontsize=15)

			#save or show
			# plt.show()

			#Set figure names
			if direction=='home':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_absolute_values_with_limit_{3}_{4}_{5}.png'.format(occ,direction,ess,residents_limit[ess]['car'],residents_limit[ess]['bus'],residents_limit[ess]['rail'])
			elif direction=='work':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_absolute_values_with_limit_{3}_{4}_{5}.png'.format(occ,direction,ess,workers_limit[ess]['car'],workers_limit[ess]['bus'],workers_limit[ess]['rail'])
			output=foldername_output+outputname
			plt.savefig(output)
			axin.clear()
			axin_london.clear()
			plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
			plt.clf() #clear the entire figure. Since we define the figure inside the loop, this is ok. We do this because otherwise there is some overlap of colors in the main figure..
			print ('Figure saved')


'''



############################
#4.4 Visualise relative share of transport modes per MSOA, for different home/work and different occupations.
############################

####################
#4.4.1  Calculate shares per MSOA per occupations (both for essential and all workers)
####################

#Calculate shares per MSOA per occupations (both for essential and all workers)

to_calculate_share_for_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9','EO1','EO2','EO3','EO4','EO5','EO6','EO7','EO8','EO9']

for occ in to_calculate_share_for_list:
	print (occ)
	occ_car=occ+'_car'
	occ_bus=occ+'_bus'
	occ_rail=occ+'_rail'

	share_car=occ+'_car_msoa_share'
	share_bus=occ+'_bus_msoa_share'
	share_rail=occ+'_rail_msoa_share'

	#Origin
	gp_MSOA_Ess_aggregated_origin[share_car]=gp_MSOA_Ess_aggregated_origin[occ_car]/gp_MSOA_Ess_aggregated_origin[[occ_car,occ_bus,occ_rail]].sum(axis=1)
	gp_MSOA_Ess_aggregated_origin[share_bus]=gp_MSOA_Ess_aggregated_origin[occ_bus]/gp_MSOA_Ess_aggregated_origin[[occ_car,occ_bus,occ_rail]].sum(axis=1)
	gp_MSOA_Ess_aggregated_origin[share_rail]=gp_MSOA_Ess_aggregated_origin[occ_rail]/gp_MSOA_Ess_aggregated_origin[[occ_car,occ_bus,occ_rail]].sum(axis=1)


	#Destination
	gp_MSOA_Ess_aggregated_destination[share_car]=gp_MSOA_Ess_aggregated_destination[occ_car]/gp_MSOA_Ess_aggregated_destination[[occ_car,occ_bus,occ_rail]].sum(axis=1)
	gp_MSOA_Ess_aggregated_destination[share_bus]=gp_MSOA_Ess_aggregated_destination[occ_bus]/gp_MSOA_Ess_aggregated_destination[[occ_car,occ_bus,occ_rail]].sum(axis=1)
	gp_MSOA_Ess_aggregated_destination[share_rail]=gp_MSOA_Ess_aggregated_destination[occ_rail]/gp_MSOA_Ess_aggregated_destination[[occ_car,occ_bus,occ_rail]].sum(axis=1)

# To explore
# gp_MSOA_Ess_aggregated_destination[['EO1_car_msoa_share','EO1_bus_msoa_share','EO1_rail_msoa_share',occ_car,occ_bus,occ_rail]].head()


####################
#4.4.2 Create maps of relative shares per MSOA.
####################
'''
print ('\n We are now plotting shares per modes per msoa for different occupations. essential workers per mode but with limits..')


#Set up iteration lists
occupation_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9']
direction_list=['home','work'] #'work' and or 'home'
ess_list=['all_workers'] #'essential_workers' and or 'all_workers'


for direction in direction_list:
	for ess in ess_list:
		for occ in occupation_list:
			print(direction,ess,occ)


			#Setup figure
			figsize_x_cm=42 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
			figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
			figsize_y_cm=22
			figsize_y_inches=figsize_y_cm/2.54

			#define number of subplots.
			ncols=3
			nrows=1

			#Set up fig and ax
			fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
			#axarr[row][col] if row>1
			#axarr[col] if row=1

			left   =  0.00  # the left side of the subplots of the figure
			right  =  1 	# the right side of the subplots of the figure
			bottom =  0.07  # the bottom of the subplots of the figure
			top    =  0.93  # the top of the subplots of the figure
			wspace =  .02   # the amount of width reserved for blank space between subplots
			hspace =  .00   # the amount of height reserved for white space between subplots

			# This function actually adjusts the sub plots using the above paramters
			plt.subplots_adjust(
			left    =  left, 
			bottom  =  bottom, 
			right   =  right, 
			top     =  top, 
			wspace  =  wspace, 
			hspace  =  hspace
				)

			#We will be making a figure with mutliple columns. 
			col_counter=0
			col_suffix=['_car','_bus','_rail']
			col_name=['car','bus','rail']
			
			for col in range(ncols):

				#Setup the col name you want to plot
				if ess=='all_workers':
					col_to_plot=occ+col_suffix[col]+'_msoa_share'
				elif ess=='essential_workers':
					col_to_plot='E'+occ+col_suffix[col]+'_msoa_share'

				print(col_to_plot)

				#Setup insets
				#Make a position for the legend ax (cax)
				divider = make_axes_locatable(axarr[col])
				cax_by_us = divider.append_axes("bottom", size="2%", pad=0)

				#Create position for historgram
				axin = axarr[col].inset_axes([0.0, 0.00, 1, 0.04])
				axin_london = axarr[col].inset_axes([0.62, 0.52, 0.38, 0.14])

				if direction=='home':
					# Label for legend
					label='Share of residents in the MSOA that commute by {0}'.format(col_name[col]) 
					
					# Plot main figure
					gp_MSOA_Ess_aggregated_destination.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=1,
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')
					
					# Plot London inset
					gp_MSOA_Ess_aggregated_destination.loc[gp_MSOA_Ess_aggregated_destination['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					a=np.array(gp_MSOA_Ess_aggregated_destination[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					#First get mean, independently from how we treated the max, then plot it
					mean=gp_MSOA_Ess_aggregated_destination[col_to_plot].mean()
					axin.axvline(mean, color='0.8', linestyle='--', dashes=(2, 2), linewidth=2)

					#Set x limits for histogram
					# max_x=max(a)
					axin.set_xlim(0,1)
					axin.set_axis_off()


				elif direction=='work':
					# Label for legend
					label='Share of workers in the MSOA that commute by {0}'.format(col_name[col])

					# Plot main figure
					gp_MSOA_Ess_aggregated_origin.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=1,
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')

					# Plot London inset
					gp_MSOA_Ess_aggregated_origin.loc[gp_MSOA_Ess_aggregated_origin['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					# Get data for histogram
					a=np.array(gp_MSOA_Ess_aggregated_origin[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					#Plot mean
					#First get mean, independently from how we treated the max, then plot it
					mean=gp_MSOA_Ess_aggregated_origin[col_to_plot].mean()
					axin.axvline(mean, color='0.8', linestyle='--', dashes=(2, 2), linewidth=2)  #dashes=(length, interval space)


					#Set x limits for histogram
					# max_x=max(a)
					axin.set_xlim(0,1)
					axin.set_axis_off()


				# Titelke dabei
				extra_title='Commuting by {0}'.format(col_name[col]) 
				axarr[col].text(.03, .97, extra_title, ha='left', va='top', rotation=0, fontsize=11, color='black',
					transform=axarr[col].transAxes,bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':'black'})


				#Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
				axarr[col].set_axis_off()

				#Set axin_london up
				axin_london.set_aspect('equal')
				axin_london.set_title('Greater London Area', fontsize=6,color='0.3')

				for pos in ['top','bottom','left','right']:
					axin_london.spines[pos].set_linewidth(0.1)
					axin_london.spines[pos].set_color('0.2')

				# Set ticks parameters so they do not show
				axin_london.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
				axin_london.tick_params(axis='y',which='both',left=False,right=False, labelleft=False) 

				#Set up north arrow
				x, y, arrow_length = 0.95, 0.1, 0.03
				axarr[col].annotate('N', color='0.8',xy=(x, y), xytext=(x, y-arrow_length),
					arrowprops=dict(facecolor='0.6',edgecolor='0.6', width=1, headwidth=3,headlength=5),
					ha='center', va='center', fontsize=8,xycoords=axarr[col].transAxes)

				col_counter=col_counter+1				

			#Set figure title 
			if direction=='home':
				title= 'Share of residents in "{0}" commuting by different modes'.format(plot_titles[occ])
				if ess=="essential_workers":
					title= 'Essential workers: \n' + title 
			elif direction=='work':
				title= 'Share of workers in "{0}" commuting by different modes'.format(plot_titles[occ])
				if ess=="essential_workers":
					title= 'Essential workers: \n' + title 			 
			plt.suptitle(title, fontsize=15)

			#save or show
			# plt.show()

			#Set figure names
			if direction=='home':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_share_per_msoa.png'.format(occ,direction,ess)
			elif direction=='work':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_share_per_msoa.png'.format(occ,direction,ess)
			output=foldername_output+outputname
			plt.savefig(output)
			axin.clear()
			axin_london.clear()
			plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
			plt.clf() #clear the entire figure. Since we define the figure inside the loop, this is ok. We do this because otherwise there is some overlap of colors in the main figure..
			print ('Figure saved')

'''

####################
#4.4.2 Create maps of relative shares per MSOA but with limits for the different modes.
####################
'''
#Limits were chosen upon visual inspection and will be the same for all occupations

#Hard-coded limit.
residents_limit={}
workers_limit={}
residents_limit['all_workers']={'car':0.7,'bus':0.2,'rail':0.1}
workers_limit['all_workers']={'car':0.7,'bus':0.2,'rail':0.1}
residents_limit['essential_workers']={'car':0.7,'bus':0.2,'rail':0.1}
workers_limit['essential_workers']={'car':0.7,'bus':0.2,'rail':0.1}


print ('\n We are now plotting shares per modes per msoa for different occupations. essential workers per mode but with limits..')


#Set up iteration lists
occupation_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9']
# occupation_list=['O1']
direction_list=['work'] #'work' and or 'home'
ess_list=['all_workers'] #'essential_workers' and or 'all_workers'


for direction in direction_list:
	for ess in ess_list:
		for occ in occupation_list:
			print(direction,ess,occ)


			#Setup figure
			figsize_x_cm=42 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
			figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
			figsize_y_cm=22
			figsize_y_inches=figsize_y_cm/2.54

			#define number of subplots.
			ncols=3
			nrows=1

			#Set up fig and ax
			fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
			#axarr[row][col] if row>1
			#axarr[col] if row=1

			left   =  0.00  # the left side of the subplots of the figure
			right  =  1 	# the right side of the subplots of the figure
			bottom =  0.07  # the bottom of the subplots of the figure
			top    =  0.93  # the top of the subplots of the figure
			wspace =  .02   # the amount of width reserved for blank space between subplots
			hspace =  .00   # the amount of height reserved for white space between subplots

			# This function actually adjusts the sub plots using the above paramters
			plt.subplots_adjust(
			left    =  left, 
			bottom  =  bottom, 
			right   =  right, 
			top     =  top, 
			wspace  =  wspace, 
			hspace  =  hspace
				)

			#We will be making a figure with mutliple columns. 
			col_counter=0
			col_suffix=['_car','_bus','_rail']
			col_name=['car','bus','rail']
			
			for col in range(ncols):

				#Setup the col name you want to plot
				if ess=='all_workers':
					col_to_plot=occ+col_suffix[col]+'_msoa_share'
				elif ess=='essential_workers':
					col_to_plot='E'+occ+col_suffix[col]+'_msoa_share'

				print(col_to_plot)

				#Setup insets
				#Make a position for the legend ax (cax)
				divider = make_axes_locatable(axarr[col])
				cax_by_us = divider.append_axes("bottom", size="2%", pad=0)

				#Create position for historgram
				axin = axarr[col].inset_axes([0.0, 0.00, 1, 0.04])
				axin_london = axarr[col].inset_axes([0.62, 0.52, 0.38, 0.14])

				if direction=='home':
					# Label for legend
					if col_name[col]=='car':
						label='Share of residents in the MSOA that commute by {0} \n (the {1} value covers shares of {1} and less)'.format(col_name[col],residents_limit[ess][col_name[col]])   
					else:
						label='Share of residents in the MSOA that commute by {0} \n (the {1} value covers shares of {1} and more)'.format(col_name[col],residents_limit[ess][col_name[col]])   
					

					# Plot main figure
					if col_name[col]=='car':
						gp_MSOA_Ess_aggregated_destination.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmin=residents_limit[ess][col_name[col]],
						legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')
					else:
						gp_MSOA_Ess_aggregated_destination.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=residents_limit[ess][col_name[col]],
						legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')

					
					# Plot London inset
					gp_MSOA_Ess_aggregated_destination.loc[gp_MSOA_Ess_aggregated_destination['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					#Set all values higher than limit to be the limit so that they pop up in the histogram.
					if col_name[col]=='car':
						gp_MSOA_Ess_aggregated_destination.loc[gp_MSOA_Ess_aggregated_destination[col_to_plot] < residents_limit[ess][col_name[col]], col_to_plot] = residents_limit[ess][col_name[col]]
					else:
						gp_MSOA_Ess_aggregated_destination.loc[gp_MSOA_Ess_aggregated_destination[col_to_plot] > residents_limit[ess][col_name[col]], col_to_plot] = residents_limit[ess][col_name[col]]


					# Get data for histogram
					a=np.array(gp_MSOA_Ess_aggregated_destination[col_to_plot])
					
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					
					#Plot mean in histogram
					#First get mean, independently from how we treated the max, then plot it
					mean=gp_MSOA_Ess_aggregated_destination[col_to_plot].mean()
					axin.axvline(mean, color='0.8', linestyle='--', dashes=(2, 2), linewidth=2)

					#Set x limits for histogram
					max_x=max(a)
					axin.set_xlim(0,max_x)
					if col_name[col]=='car':
						axin.set_xlim(residents_limit[ess][col_name[col]],1)
					axin.set_axis_off()


				elif direction=='work':
					# Label for legend
					if col_name[col]=='car':
						label='Share of workers in the MSOA that commute by {0} \n (the {1} value covers shares of {1} and less)'.format(col_name[col],workers_limit[ess][col_name[col]])
					else:
						label='Share of workers in the MSOA that commute by {0} \n (the {1} value covers shares of {1} and more)'.format(col_name[col],workers_limit[ess][col_name[col]])
					

					# Plot main figure
					if col_name[col]=='car':
						gp_MSOA_Ess_aggregated_origin.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmin=workers_limit[ess][col_name[col]],
						legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')
					else:
						gp_MSOA_Ess_aggregated_origin.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=workers_limit[ess][col_name[col]],
						legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')

					# Plot London inset
					gp_MSOA_Ess_aggregated_origin.loc[gp_MSOA_Ess_aggregated_origin['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					#Set all values higher than limit to be the limit so that they pop up in the histogram.
					if col_name[col]=='car':
						gp_MSOA_Ess_aggregated_origin.loc[gp_MSOA_Ess_aggregated_origin[col_to_plot] < workers_limit[ess][col_name[col]], col_to_plot] = workers_limit[ess][col_name[col]]

					else:
						gp_MSOA_Ess_aggregated_origin.loc[gp_MSOA_Ess_aggregated_origin[col_to_plot] > workers_limit[ess][col_name[col]], col_to_plot] = workers_limit[ess][col_name[col]]

					# Get data for histogram
					a=np.array(gp_MSOA_Ess_aggregated_origin[col_to_plot])
					
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75)
					
					#Plot mean in histogram
					#First get mean, independently from how we treated the max, then plot it
					mean=gp_MSOA_Ess_aggregated_origin[col_to_plot].mean()
					axin.axvline(mean, color='0.8', linestyle='--', dashes=(2, 2), linewidth=2)  #dashes=(length, interval space)

					#Set x limits for histogram
					max_x=max(a)
					axin.set_xlim(0,max_x)
					if col_name[col]=='car':
						axin.set_xlim(workers_limit[ess][col_name[col]],1)
					axin.set_axis_off()


				# Titelke dabei
				extra_title='Commuting by {0}'.format(col_name[col]) 
				axarr[col].text(.03, .97, extra_title, ha='left', va='top', rotation=0, fontsize=11, color='black',
					transform=axarr[col].transAxes,bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':'black'})


				#Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
				axarr[col].set_axis_off()

				#Set axin_london up
				axin_london.set_aspect('equal')
				axin_london.set_title('Greater London Area', fontsize=6,color='0.3')

				for pos in ['top','bottom','left','right']:
					axin_london.spines[pos].set_linewidth(0.1)
					axin_london.spines[pos].set_color('0.2')

				# Set ticks parameters so they do not show
				axin_london.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
				axin_london.tick_params(axis='y',which='both',left=False,right=False, labelleft=False) 

				#Set up north arrow
				x, y, arrow_length = 0.95, 0.1, 0.03
				axarr[col].annotate('N', color='0.8',xy=(x, y), xytext=(x, y-arrow_length),
					arrowprops=dict(facecolor='0.6',edgecolor='0.6', width=1, headwidth=3,headlength=5),
					ha='center', va='center', fontsize=8,xycoords=axarr[col].transAxes)

				col_counter=col_counter+1				

			#Set figure title 
			if direction=='home':
				title= 'Share of residents in "{0}" commuting by different modes'.format(plot_titles[occ])
				if ess=="essential_workers":
					title= 'Essential workers: \n' + title 
			elif direction=='work':
				title= 'Share of workers in "{0}" commuting by different modes'.format(plot_titles[occ])
				if ess=="essential_workers":
					title= 'Essential workers: \n' + title 			 
			plt.suptitle(title, fontsize=15)

			#save or show
			# plt.show()

			#Set figure names
			if direction=='home':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_share_per_msoa_with_limit_{3}_{4}_{5}.png'.format(occ,direction,ess,residents_limit[ess]['car'],residents_limit[ess]['bus'],residents_limit[ess]['rail'])
			elif direction=='work':
				outputname='Occ_{0}_{2}_by_{1}_three_modes_share_per_msoa_with_limit_{3}_{4}_{5}.png'.format(occ,direction,ess,workers_limit[ess]['car'],workers_limit[ess]['bus'],workers_limit[ess]['rail'])
			output=foldername_output+outputname
			plt.savefig(output)
			axin.clear()
			axin_london.clear()
			plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
			plt.clf() #clear the entire figure. Since we define the figure inside the loop, this is ok. We do this because otherwise there is some overlap of colors in the main figure..
			print ('Figure saved')

'''

############################
#4.5 Visualise the mean trip lengths per occupation and mode 
############################


###############
#4.5.1 Join the trip_length file with the geopandas.
###############

#For all msoas.
gp_MSOA_trip_length = gp_MSOA.merge(df_MSOA_trip_length, left_on='MSOA11CD', right_on='zone')

#Check whether dimensions are still the same after the merge. 
if gp_MSOA_trip_length.shape[0] != df_MSOA_trip_length.shape[0]:
	print ('\n The merge we just performed has reduced the dimensions of your inputdata that was aggregated on origin. The shapes of both datasets are:')
	print (gp_MSOA_trip_length.shape)
	print (df_MSOA_trip_length.shape)
else:
	print ('\nThis merge has not reduced the dimensions of your inputdata, which was trip length.')
 


###############
#4.5.1 Make maps.
###############

# Hardcoded limits for the maps. Limits were chosen based on Iacopo's boxplot.
residents_limit=50
workers_limit=50


print ('\n We are now plotting the maps of different occupations and essential workers per mode.')


#Set up iteration lists
occupation_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9']
direction_list=['home','work'] #'work' and or 'home'



for direction in direction_list:
		for occ in occupation_list:
			print(direction,occ)

			#Setup figure
			figsize_x_cm=42 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
			figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
			figsize_y_cm=22
			figsize_y_inches=figsize_y_cm/2.54

			#define number of subplots.
			ncols=3
			nrows=1

			#Set up fig and ax
			fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
			#axarr[row][col] if row>1
			#axarr[col] if row=1

			left   =  0.00  # the left side of the subplots of the figure
			right  =  1 	# the right side of the subplots of the figure
			bottom =  0.07  # the bottom of the subplots of the figure
			top    =  0.93  # the top of the subplots of the figure
			wspace =  .02   # the amount of width reserved for blank space between subplots
			hspace =  .00   # the amount of height reserved for white space between subplots

			# This function actually adjusts the sub plots using the above paramters
			plt.subplots_adjust(
			left    =  left, 
			bottom  =  bottom, 
			right   =  right, 
			top     =  top, 
			wspace  =  wspace, 
			hspace  =  hspace
				)

			#We will be making a figure with mutliple columns. 
			col_counter=0
			col_suffix=[' Road',' Bus',' Rail']
			col_name=['car','bus','rail']
			
			for col in range(ncols):

				#Setup insets
				#Make a position for the legend ax (cax)
				divider = make_axes_locatable(axarr[col])
				cax_by_us = divider.append_axes("bottom", size="2%", pad=0)

				#Create position for histogram
				axin = axarr[col].inset_axes([0.0, 0.00, 1, 0.04])
				axin_london = axarr[col].inset_axes([0.62, 0.52, 0.38, 0.14])

				if direction=='home':
					# Label for legend
					label='Mean trip length of commute (in min) of residents using {0}'.format(col_name[col]) 

					#Setup the col name you want to plot
					col_to_plot='Res ' + occ + col_suffix[col]
					print(col_to_plot)

					# Plot main figure
					gp_MSOA_trip_length.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=residents_limit,
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')
					
					# Plot London inset
					gp_MSOA_trip_length.loc[gp_MSOA_trip_length['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					#Set all values higher than limit to be the limit so that they pop up in the histogram.
					gp_MSOA_trip_length.loc[gp_MSOA_trip_length[col_to_plot] > residents_limit, col_to_plot] = residents_limit
					# Plot histogram in inset
					a=np.array(gp_MSOA_trip_length[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75,zorder=1)
					#Plot mean
					#First get mean, independently from how we treated the max, then plot it
					mean=gp_MSOA_trip_length[col_to_plot].mean()
					axin.axvline(mean, color='0.8', linestyle='solid', linewidth=2,zorder=10)

				elif direction=='work':
					# Label for legend
					label='Mean trip length of commute (in min) of workers using {0}'.format(col_name[col]) 

					#Setup the col name you want to plot
					col_to_plot='Empl ' + occ + col_suffix[col]
					print(col_to_plot)

					# Plot main figure
					gp_MSOA_trip_length.plot(ax=axarr[col],column=col_to_plot,legend=True,cax=cax_by_us,vmax=workers_limit,
					legend_kwds={'label': label,'orientation': "horizontal"},cmap='YlOrBr')

					# Plot London inset
					gp_MSOA_trip_length.loc[gp_MSOA_trip_length['MSOA11CD'].isin(MSOA_list_london)].plot(ax=axin_london,column=col_to_plot,cmap='YlOrBr')
			
					# Plot histogram in inset
					#Set all values higher than limit to be the limit so that they pop up in the histogram.
					gp_MSOA_trip_length.loc[gp_MSOA_trip_length[col_to_plot] > workers_limit, col_to_plot] = workers_limit
					# Plot histogram in inset
					a=np.array(gp_MSOA_trip_length[col_to_plot])
					# Define weights so that sum of bars = 1
					weighta=np.ones_like(a)/float(len(a))
					n1, bins1, patches1 = axin.hist(a, bins=50, weights=weighta, facecolor='black', alpha=0.75,zorder=1)
					#Plot mean
					#First get mean, independently from how we treated the max, then plot it
					mean=gp_MSOA_trip_length[col_to_plot].mean()
					axin.axvline(mean, color='0.8', linestyle='solid', linewidth=2,zorder=10)


				# Titelke dabei
				extra_title='Commuting by {0}'.format(col_name[col]) 
				axarr[col].text(.03, .97, extra_title, ha='left', va='top', rotation=0, fontsize=11, color='black',
					transform=axarr[col].transAxes,bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':'black'})

				#Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
				axarr[col].set_axis_off()

				#Set axin_london up
				axin_london.set_aspect('equal')
				axin_london.set_title('Greater London Area', fontsize=6,color='0.3')

				for pos in ['top','bottom','left','right']:
					axin_london.spines[pos].set_linewidth(0.1)
					axin_london.spines[pos].set_color('0.2')

				# Set ticks parameters so they do not show
				axin_london.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
				axin_london.tick_params(axis='y',which='both',left=False,right=False, labelleft=False) 
				
				#Set x limits for histogram
				max_x=max(a)
				axin.set_xlim(0,max_x)
				axin.set_axis_off()

				#Set up north arrow
				x, y, arrow_length = 0.95, 0.1, 0.03
				axarr[col].annotate('N', color='0.8',xy=(x, y), xytext=(x, y-arrow_length),
					arrowprops=dict(facecolor='0.6',edgecolor='0.6', width=1, headwidth=3,headlength=5),
					ha='center', va='center', fontsize=8,xycoords=axarr[col].transAxes)

				col_counter=col_counter+1				

			#Set figure title 
			if direction=='home':
				title= 'Mean trip length of commute by residents in "{0}"'.format(plot_titles[occ])
			elif direction=='work':
				title= 'Mean trip length of commute by workers in "{0}"'.format(plot_titles[occ])			 
			plt.suptitle(title, fontsize=15)

			#save or show
			# plt.show()

			#Set figure names
			if direction=='home':
				outputname='Occ_{0}_mean_trip_length_at_{1}_for_three_modes_absolute_values_with_limit_{2}.png'.format(occ,direction,residents_limit)
			elif direction=='work':
				outputname='Occ_{0}_mean_trip_length_at_{1}_for_three_modes_absolute_values_with_limit_{2}.png'.format(occ,direction,workers_limit)
			output=foldername_output+outputname
			plt.savefig(output)
			axin.clear()
			axin_london.clear()
			plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
			plt.clf() #clear the entire figure. Since we define the figure inside the loop, this is ok. We do this because otherwise there is some overlap of colors in themain figure..
			print ('Figure saved')




################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################


'''
gp_MSOA_Occ_NoMode_aggregated_origin.shape

a=gp_MSOA_Occ_NoMode_aggregated_origin.loc[gp_MSOA_Occ_NoMode_aggregated_origin['MSOA11CD']=='E02000001']


b=gp_MSOA_Occ_NoMode_aggregated_origin.loc[gp_MSOA_Occ_NoMode_aggregated_origin['MSOA11CD'].str.contains('E02000', na=False)]


df.loc[df['column_name'] == some_value]
'''

# ax.legend(loc='upper right')
# ax.get_legend().set_bbox_to_anchor((0.5,0.5)) #position legend title in the ax
# ax.get_legend().set_title('lol',)  #set legend title.

"# The legend is actually a Colorbar object. To change the legend's font size, ",
"# we have to get hold of the Colorbar's Axes object, and call .tick_params() ",
"# on that. ",
" ",
"# First, we call the .plot() method as usual, but we capture the return value ",
"# which is the Axes of the map. ",
"ax = world.plot(column='gdp_per_cap', cmap='OrRd', legend=True) ",
" ",
"# We can use this to get hold of the Figure that contains the Axes. ",
"fig = ax.figure ",
" ",
"# The Figure has two Axes: one for the map, and one for the Colorbar. The ",
"# one we care about is the second one. ",
"cb_ax = fig.axes[1] ",
" ",
"# We can now set the font size for the Colorbar. Other parameters for ",
"# tick_params are documented at: ",
"# https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.tick_params.html ",
"cb_ax.tick_params(labelsize=100)"

'''
You could normalize the color by using the DivergingNorm function in matplotlib.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import geopandas as gpd
plt.style.use('seaborn-white')

# generate data
gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gdf = gdf[gdf.continent == 'Africa']
gdf['random'] = np.random.gamma(2, 2, len(gdf)) - 2

# normalize color
vmin, vmax, vcenter = gdf.random.min(), gdf.random.max(), 0
divnorm = colors.DivergingNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
# create a normalized colorbar
cbar = plt.cm.ScalarMappable(norm=divnorm, cmap='RdBu')

# plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
# with no normalization
gdf.plot(column='random', cmap='RdBu', legend=True, ax=ax1)
# with normalization
gdf.plot(column='random', cmap='RdBu', legend=False, norm=divnorm, ax=ax2)
# add colorbar
fig.colorbar(cbar, ax=ax2)

'''



'''


print ('\n We are now plotting the maps for different occupations')

#Setup figure
ncols=2 
nrows=2

figsize_x_cm=30 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
figsize_y_cm=20
figsize_y_inches=figsize_y_cm/2.54

fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
#axarr[row][col]

left   =  0.05  # the left side of the subplots of the figure
right  =  0.97    # the right side of the subplots of the figure
bottom =  0.03    # the bottom of the subplots of the figure
top    =  0.90    # the top of the subplots of the figure
wspace =  .65     # the amount of width reserved for blank space between subplots
hspace =  .15    # the amount of height reserved for white space between subplots

# This function actually adjusts the sub plots using the above paramters
plt.subplots_adjust(
left    =  left, 
bottom  =  bottom, 
right   =  right, 
top     =  top, 
wspace  =  wspace, 
hspace  =  hspace
	)

#Set figure title 
title=str('Occupation')
plt.suptitle(title, fontsize=20)


occupation_list=['O1','O2','O3','O4','O5','O6','O7','O8','O9']
for occ in occupation_list:
	print (occ)

# Absolute values
gp_MSOA_Occ_NoMode_aggregated_origin.plot(ax=axarr[0][0],column='O1',legend=True,
			norm=clr.Normalize(vmin=0,vmax=50000),cmap='RdBu_r')
gp_MSOA_Occ_NoMode_aggregated_destination.plot(ax=axarr[0][1],column='O1',legend=True,
			norm=clr.Normalize(vmin=0,vmax=50000),cmap='RdBu_r')

# Relative values
gp_MSOA_Occ_NoMode_aggregated_origin.plot(ax=axarr[1][0],column='relO1',legend=True,
			norm=clr.Normalize(vmin=0,vmax=1),cmap='RdBu_r')
gp_MSOA_Occ_NoMode_aggregated_destination.plot(ax=axarr[1][1],column='relO1',legend=True,
			norm=clr.Normalize(vmin=0,vmax=1),cmap='RdBu_r')

# set aspect to equal. This is done automatically when using *geopandas* plot on it's own, but not when working with pyplot directly. 
for axrow in axarr:
	for ax in axrow:
		ax.set_aspect('equal')

plt.show()
plt.close('all')
'''	
'''
		#axarr[row][col].legend(loc='upper right')
		#axarr[row][col].get_legend().set_bbox_to_anchor((1,0.5))
		#axarr[row][col].get_legend().set_title('lol') 
		


#gp_MSOA_GM.plot(ax=axarr[0][0],column='employment',legend=False)
#gp_MSOA_GM.plot(ax=axarr[0][1],column='E',legend=False)
#gp_MSOA_GM.plot(ax=axarr[1][0],column='X',legend=False)
#gp_MSOA_GM.plot(ax=axarr[1][1],column='S',legend=False)
'''
'''
sc0= axarr[1][0].scatter(x=df_to_plot['Dij_car'],y=df_to_plot['Cumsum_percentage_car'], c=color_dict_mode['car'],s=1)
sc1= axarr[1][1].scatter(x=df_to_plot['Dij_bus'],y=df_to_plot['Cumsum_percentage_bus'], c=color_dict_mode['bus'],s=1)
sc2= axarr[1][2].scatter(x=df_to_plot['Dij_rail'],y=df_to_plot['Cumsum_percentage_rail'], c=color_dict_mode['rail'], s=1)

#Set titles
if home_to_work:
	title='Commuters leaving home from MSOA: {0}'.format(MSOA)
elif work_to_home:
	title='Commuters leaving work from MSOA: {0}'.format(MSOA)

plt.suptitle(title, fontsize=14)

#Set boxes
axarr[0][0].text(.97, .97, 'by car', ha='right', va='top', rotation=0, fontsize=11, color='black',transform=axarr[0][0].transAxes,
			bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':color_dict_mode['car']})
axarr[0][1].text(.97, .97, 'by bus', ha='right', va='top', rotation=0, fontsize=11, color='black',transform=axarr[0][1].transAxes,
			bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':color_dict_mode['bus']})
axarr[0][2].text(.97, .97, 'by rail', ha='right', va='top', rotation=0, fontsize=11, color='black',transform=axarr[0][2].transAxes,
			bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':color_dict_mode['rail']})

'''

'''
variables_to_plot=['population','working population','E','X','E','S']
counter=0
for row in range(nrows):
	for col in range(ncols):

		color_max=50000
		gp_MSOA_GM_PWPXSE.plot(ax=axarr[row][col],column=variables_to_plot[counter],legend=True,
			norm=clr.Normalize(vmin=0,vmax=50000),cmap='RdBu_r')

		#axarr[row][col].legend(loc='upper right')
		#axarr[row][col].get_legend().set_bbox_to_anchor((1,0.5))
		#axarr[row][col].get_legend().set_title('lol') 
		
		# set aspect to equal. This is done automatically when using *geopandas* plot on it's own, but not when working with pyplot directly. 
		axarr[row][col].set_aspect('equal')

		#Set title of subplot
		title_name=variables_to_plot[counter]
		axarr[row][col].set_title(title_name,fontsize=12)

		##Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
		axarr[row][col].get_xaxis().set_visible(False)
		axarr[row][col].get_yaxis().set_visible(False)

		# Make frame lighter and change line-width:
		for pos in ['top','bottom','left','right']:
			axarr[row][col].spines[pos].set_linewidth(0.5)
			axarr[row][col].spines[pos].set_color('0.6')

		counter=counter+1
'''






################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################




########################################################
#3. Unfold data to become dataframe in matrix style. 
########################################################

# Our aim is to construct a 8436 by 8436 dataframe that can hold the trips, Occ, etc for each MSOA pair. 
#  and ththat can easily be used in further analysis.


############################
#3.1 Define a helper function to recreate the OD matrix
############################
'''

def to_dataframe_OD_matrix(df_unique_msoa_list, df_input, value_name, row_name='destination_msoacode', column_name='origin_msoacode'):
	""" 
	This function takes a dataframe with pairs of values as input and creates an 
	8436 by 8436 dataframe of all MSOAs in the UK that stores these values as a matrix.
	Pairs with no values get NaN
	The columns in our matrix are origin, the rows are destination. 
	df_unique_msoa_list should be a list of unque msoa identifiers in a dataframe with columname='MSOA'
	"""

	print('\n We are unfolding the {0} and transforming it into an OD matrix'.format(value_name))

	#Setup storage	
	df_storage=df_unique_msoa_list.copy()
	df_storage2=df_unique_msoa_list.copy()

	#Take a copy of the df_input to work on. Set origin msoa_code to be the index, this makes the filtering a lot faster
	df_filtering=df_input[['{0}'.format(row_name),'{0}'.format(column_name),'{0}'.format(value_name)]].copy()
	
	#Set origin msoa_code to be the index, this makes the filtering a lot faster
	df_filtering=df_filtering.set_index(column_name)

	#Set up counter
	msoa_counter=1
	for MSOA in list(df_unique_msoa_list['MSOA']): #['E02000001','E02000002','E02000003']:
		#We will work with one origin each time.
		#if msoa_counter>3000:
		#	print(MSOA)

		#If the MSOA that is an origin is in the df_input, we go ahead
		if MSOA in df_filtering.index:
			#print ('This one is in the list')

			#We first select only those rows where the index (origin_msoacode) == a value
			#effectively keeping all the destination for that MSOA.)

			df_filtered=df_filtering.loc[[MSOA]].copy() #.loc[] works on index. 
			#Note that we use a list inside .loc[] but with only one element. This is because of the following issue:
			#https://stackoverflow.com/questions/20383647/pandas-selecting-by-label-sometimes-return-series-sometimes-returns-dataframe
			df_filtered=df_filtered.reset_index()

			#print("Filtered")
			#print(df_filtered.shape)
			#print(df_filtered.head())

			#We then join this list with destinations for one MSOA with a list of all MSOAs. 
			#That way, pairs for which there was no value will be filled up with NaN
			#print("Unique")
			#print(df_unique_msoa_list.shape)
			#print(df_unique_msoa_list.head())

			df_tussen=df_unique_msoa_list.copy()
			df_tussen=pd.merge(df_tussen, df_filtered[[row_name,value_name]], how='left',left_on='MSOA', right_on=row_name).copy()
			
			#print("Tussen")
			#print(df_tussen.shape)
			#print(df_tussen.head())

			#The full list of destinations (with values and NaN) for one origin MSOA is than attached to the storage
			# as a column, the column name is the name of the MSOA we used as the origin.
			df_storage[MSOA]=df_tussen[value_name].copy()

			#print("Storage")
			#print(df_storage.head())

			#This is another way of getting the data in storage, this time joing key pairs so we are sure nothing is missed
			#This technique is slower though
			#df_storage2=df_storage2.join(df_tussen.set_index(row_name), how='left', on='MSOA',rsuffix='_right') #DataFrame.join always uses other’s index but we can use any column in df
			#df_storage2=df_storage2.drop(columns=['MSOA_right'])
			#df_storage2=df_storage2.rename(columns={value_name: MSOA})

			#print("Storage2")
			#print(df_storage2.head())

		#If there is an MSOA that is not in the origin MSOAs of the input, we create a column filled of NaN
		else:
			#print('Niet in de lijst jongens')
			df_storage[MSOA]=np.nan

		#Print progress
		if msoa_counter%10==0:
			print('The code has just finished treating MSOA number: ' + str(msoa_counter) + ' out of ' + str(len(list(df_unique_msoa_list['MSOA']))))
		#Update counter
		msoa_counter=msoa_counter+1

	print('\n We finished transforming df_input into an OD matrix')
	return df_storage
'''


############################
#3.2 Write out OD matrices to feather 
############################
'''
#We store the expanded dataframes by using feather (a binare file format to store, a.o., pandas dataframes)


for input_type in input_list:
	for mode in mode_list:
		print ("\n We are creating the matrix for {0} and mode: {1}".format(input_type,mode))

		#Start timing
		start_time = time.time()
		
		#Use helper function to extract 
		value_name_creator='{0}_{1}'.format(input_type,mode)
		a= to_dataframe_OD_matrix(df_MSOA_unique_values, available_inputfiles[input_type][mode], value_name_creator, row_name='destination_msoacode', column_name='origin_msoacode')
		
		#Read out full matrix
		outputname=foldername_output + '{0}_{1}_OD_matrix.ftr'.format(input_type,mode)
		a.to_feather(outputname)

		print ("\n Treating {0} for {1} took about".format(input_type,mode), round((time.time()-start_time)/60), "minutes")


#a_terug= pd.read_feather(out)
'''

########################################################
#4. Store data for each MSOA in a seperate pickle. 
########################################################

# This code creates a pickle for each MSOA storing its information for the different input_types and modes
# The code works both in the home-to-work direction as in the work-to-home direction. 


############################
#4.1 Initialise Pickles for all MSOAs
# You only need to do this step once. Unless you want to overwrite all your data. 
############################
'''
#Setup storage	
print('\nWe are starting the setup of the pickles, this will create 16k files on your computer. Be aware.')

df_storage_home_to_work=df_MSOA_unique_values.copy()
df_storage_home_to_work=df_storage_home_to_work.rename(columns={'MSOA': 'MSOA_work'}) #Rename for clarity

df_storage_work_to_home=df_MSOA_unique_values.copy()
df_storage_work_to_home=df_storage_work_to_home.rename(columns={'MSOA': 'MSOA_home'}) #Rename for clarity

#Initialise a pickle for each MSOA, both in the home-to-work direction as in the work-to-home direction.
#Store pickle with a dataframe that has a MSOA home or Work colum that is filled with the treated MSOA.
for MSOA in list(df_MSOA_unique_values['MSOA']):  # ['E02000001','E02000002','E02000003']:
	df_storage_home_to_work['MSOA_home']=MSOA
	df_storage_work_to_home['MSOA_work']=MSOA

	#Set up outputname
	filename='{0}_home_to_work'.format(MSOA)
	#Store to pickle.
	out=foldername_output_pickle + filename
	outfile = open(out,'wb')
	pickle.dump(df_storage_home_to_work,outfile)
	outfile.close()

	#Set up outputname2
	filename2='{0}_work_to_home'.format(MSOA)
	#Store to pickle.
	out2=foldername_output_pickle + filename2
	outfile2 = open(out2,'wb')
	pickle.dump(df_storage_work_to_home, outfile2)
	outfile2.close()
'''

############################
#4.2 Fill up the pickles with information for different modes and metrics
############################
'''
infile = open('/Users/Metti_Hoof/Desktop/Test/Pickle_storage/E02000003_home_to_work','rb')
new_dict1 = pickle.load(infile)
infile.close()

print ('Before filling up:')
print(new_dict1.head())
'''
'''
#Choose which ones you want to work on.
home_to_work=True
work_to_home=True


if home_to_work:
	print('\nWe are filling the pickles for the home to work direction')

	for input_type in input_list:
		for mode in mode_list:
			#Setup timer
			start_time = time.time()

			#Get relevant dataframe.
			df_input=available_inputfiles[input_type][mode]
			
			#Reconstruct the name of the values in the df_input
			value_name='{0}_{1}'.format(input_type,mode)

			#Take a copy of the df_input to work on. 
			df_filtering=df_input[['origin_msoacode','destination_msoacode',value_name]].copy()
			
			#For home to work, we filter on destination_msoa code (the home in quant2)
			# We set destination_msoacode to be the index, this makes the filtering a lot faster
			df_filtering=df_filtering.set_index('destination_msoacode')

			msoa_counter=0
			for MSOA in list(df_MSOA_unique_values['MSOA']):  # ['E02000001','E02000002','E02000003']:
				
				#Open existing pickle. 
				filename='{0}_home_to_work'.format(MSOA)
				file_in=foldername_output_pickle + filename
				infile = open(file_in,'rb')
				df_storage_home_to_work = pickle.load(infile)
				infile.close()
			
				# See whether the MSOA under consideration is in the index of df_filtering 
				if MSOA in df_filtering.index:
					df_filtered=df_filtering.loc[[MSOA]].copy() #.loc[] works on index so in this case on destination_msoacode
					#Note that we use a list inside .loc[] but with only one element. This is because of the following issue:
					#https://stackoverflow.com/questions/20383647/pandas-selecting-by-label-sometimes-return-series-sometimes-returns-dataframe
					df_filtered=df_filtered.reset_index()# So that destination_msoacode becomes a column again. 

					df_tussen=df_storage_home_to_work['MSOA_work'].copy()
					df_tussen=pd.merge(df_tussen, df_filtered[['origin_msoacode',value_name]], how='left',left_on='MSOA_work', right_on='origin_msoacode').copy()
					
					#The full list of work MSOAs (with values and NaN) for one home MSOA is than attached to the storage
					# as a column, the column name is the name of the MSOA we used as the origin.
					df_storage_home_to_work[value_name]=df_tussen[value_name].copy()

				#If there is an MSOA that is not in the origin MSOAs of the input, we create a column filled of NaN
				else:
					#print('Niet in de lijst jongens')
					df_storage_home_to_work[value_name]=np.nan

				#Store to pickle. Set up outputname
				filename='{0}_home_to_work'.format(MSOA)
				#Store to pickle.
				out=foldername_output_pickle + filename
				outfile = open(out,'wb')
				pickle.dump(df_storage_home_to_work,outfile)
				outfile.close()

				# Follow up on counter.
				msoa_counter=msoa_counter+1
				if msoa_counter%100==0:
					print('We are creating the pickle for home to work of MSOA {0}, {1} and {2}'.format(msoa_counter,input_type,mode))
			
			# Print out time
			print ("\n Creating all pickels home to work for {0} and {1} took about".format(input_type,mode), round((time.time()-start_time)/60), "minutes")



if work_to_home:
	print('\nWe are filling the pickles for the work to home direction')

	for input_type in input_list:
		for mode in mode_list:
			#Setup timer
			start_time = time.time()

			#Get relevant dataframe.
			df_input=available_inputfiles[input_type][mode]
			
			#Reconstruct the name of the values in the df_input
			value_name='{0}_{1}'.format(input_type,mode)

			#Take a copy of the df_input to work on. 
			df_filtering=df_input[['origin_msoacode','destination_msoacode',value_name]].copy()
			
			#For work to home, we filter on origin_msoa code (the work in quant2)
			# We set origin_msoacode to be the index, this makes the filtering a lot faster
			df_filtering=df_filtering.set_index('origin_msoacode')

			msoa_counter=0
			for MSOA in list(df_MSOA_unique_values['MSOA']): #['E02000001','E02000002','E02000003']:
				
				#Open existing pickle. 
				filename='{0}_work_to_home'.format(MSOA)
				file_in=foldername_output_pickle + filename
				infile = open(file_in,'rb')
				df_storage_work_to_home = pickle.load(infile)
				infile.close()
			
				# See whether the MSOA under consideration is in the index of df_filtering 
				if MSOA in df_filtering.index:
					df_filtered=df_filtering.loc[[MSOA]].copy() #.loc[] works on index so in this case on destination_msoacode
					#Note that we use a list inside .loc[] but with only one element. This is because of the following issue:
					#https://stackoverflow.com/questions/20383647/pandas-selecting-by-label-sometimes-return-series-sometimes-returns-dataframe
					df_filtered=df_filtered.reset_index()# So that destination_msoacode becomes a column again. 

					df_tussen=df_storage_work_to_home['MSOA_home'].copy()
					df_tussen=pd.merge(df_tussen, df_filtered[['destination_msoacode',value_name]], how='left',left_on='MSOA_home', right_on='destination_msoacode').copy()
					
					#The full list of home MSOAs (with values and NaN) for one work MSOA is than attached to the storage
					# as a column, the column name is the name value.
					df_storage_work_to_home[value_name]=df_tussen[value_name].copy()

				#If there is an MSOA that is not in the  MSOAs of the input, we create a column filled of NaN
				else:
					#print('Niet in de lijst jongens')
					df_storage_work_to_home[value_name]=np.nan

				#Store to pickle. Set up outputname
				filename='{0}_work_to_home'.format(MSOA)
				#Store to pickle.
				out=foldername_output_pickle + filename
				outfile = open(out,'wb')
				pickle.dump(df_storage_work_to_home,outfile)
				outfile.close()

				# Follow up on counter.
				msoa_counter=msoa_counter+1
				if msoa_counter%100==0:
					print('We are creating the pickle for work to home of MSOA {0}, {1} and {2}'.format(msoa_counter,input_type,mode))

			# Print out time
			print ("\n Creating all pickels work to home for {0} and {1} took about".format(input_type,mode), round((time.time()-start_time)/60), "minutes")


print('We are ready, just testing out some stuff.')

infile = open('/Users/Metti_Hoof/Desktop/Heavy_data/Pickle_storage_baseline/E02000003_home_to_work','rb')
new_dict1 = pickle.load(infile)
infile.close()

print ('After filling up home to work:')
print(new_dict1.head())


infile2 = open('/Users/Metti_Hoof/Desktop/Heavy_data/Pickle_storage_baseline/E02000003_work_to_home','rb')
new_dict2 = pickle.load(infile2)
infile2.close()

print ('After filling up work to home:')
print(new_dict2.head())
'''
################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################

'''
home_to_work=True
work_to_home=True


if home_to_work:
	print('\nWe are creating the pickles for the home to work direction')

	for input_type in input_list:
		for mode in mode_list:

			#Get relevant dataframe.
			df_input=available_inputfiles[input_type][mode]
			
			#Reconstruct the name of the values in the df_input
			value_name='{0}_{1}'.format(input_type,mode)

			#Take a copy of the df_input to work on. 
			df_filtering=df_input[['origin_msoacode','destination_msoacode',value_name]].copy()
			
			#For home to work, we filter on destination_msoa code (the home in quant2)
			# We set destination_msoacode to be the index, this makes the filtering a lot faster
			df_filtering=df_filtering.set_index('destination_msoacode')

			msoa_counter=1
			for MSOA in ['E02000001','E02000002','E02000003']: #list(df_MSOA_unique_values['MSOA']): 

				#Setup storage	
				df_storage=df_MSOA_unique_values.copy()
				
				if msoa_counter%100==0:
					print('We are creating the pickle for MSOA {0}, {1} and {2}'.format(msoa_counter,input_type,mode))

				if MSOA in df_filtering.index:
					df_filtered=df_filtering.loc[[MSOA]].copy() #.loc[] works on index so in this case on destination_msoacode
					#Note that we use a list inside .loc[] but with only one element. This is because of the following issue:
					#https://stackoverflow.com/questions/20383647/pandas-selecting-by-label-sometimes-return-series-sometimes-returns-dataframe
					df_filtered=df_filtered.reset_index()# So that destination_msoacode becomes a column again. 

					df_tussen=df_MSOA_unique_values.copy()
					df_tussen=pd.merge(df_tussen, df_filtered[['origin_msoacode',value_name]], how='left',left_on='MSOA', right_on='origin_msoacode').copy()
					
					#The full list of work MSOAs (with values and NaN) for one home MSOA is than attached to the storage
					# as a column, the column name is the name of the MSOA we used as the origin.
					df_storage[value_name]=df_tussen[value_name].copy()

				#If there is an MSOA that is not in the origin MSOAs of the input, we create a column filled of NaN
				else:
					#print('Niet in de lijst jongens')
					df_storage[value_name]=np.nan

				df_storage['MSOA_home']=MSOA
				#Rename for clarity
				df_storage=df_storage.rename(columns={'MSOA': 'MSOA_work'})

				#Store to pickle. Set up outputname
				filename='{0}_home_to_work_{1}_{2}'.format(MSOA,input_type,mode)

				out=foldername_output_pickle + filename
				outfile = open(out,'wb')
				pickle.dump(df_storage,outfile)
				outfile.close()
'''
'''
infile = open(out,'rb')
new_dict = pickle.load(infile)
infile.close()
'''
'''

if work_to_home:
	print('\nWe are creating the pickles for the work to home direction')

	for input_type in input_list:
		for mode in mode_list:

			#Get relevant dataframe.
			df_input=available_inputfiles[input_type][mode]
			
			#Reconstruct the name of the values in the df_input
			value_name='{0}_{1}'.format(input_type,mode)

			#Take a copy of the df_input to work on. 
			df_filtering=df_input[['origin_msoacode','destination_msoacode',value_name]].copy()
			
			#For work to home, we filter on origin_msoacode (the work in quant2)
			# We set origin_msoacode to be the index, this makes the filtering a lot faster
			df_filtering=df_filtering.set_index('origin_msoacode')

			msoa_counter=1
			for MSOA in ['E02000001','E02000002','E02000003']: #list(df_MSOA_unique_values['MSOA']): 

				#Setup storage	
				df_storage=df_MSOA_unique_values.copy()
				
				if msoa_counter%100==0:
					print('We are creating the pickle for MSOA {0}, {1} and {2}'.format(msoa_counter,input_type,mode))

				if MSOA in df_filtering.index:
					df_filtered=df_filtering.loc[[MSOA]].copy() #.loc[] works on index so in this case on destination_msoacode
					#Note that we use a list inside .loc[] but with only one element. This is because of the following issue:
					#https://stackoverflow.com/questions/20383647/pandas-selecting-by-label-sometimes-return-series-sometimes-returns-dataframe
					df_filtered=df_filtered.reset_index()# So that destination_msoacode becomes a column again. 

					df_tussen=df_MSOA_unique_values.copy()
					df_tussen=pd.merge(df_tussen, df_filtered[['destination_msoacode',value_name]], how='left',left_on='MSOA', right_on='destination_msoacode').copy()
					
					#The full list of home MSOAs (with values and NaN) for one work MSOA is than attached to the storage
					# as a column, the column name is the name of the MSOA we used as the origin.
					df_storage[value_name]=df_tussen[value_name].copy()

				#If there is an MSOA that is not in the origin MSOAs of the input, we create a column filled of NaN
				else:
					#print('Niet in de lijst jongens')
					df_storage[value_name]=np.nan

				df_storage['MSOA_work']=MSOA
				#Rename for clarity
				df_storage=df_storage.rename(columns={'MSOA': 'MSOA_home'})

				#Store to pickle. Set up outputname
				filename='{0}_work_to_home_{1}_{2}'.format(MSOA,input_type,mode)

				out=foldername_output_pickle + filename
				outfile = open(out,'wb')
				pickle.dump(df_storage,outfile)
				outfile.close()

'''
'''
print('The end')




infile = open('/Users/Metti_Hoof/Desktop/Test/Pickle_storage/E02000003_home_to_work','rb')
new_dict1 = pickle.load(infile)
infile.close()


infile = open('/Users/Metti_Hoof/Desktop/Test/Pickle_storage/E02000003_work_to_home_Ess_rail','rb')
new_dict2 = pickle.load(infile)
infile.close()

'''

#outputname=foldername_output + 'Pickle_storage/{0}_{1}_{2}'.format(MSOA,input_type,mode)

'''
dogs_dict = { 'Ozzy': 3, 'Filou': 8, 'Luna': 5, 'Skippy': 10, 'Barco': 12, 'Balou': 9, 'Laika': 16 }

filename = foldername_output + 'Pickle_storage/dogs'
outfile = open(filename,'wb')
pickle.dump(dogs_dict,outfile)
outfile.close()

'''



################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################

'''
########################################################
# Creating datasets for developing purposes. 

#Write out subset to csv.
"""
df_Occ_rail.head(10000).to_csv('/Users/Metti_Hoof/Desktop/Test/df_Occ_rail_subset.csv')
"""

#Read in stored subset
print('\nWe are reading in the stored subsets for developing purposes')
df_Occ_rail_subset=pd.read_csv('/Users/Metti_Hoof/Desktop/Test/df_Occ_rail_subset.csv',sep=',', lineterminator='\n') 
df_Occ_rail_subset=df_Occ_rail_subset.drop(columns=['Unnamed: 0'])

print ('\n The first five lines of the df_Occ_rail_subset dataframe look like this:')
print(df_Occ_rail_subset.head())

MSOA_list_of_origins_in_subset=list(df_Occ_rail_subset['origin_msoacode'].unique())

print ('\n The unique origins in the subset are:')
print(MSOA_list_of_origins_in_subset)
########################################################

## Trying to construct a 8436 by 8436 dataframe that can hold the trips, Occ, etc for each MSOA pair. 

df_to_merge=df_MSOA_unique_values
df_storage=df_MSOA_unique_values

#Set origin msoa_code to be the index, this makes the filtering a lot faster
df_Occ_rail_for_filtering=df_Occ_rail_subset[['origin_msoacode','destination_msoacode','Occ_rail']].copy()
df_Occ_rail_for_filtering=df_Occ_rail_for_filtering.set_index('origin_msoacode')

msoa_counter=0

for MSOA in MSOA_list_of_origins_in_subset:
	if colcounter%1000==0:
		print('The code is at column number: ' + str(msoa_counter) + ' and there are ' + str(len(MSOA_list_of_origins_in_subset)) + ' columns to process')

	print(MSOA)

	#Select only those rows where the index (origin_msoacode) == a value
	df_filtered=df_Occ_rail_for_filtering.loc[MSOA]
	df_filtered=df_filtered.reset_index()

	print("Filtered")
	print(df_filtered.shape)
	print(df_filtered.head())

	#
	df_tussen=pd.merge(df_to_merge, df_filtered[['destination_msoacode','Occ_rail']], how='left',left_on='MSOA', right_on='destination_msoacode')
	print("Tussen")
	print(df_tussen.shape)
	print(df_tussen.head())

	df_storage[MSOA]=df_tussen['Occ_rail']
	print("Storage")
	print(df_storage.head())


'''



'''
# The Occ files are matrices with headers and columns available. 
# Remember that the initial Occ data is in 1/minutes, so we do 1 / Occ to get to minutes. 
# Some of the Occ values are '∞' because it is 1/time and if time is 0
# They are replaced by a value of choice which is hardcoded in the beginning of the file
# inside the hardcoded_infinity_replace_value variable. 


while car:
	print("Reading in the Occ file for car: " +'\n' + str(inputfile_Occ_car))
	df_Occ_car_in=pd.read_csv(inputfile_Occ_car,sep=',', lineterminator='\n', header=0) 
	df_Occ_car_in.set_index('MSOA',inplace=True)

	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_Occ_car_in=df_Occ_car_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_Occ_bus to be float entirely. 
	df_Occ_car_in= df_Occ_car_in.astype(float)

	#Set the df_Occ to be in minutes. Remember that the initial Occ data is in 1/minutes
	df_Occ_car=1/df_Occ_car_in

	print ('\n The number of rows and columns in the Occ_car dataframe are:')
	print(df_Occ_car.shape)

	print ('\n The first five lines of the Occ_car dataframe look like this:')
	print(df_Occ_car.head())

	break

	# When importing we get a warning that columns 4588 and 6640 have mixed dtypes, 
	# so we investigate and find that there are two float values
	# which are interpreted as string, don't know why. 
	# this issue should't play anymore once we have converted the df to float.
	# but just to be sure I documented it here. 

	#a=df_Occ_car.iloc[4588,:] 
	#for i in a: 
	#	if type(i)==str: 
	#		print(i)
	#
	#b=df_Occ_car.iloc[6640,:] 
	#for i in b: 
	#	if type(i)==str: 
	#		print (i)

while bus:
	print("Reading in the Occ file for bus: " +'\n' + str(inputfile_Occ_bus))
	df_Occ_bus_in=pd.read_csv(inputfile_Occ_bus,sep=',',header=0,index_col='MSOA')

	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_Occ_bus_in=df_Occ_bus_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_Occ_bus to be float entirely. 
	df_Occ_bus_in = df_Occ_bus_in.astype(float)

	#Set the df_Occ to be in minutes. Remember that the initial Occ data is in 1/minutes
	df_Occ_bus=1/df_Occ_bus_in

	print ('\n The number of rows and columns in the Occ_bus dataframe are:')
	print(df_Occ_bus.shape)

	print ('\n The first five lines of the Occ_bus dataframe look like this:')
	print(df_Occ_bus.head())

	break

while rail:
	print("Reading in the Occ file for rail: " +'\n' + str(inputfile_Occ_rail))
	df_Occ_rail_in=pd.read_csv(inputfile_Occ_rail,sep=',', lineterminator='\n', header=0) 
	df_Occ_rail_in.set_index('MSOA',inplace=True) 

	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_Occ_rail_in=df_Occ_rail_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_Occ_bus to be float entirely. 
	df_Occ_rail_in = df_Occ_rail_in.astype(float)

	#Set the df_Occ to be in minutes. Remember that the initial Occ data is in 1/minutes
	df_Occ_rail=1/df_Occ_rail_in

	print ('\n The number of rows and columns in the Occ_rail dataframe are:')
	print(df_Occ_rail.shape)

	print ('\n The first five lines of the Occ_rail dataframe look like this:')
	print(df_Occ_rail.head())

	break



'''
######################
#2.1.3 Read in the Ess files 
######################
'''
while car:
	print("Reading in the Ess file for car: " + '\n' + str(inputfile_Ess_car))
	df_Ess_car=pd.read_csv(inputfile_Ess_car, sep=',', lineterminator='\n') 

	df_Ess_car=df_Ess_car.rename(columns={'data\r': 'Ess_car'})

	print ('\n The number of rows and columns in the Ess_car dataframe are:')
	print(df_Ess_car.shape)

	print ('\n The first five lines of the Ess_car dataframe look like this:')
	print(df_Ess_car.head())

	break

while bus:
	print("Reading in the Ess file for bus: " + '\n' + str(inputfile_Ess_bus))
	df_Ess_bus=pd.read_csv(inputfile_Ess_bus, sep=',', lineterminator='\n')

	df_Ess_bus=df_Ess_bus.rename(columns={'data\r': 'Ess_bus'}) 

	print ('\n The number of rows and columns in the Ess_bus dataframe are:')
	print(df_Ess_bus.shape)

	print ('\n The first five lines of the Ess_bus dataframe look like this:')
	print(df_Ess_bus.head())

	break

while rail:
	print("Reading in the Ess file for rail: " + '\n' + str(inputfile_Ess_rail))
	
	df_Ess_rail=df_Ess_rail=pd.read_csv(inputfile_Ess_rail, sep=',', lineterminator='\n') 

	df_Ess_rail=df_Ess_rail.rename(columns={'data\r': 'Ess_rail'})
	
	print ('\n The number of rows and columns in the Ess_rail dataframe are:')
	print(df_Ess_rail.shape)

	print ('\n The first five lines of the Ess_rail dataframe look like this:')
	print(df_Ess_rail.head())

	break


######################
#2.1.3 Read in the NoMode files 
######################

while car:
	print("Reading in the NoMode file for car: " + '\n' + str(inputfile_NoMode_car))
	df_NoMode_car=pd.read_csv(inputfile_NoMode_car, sep=',', lineterminator='\n') 

	df_NoMode_car=df_NoMode_car.rename(columns={'data\r': 'NoMode_car'})

	print ('\n The number of rows and columns in the NoMode_car dataframe are:')
	print(df_NoMode_car.shape)

	print ('\n The first five lines of the NoMode_car dataframe look like this:')
	print(df_NoMode_car.head())

	break

while bus:
	print("Reading in the NoMode file for bus: " + '\n' + str(inputfile_NoMode_bus))
	df_NoMode_bus=pd.read_csv(inputfile_NoMode_bus, sep=',', lineterminator='\n')

	df_NoMode_bus=df_NoMode_bus.rename(columns={'data\r': 'NoMode_bus'}) 

	print ('\n The number of rows and columns in the NoMode_bus dataframe are:')
	print(df_NoMode_bus.shape)

	print ('\n The first five lines of the NoMode_bus dataframe look like this:')
	print(df_NoMode_bus.head())

	break

while rail:
	print("Reading in the NoMode file for rail: " + '\n' + str(inputfile_NoMode_rail))
	
	df_NoMode_rail=pd.read_csv(inputfile_NoMode_rail, sep=',', lineterminator='\n') 

	df_NoMode_rail=df_NoMode_rail.rename(columns={'data\r': 'NoMode_rail'})
	
	print ('\n The number of rows and columns in the NoMode_rail dataframe are:')
	print(df_NoMode_rail.shape)

	print ('\n The first five lines of the NoMode_rail dataframe look like this:')
	print(df_NoMode_rail.head())

	break

'''

########################################################
#3. Create a minutes spent on mode matrix
########################################################

############################
#3.1 Create a minutes spent on mode matrix
############################
'''
# We create a table which tells us the minutes spent for each trip, which = number of obs trips * the shortest route distance (in minutes)

if time_spent: # Only create time_spent if the user is interested in using this.
	while car:
		#We round by minutes as in the overall scheme this will not matter. 
		df_time_spent_car=np.round(df_Ess_car*df_Occ_car,decimals=0)
		#We round by minutes as in the overall scheme this will not matter.
		print ('\n The first five lines of the time_spent_car dataframe look like this:')
		print(df_time_spent_car.head())

		break

	while bus:
		df_time_spent_bus=np.round(df_Ess_bus*df_Occ_bus,decimals=0) 
		#We round by minutes as in the overall scheme this will not matter.
		print ('\n The first five lines of the time_spent_bus dataframe look like this:')
		print(df_time_spent_bus.head())

		break

	while rail:
		df_time_spent_rail=np.round(df_Ess_rail*df_Occ_rail,decimals=0)
		print ('\n The first five lines of the time_spent_rail dataframe look like this:')
		print(df_time_spent_rail.head()) 
		#We round by minutes as in the overall scheme this will not matter.
		break

'''