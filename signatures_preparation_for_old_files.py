
##############################################################################################
# -*- coding: utf-8 -*-
# Script to prepare data for the signatures creation and classification (signatures.py)
# In this script, we will create features from Dij and Tobj data from Quant.
# Written by Maarten Vanhoof, december 2019
# Python 3
#
# Source files were given to me by Roberto Murcio


#Oberserved trips between MSOAS per mode used in Quant. These tables are input in Quant.
#Values in these files are individuals commuting between different msoas. 

#Calculated shortest routes (Dij) by Quant for OD between MSOAS. They serve as input for Quant
#Values in these files are 1/time(minutes)
##############################################################################################

#Put to True if you want to do the preparation for the different modes. 
car=True
bus=True
rail=True

#Put to True if you want to do the preparation for the different directions. 
home_to_work=True
work_to_home=False

#Put to True if you want to do the preparation for the different metrics. 
trips=True
shortest_route=True
time_spent=True

print("The script is starting")

########################################################
#-1. Hard-coded elements
########################################################

####################### Personal hard-coding #####################
# Some of the dij values are '∞' because it is 1/time and if time is 0
# C sharp will add an infinity sign in the data. We convert this data to
#  be an arbitrary value that'
hardcoded_infinity_replace_value='NaN'
####################### Personal hard-coding #####################


####################### Personal hard-coding #####################
# For the aggregation per MSOA we filter out MSOA to MSOA links that have 
# a limited contribution in terms of trips, minutes or trips per minute. 
# we calculate in msoa to msoa links only if they contribute a larger share
# to all values originating from this msoa than the proposes percentage filter. 
hardcoded_percentage_filter=0.01
####################### Personal hard-coding #####################


########################################################
#0. Setup environment
########################################################

############################
#0.1 Import dependencies
############################
import pandas as pd #For data handling
import numpy as np #For matrix handling
import math #For math handling
import geopandas as gpd #For geographic work
import matplotlib #for plotting
#matplotlib.use("TkAgg") #matplotlibs needs to use this backend to not crash on the new mac. 
import matplotlib.pylab as plt #For interactive plotting

############################
#0.2 Setup in and output paths
############################

#Where inputdata lives and output will be put
foldername_input ='/Users/Metti_Hoof/Desktop/Quant Developing/data/' 
foldername_output ='/Users/Metti_Hoof/Desktop/' 


########################################################
#1. Read in inputfiles
########################################################

############################
#1.1 Set names of inputfiles
############################

#Census 2011 data with OD between MSOAs by different modes
inputfile_OD= foldername_input + 'Quant_forMaarten/wu03uk_v3.csv'  

#Oberserved trips between MSOAS per mode used in Quant. These tables are input in Quant.
#Values in these files are individuals
inputfile_Tobs_car= foldername_input + 'Quant_forMaarten/EWS_TObs_1.csv' 
inputfile_Tobs_bus= foldername_input + 'Quant_forMaarten/EWS_TObs_2.csv' 
inputfile_Tobs_rail= foldername_input + 'Quant_forMaarten/EWS_TObs_3.csv' 
inputfile_Tobs_total= foldername_input + 'Quant_forMaarten/EWS_TObs.csv' 

#Calculated shortest routes by Quant for OD between MSOAS. They serve as input for Quant
#Values in these files are 1/time(minutes)

#files that will be used to copy structure from.
inputfile_struture_storage= foldername_input + 'Quant_forMaarten/old/names_gb.csv' 
inputfile_names_with_scotland= foldername_input + 'Quant_forMaarten/names.csv' 


#old files
inputfile_dij_car= foldername_input + 'Quant_forMaarten/old/dis_roads_minEW.csv' 
inputfile_dij_bus= foldername_input + 'Quant_forMaarten/old/dis_bus_minEW.csv' 
inputfile_dij_rail= foldername_input + 'Quant_forMaarten/old/dis_gbrail_minEW.csv'


#Shapefile with MSOA locations
inputfile_shapefile_MSOA= foldername_input + 'shapefiles/EPSG7405_MSOA_2011/EPSG7405_MSOA_2011.shp'



########################################################
#2. Read in and pre-process data
########################################################

# Our aim is to aggregate the information on distancances and observed trips per MSOA so 
# that they can be used as features for a classification task. 

############################
#2.1 Read in data
############################

######################
#2.1.2 Copy the structure of names files to be used later. 
######################

print("Reading in the names file to copy its structure")
df_structure_in=pd.read_csv(inputfile_struture_storage,sep=',', lineterminator='\r', header=0) 
df_structure_in.set_index('MSOA11CD',inplace=True)

# We create an empty dataframe that has the same structure as the dij new dataframe so it can be transferred to the
#	dij old files and the Tobs files  since those don't have a structure but Roberto told me their structure was the same. 

df_structure_storage=pd.DataFrame().reindex_like(df_structure_in)


print("Reading in the names file including Scotland")
df_names_with_scotland=pd.read_csv(inputfile_names_with_scotland,sep=',', lineterminator='\n', header=0)
# Filter out msoas that are in scotlnad (their names start with S0)
df_names_without_scotland=df_names_with_scotland[~df_names_with_scotland.MSOA11CD.str.contains('S0',case=True)]
# Set MSOA11CD to be the indices im both.
df_names_with_scotland.set_index('MSOA11CD',inplace=True)
df_names_without_scotland.set_index('MSOA11CD',inplace=True)

######################
#2.1.1 Read in the Dij files
######################

# The dij files are matrices with headers and columns available. 
# Remember that the initial dij data is in 1/minutes, so we do 1 / dij to get to minutes. 
# Some of the dij values are '∞' because it is 1/time and if time is 0
# They are replaced by a value of choice which is hardcoded in the beginning of the file
# inside the hardcoded_infinity_replace_value variable. 


while car:
	print("Reading in the dij file for car: " +'\n' + str(inputfile_dij_car))
	df_dij_car_in=pd.read_csv(inputfile_dij_car,sep=',', lineterminator='\n',header=None) 

	#Take on structure from structure_storage
	df_dij_car_in.columns = list(df_structure_storage.index)
	df_dij_car_in.set_index(df_structure_storage.index,inplace=True)

	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_dij_car_in=df_dij_car_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_dij_car to be float entirely. 
	df_dij_car= df_dij_car_in.astype(float)

	print ('\n The number of rows and columns in the dij_car dataframe are:')
	print(df_dij_car.shape)

	print ('\n The first five lines of the dij_car dataframe look like this:')
	print(df_dij_car.head())

	break

	# When importing we get a warning that columns 4588 and 6640 have mixed dytpes, 
	# so we investigate and find that there are two float values
	# which are interpreted as string, don't know why. 
	# this issue should't play anymore once we have converted the df to float.
	# but just to be sure I documented it here. 

	#a=df_dij_car.iloc[4588,:] 
	#for i in a: 
	#	if type(i)==str: 
	#		print(i)
	#
	#b=df_dij_car.iloc[6640,:] 
	#for i in b: 
	#	if type(i)==str: 
	#		print (i)

while bus:
	print("Reading in the dij file for bus: " +'\n' + str(inputfile_dij_bus))
	df_dij_bus_in=pd.read_csv(inputfile_dij_bus,sep=',', lineterminator='\n',header=None)

	#Take on structure from structure_storage
	df_dij_bus_in.columns = list(df_structure_storage.index)
	df_dij_bus_in.set_index(df_structure_storage.index,inplace=True)


	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_dij_bus_in=df_dij_bus_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_dij_bus to be float entirely. 
	df_dij_bus= df_dij_bus_in.astype(float)

	print ('\n The number of rows and columns in the dij_bus dataframe are:')
	print(df_dij_bus.shape)

	print ('\n The first five lines of the dij_bus dataframe look like this:')
	print(df_dij_bus.head())

	break

while rail:
	print("Reading in the dij file for rail: " +'\n' + str(inputfile_dij_rail))
	df_dij_rail_in=pd.read_csv(inputfile_dij_rail,sep=',', lineterminator='\n', header=None) 

	#Take on structure from structure_storage
	df_dij_rail_in.columns = list(df_structure_storage.index)
	df_dij_rail_in.set_index(df_structure_storage.index,inplace=True)


	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_dij_rail_in=df_dij_rail_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_dij_bus to be float entirely. 
	df_dij_rail = df_dij_rail_in.astype(float)


	print ('\n The number of rows and columns in the dij_rail dataframe are:')
	print(df_dij_rail.shape)

	print ('\n The first five lines of the dij_rail dataframe look like this:')
	print(df_dij_rail.head())

	break



######################
#2.1.3 Read in the Tobs files 
######################
# The Tobs files don't have the headers and columns but those are given in names.csv 
# so we first have to assign the MSOA11CD identifiers.
# Then there are 8436 msoas in the Tobs, to get to 7201 we need to filter out the Scottish ones.


while car:
	print("Reading in the Tobs file for car: " + '\n' + str(inputfile_Tobs_car))
	df_Tobs_car_in=pd.read_csv(inputfile_Tobs_car, header=None, sep=',', lineterminator='\n') 

	df_Tobs_car_in.columns=list(df_names_with_scotland.index)
	df_Tobs_car_in.set_index(df_names_with_scotland.index,inplace=True)

	df_Tobs_car_tussen=df_Tobs_car_in.filter(items=list(df_names_without_scotland.index),axis=0) #Filter index
	df_Tobs_car=df_Tobs_car_tussen.filter(items=list(df_names_without_scotland.index),axis=1) #Filter columns

	print ('\n The number of rows and columns in the Tobs_car dataframe are:')
	print(df_Tobs_car.shape)

	print ('\n The first five lines of the Tobs_car dataframe look like this:')
	print(df_Tobs_car.head())

	break

while bus:
	print("Reading in the Tobs file for bus: " + '\n' + str(inputfile_Tobs_bus))
	df_Tobs_bus_in=pd.read_csv(inputfile_Tobs_bus, header=None, sep=',', lineterminator='\n') 

	df_Tobs_bus_in.columns=list(df_names_with_scotland.index)
	df_Tobs_bus_in.set_index(df_names_with_scotland.index,inplace=True)

	df_Tobs_bus_tussen=df_Tobs_bus_in.filter(items=list(df_names_without_scotland.index),axis=0) #Filter index
	df_Tobs_bus=df_Tobs_bus_tussen.filter(items=list(df_names_without_scotland.index),axis=1) #Filter columns


	print ('\n The number of rows and columns in the Tobs_bus dataframe are:')
	print(df_Tobs_bus.shape)

	print ('\n The first five lines of the Tobs_bus dataframe look like this:')
	print(df_Tobs_bus.head())

	break

while rail:
	print("Reading in the Tobs file for rail: " + '\n' + str(inputfile_Tobs_rail))
	df_Tobs_rail_in=pd.read_csv(inputfile_Tobs_rail, header=None, sep=',', lineterminator='\n') 

	df_Tobs_rail_in.columns=list(df_names_with_scotland.index)
	df_Tobs_rail_in.set_index(df_names_with_scotland.index,inplace=True)

	df_Tobs_rail_tussen=df_Tobs_rail_in.filter(items=list(df_names_without_scotland.index),axis=0) #Filter index
	df_Tobs_rail=df_Tobs_rail_tussen.filter(items=list(df_names_without_scotland.index),axis=1) #Filter columns

	print ('\n The number of rows and columns in the Tobs_rail dataframe are:')
	print(df_Tobs_rail.shape)

	print ('\n The first five lines of the Tobs_rail dataframe look like this:')
	print(df_Tobs_rail.head())

	break



########################################################
#3. Create a minutes spent on mode matrix
########################################################

############################
#3.2 Create a minutes spent on mode matrix
############################

# We create a tabel which tells us the minutes spend for each trip, which = number of obs trips * the shortest route distance (in minutes)

if time_spent: # Only create time_spent if the user is interested in using this.
	while car:
		#We round by minutes as in the overall scheme this will not matter. 
		df_time_spent_car=np.round(df_Tobs_car*df_dij_car,decimals=0)
		#We round by minutes as in the overall scheme this will not matter.
		print ('\n The first five lines of the time_spent_car dataframe look like this:')
		print(df_time_spent_car.head())

		break

	while bus:
		df_time_spent_bus=np.round(df_Tobs_bus*df_dij_bus,decimals=0) 
		#We round by minutes as in the overall scheme this will not matter.
		print ('\n The first five lines of the time_spent_bus dataframe look like this:')
		print(df_time_spent_bus.head())

		break

	while rail:
		df_time_spent_rail=np.round(df_Tobs_rail*df_dij_rail,decimals=0)
		print ('\n The first five lines of the time_spent_rail dataframe look like this:')
		print(df_time_spent_rail.head()) 
		#We round by minutes as in the overall scheme this will not matter.
		break



########################################################
#4. Summarize data per MSOA: aggregate per mode, 
	#for different directions, and with a filter for minimum share
########################################################

############################
#4.1 Setup 
############################
modes=[] #select one or multiple modes. ['car','bus','rail']
if car:
	modes.append('car')
if bus:
	modes.append('bus')
if rail:
	modes.append('rail')

#Directions are different in the sense that we will have to aggragate column of row wise. 
directions=[]
if home_to_work:
	directions.append('home_to_work') #select one or multiple directions.['home_to_work','work_to_home']
if work_to_home:
	directions.append('work_to_home')

metrices=[] #select one or multiple inputmatrices to aggregate['trips','shortest_route','time_spent']
if trips:
	metrices.append('trips')
if shortest_route:
	metrices.append('shortest_route')
if time_spent:
	metrices.append('time_spent')


############################
#4.2 Aggregatiom
############################

######################
#4.2.1 Set up a filter based on the amount of trips and a hardcoded minimum percentage. 
######################

######### NOTE THAT THIS FILTER ONLY WORKS FOR THE HOME_TO_WORK DIRECTION ########

if car:
	print('\nWe are setting up the filtering based on trip percentage > {0} for the car'.format(hardcoded_percentage_filter)) 
	dict_filter_car={}
	dict_filter_car_retained_percentage={}

	colcounter=0
	for col in df_Tobs_car.columns:
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df_Tobs_car.columns)) + ' columns to process')
		colcounter=colcounter+1

		df_filter_car=df_Tobs_car[[col]].copy()
		df_filter_car['percentage']=df_filter_car[col]/df_filter_car[col].sum()
		#Apply HARDCODED filter.
		df_filter_car_selection=df_filter_car.query("percentage > {0}".format(hardcoded_percentage_filter))
		
		#Create a filter_car dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter_car[col]=df_filter_car_selection.index.to_list() 
		#Create a filter_car dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter_car_retained_percentage[col]=np.round(df_filter_car_selection['percentage'].sum()*100,decimals=1)

if bus:
	print('\nWe are setting up the filtering based on trip percentage > {0} for the bus'.format(hardcoded_percentage_filter)) 
	dict_filter_bus={}
	dict_filter_bus_retained_percentage={}

	colcounter=0
	for col in df_Tobs_bus.columns:
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df_Tobs_bus.columns)) + ' columns to process')
		colcounter=colcounter+1

		df_filter_bus=df_Tobs_bus[[col]].copy()
		df_filter_bus['percentage']=df_filter_bus[col]/df_filter_bus[col].sum()
		#Apply HARDCODED filter.
		df_filter_bus_selection=df_filter_bus.query("percentage > {0}".format(hardcoded_percentage_filter))
		
		#Create a filter_bus dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter_bus[col]=df_filter_bus_selection.index.to_list() 
		#Create a filter_bus dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter_bus_retained_percentage[col]=np.round(df_filter_bus_selection['percentage'].sum()*100,decimals=1)


if rail:
	print('\nWe are setting up the filtering based on trip percentage > {0} for the rail'.format(hardcoded_percentage_filter)) 
	dict_filter_rail={}
	dict_filter_rail_retained_percentage={}
	
	colcounter=0
	for col in df_Tobs_rail.columns:
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df_Tobs_rail.columns)) + ' columns to process')
		colcounter=colcounter+1

		df_filter_rail=df_Tobs_rail[[col]].copy()
		df_filter_rail['percentage']=df_filter_rail[col]/df_filter_rail[col].sum()
		#Apply HARDCODED filter.
		df_filter_rail_selection=df_filter_rail.query("percentage > {0}".format(hardcoded_percentage_filter))
		
		#Create a filter_rail dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter_rail[col]=df_filter_rail_selection.index.to_list() 
		#Create a filter_rail dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter_rail_retained_percentage[col]=np.round(df_filter_rail_selection['percentage'].sum()*100,decimals=1)


######################
#4.2.2 Set up structure of output, add information on retained percentage of filters to it already.
######################

# we copy the structure of the storage for one  MSOA column ('MSOA11NM') because this is necessary to copy, we drop this column later
# we will delete this one column later on in the code. 
df_output=df_structure_storage['MSOA11NM'].copy()

for mode in modes:
	retained_percentage_output_name='retained_percentage_of_trips_by_{0}_with_filter_{1}'.format(mode,hardcoded_percentage_filter)
	if mode=='car':
		df_to_store = pd.DataFrame(list(dict_filter_car_retained_percentage.items()), columns = ['MSOA',retained_percentage_output_name])
	elif mode=='bus':
		df_to_store = pd.DataFrame(list(dict_filter_bus_retained_percentage.items()), columns = ['MSOA',retained_percentage_output_name])
	elif mode=='rail':
		df_to_store = pd.DataFrame(list(dict_filter_rail_retained_percentage.items()), columns = ['MSOA',retained_percentage_output_name])
	
	df_output=df_to_store.join(df_output, how='right', on='MSOA') #uses index of structure storage.
	df_output=df_output.set_index('MSOA')

#Drop the 'MSOA11NM' because we do not need it anymore
df_output=df_output.drop(columns=['MSOA11NM']) 


######################
#4.2.3 Run aggregation for different modes, directions and aggregation functions. Apply filter.
######################

for mode in modes:
	print ('\nWe are now treating mode: {0}'.format(mode))

	if mode=='car':
		df_time_spent=df_time_spent_car
		df_Tobs=df_Tobs_car
		df_dij=df_dij_car
		dict_filter=dict_filter_car
	elif mode=='bus':
		df_time_spent=df_time_spent_bus
		df_Tobs=df_Tobs_bus
		df_dij=df_dij_bus
		dict_filter=dict_filter_bus
	elif mode=='rail':
		df_time_spent=df_time_spent_rail
		df_Tobs=df_Tobs_rail
		df_dij=df_dij_rail
		dict_filter=dict_filter_rail

	dict_inputmatrix={}

	for direction in directions:

		if direction =='home_to_work':
			print('We are aggregating in the {0} direction.'.format(direction))

			for metric in metrices:
				print('We are aggregating the {0} metric.'.format(metric))

				if metric=='trips':
					work_matrix=df_Tobs
				elif metric=='shortest_route':
					work_matrix=df_dij				
				elif metric=='time_spent':
					work_matrix=df_time_spent

				#Initiate storage containers
				storage_MSOA_names=[]
				storage_sum=[]
				storage_avg=[]
				storage_max=[]
				data_to_store={}
				colcounter=0

				for col in work_matrix.columns: #so for each MSOA
					if colcounter%1000==0:
						print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(work_matrix.columns)) + ' columns to process')
					colcounter=colcounter+1

					df_tussen=work_matrix[col].copy()#creates an intermediare series with one column,namely col
					df_tussen_filtered=df_tussen[df_tussen.index.isin(dict_filter[col])]#select for the given col only the rows that passed the filter

					#Store MSOA name and aggregated values
					storage_MSOA_names.append(col) #Store MSOA name
					storage_sum.append(df_tussen_filtered.sum()) #Store sum of the values for MSOA to MSOA connections that have a larger share than hardcoded pergentage filter
					storage_avg.append(df_tussen_filtered.mean()) #Store the average of values MSOA to MSOA connections that have a larger share than hardcoded pergentage filter
					storage_max.append(df_tussen_filtered.max()) #Store the average of values MSOA to MSOA connections that have a larger share than hardcoded pergentage filter

				#Gather results in dataframe. 
				#Define a name for the headers 
				sum_output_name='sum_{0}_{1}_{2}_{3}'.format(mode,metric,direction,hardcoded_percentage_filter)
				avg_output_name='avg_{0}_{1}_{2}_{3}'.format(mode,metric,direction,hardcoded_percentage_filter)
				max_output_name='max_{0}_{1}_{2}_{3}'.format(mode,metric,direction,hardcoded_percentage_filter)
				
				#Get data together in a dict, that is easier to create a dataframe from.
				data_to_store = {'MSOA': storage_MSOA_names,
								sum_output_name: storage_sum,
								avg_output_name: storage_avg,
								max_output_name: storage_max
								}
				#Get data in a dataframe.
				df_to_store = pd.DataFrame(data_to_store, columns = ['MSOA', sum_output_name, avg_output_name, max_output_name])

				#Join dataframe with df_output so it can be saved in there. 
				#Join on index of df_output (MSOA names) and MSOA so that we are sure the connection is done well.
				df_output=df_to_store.join(df_output, how='right', on='MSOA')
				df_output=df_output.set_index('MSOA')

		elif direction=='work_to_home':
			print('We are aggregating in the {0} direction.'.format(direction))
			#We have not yet coded this direction out. As the code and the filter would need to be different. 
			print('\n\n\n We have not yet coded this direction out. As the code and the filter would need to be different.\n\n\n') 
			   
print (df_output.head())


########################################################
#5. Write out df_output 
########################################################
#Define name
file_outputname= "df_output_{0}_old_files.csv".format(str(hardcoded_percentage_filter))
file_output=foldername_output + file_outputname

#Write out to csv.
df_output.to_csv(file_output)

print('We finished printing out.')

############################################################################################
######################################               #######################################
####################################  Developing zone ######################################
#######################################             ########################################
############################################################################################

'''
test=df_Tobs_car.iloc[0:30, 0:30]
test2=df_time_spent_car.iloc[0:30, 0:30]

filter_dict={}
for col in test:
	df_tussen=test[[col]].copy()
	df_tussen['percentage']=df_tussen[col]/df_tussen[col].sum()

	df_selectie=df_tussen.query("percentage > {0}".format(hardcoded_percentage_filter))[col]
	filter_dict[col]=df_selectie.index.to_list() 


for col in test2:
	df_tussen2=test2[col].copy()
	df_tussen3=df_tussen2[df_tussen2.index.isin(filter_dict[col])]

'''



'''
df_tussen=work_matrix[[col]].copy() #creates an intermediare dataframe with one column being col
df_tussen['percentage']=df_tussen[col]/df_tussen[col].sum() #creates an extra column called percentage in the df_tussen dataframe

#Get the sum of the values for MSOA to MSOA connections that have a larger share than hardcoded pergentage filter
aggregated_value=df_tussen.query("percentage > {0}".format(hardcoded_percentage_filter))[col].sum()

#Store MSOA name and aggregated value
storage_colnames.append(col)
storage_aggregated_values.append(aggregated_value)
'''

#subset=df_time_spent_car.iloc[0:30, 0:30]

'''
while car:
	adsf

	break

while bus:
	adfa

	break

while rail:
	afdfd

	break
'''

############################
#1.2. Read in data and aggregate per MSOA
############################

######################
#1.2.1 OD data
######################
'''
#Read in csv in pandas
df_OD=pd.read_csv(inputfile_OD,sep=',', lineterminator='\n') 
print("Reading in the file: " + str(inputfile_OD))

#Print properties of the OD dataframe
print ('\n The number of rows and columns in the OD dataframe are:')
print(df_OD.shape)

#Print first 5 lines of the OD dataframe
print ('\n The first five lines of the OD dataframe look like this:')
print(df_OD.head())
'''

######################
#1.2.1 Tobs - Obersverved trips 
######################
'''
#Read in csv in pandas
print("Reading in the files: " + 
		'\n' str(inputfile_Tobs_car) +
		'\n' str(inputfile_Tobs_bus) +
		'\n' str(inputfile_Tobs_rail)+ 
		'\n' str(inputfile_Tobs_total))

df_Tobs_car=pd.read_csv(inputfile_Tobs_car,sep=',', lineterminator='\n') 
df_Tobs_bus=pd.read_csv(inputfile_Tobs_bus,sep=',', lineterminator='\n') 
df_Tobs_rail=pd.read_csv(inputfile_Tobs_rail,sep=',', lineterminator='\n') 
df_Tobs_total=pd.read_csv(inputfile_Tobs_total,sep=',', lineterminator='\n') 

#Print properties of the Tobs dataframe
print ('\n The number of rows and columns in the Tobs dataframe are:')
print(df_Tobs_car.shape)
print(df_Tobs_bus.shape)
print(df_Tobs_rail.shape)
print(df_Tobs_total.shape)

#Print first 5 lines of the Tobs dataframe
print ('\n The first five lines of the df_Tobs dataframe look like this:')
print(df_Tobs_car.head())
print(df_Tobs_bus.head())
print(df_Tobs_rail.head())
print(df_Tobs_total.head())
'''
