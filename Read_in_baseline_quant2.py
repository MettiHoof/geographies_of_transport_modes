##############################################################################################
# -*- coding: utf-8 -*-
# Script to read in the baseline information on distances from Quant 2
# Written by Maarten Vanhoof, in MARCH 2020.
# Python 3
#
# Source files were given to me by Richard Milton
# Source files are created within Quant 2 and contain:
#
#Travel times between zones in minutes
#dis1.zip: road
#dis2.zip: bus
#dis3.zip: rail
#
#
#Observed flows of commuters between zones in numbers of people. 
#These have been thresholded so that any trips less than 1 person have been omitted to save space.  
#Tobs1.csv: road
#Tobs.csv: bus
#Tobs3.csv: rail
#
#
#Predicted flows for the baseline scenario (ran purely on inputdata_: flows of commuters between zones in numbers of people. 
#These have been thresholded so that any trips less than 1 person have been omitted to save space.  
#TPred1.csv: road
#TPred2.csv: bus
#TPred3.csv: rail
#
#
#Output of the script is: 
# For each metric and mode a dataframe containing a 8436 by 8436 dataframe with values for all MSOA pairs (NaNs if not there)
#  e.g.: 
# For each MSOA a home-to-work and work-to-home pickle storing a dataframe with all metrics for all modes for all MSOAs (in Heavy_data_pickle_storage)
#
#
##############################################################################################

########################################################
#-1. User Decisions.
########################################################

#Put to True if you want to do the preparation for the different modes. 
car=False
bus=False
rail=True

#Put to True if you want to do the preparation for the different inputs. 
dij=True
tobs=False
tpred=False

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
foldername_input ='/Users/Metti_Hoof/Desktop/Heavy_data/Quant2_Scenariorunner/' 
foldername_output ='/Users/Metti_Hoof/Desktop/Heavy_data/OD_matrix_storage_baseline' 
foldername_output_pickle ='/Users/Metti_Hoof/Desktop/Heavy_data/Pickle_storage_baseline/' 
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
while dij:
	input_list.append('Dij')
	break
while tobs:
	input_list.append('Tobs')
	break
while tpred:
	input_list.append('Tpred')
	break

#Set up a dict containing all the inputfiles
available_inputfiles={}
available_inputfiles['Dij']={}
available_inputfiles['Tobs']={}
available_inputfiles['Tpred']={}


########################################################
#1. Read in inputfiles
########################################################

############################
#1.1 Set names of inputfiles
############################

# Distances between MSOA-zones as calculated by shortest routes in Quant
# Structure: MSOA_i - MSOA_j distance_of_shortest_route
# Distance values are in minutes
inputfile_Dij_car= foldername_input + 'baseline/dis1.csv' 
inputfile_Dij_bus= foldername_input + 'baseline/dis2.csv' 
inputfile_Dij_rail= foldername_input + 'baseline/dis3.csv'


# Observed trips between MSOAS per mode. Data are derived from census data and treated within Quant 2.
# Structure: MSOA_i - MSOA_j number_of_trips
# Number of trips are in individuals. 
# Only pairs with 1 person or more are taken into these files. 

inputfile_Tobs_car= foldername_input + 'baseline/Tobs1.csv' 
inputfile_Tobs_bus= foldername_input + 'baseline/Tobs2.csv'
inputfile_Tobs_rail= foldername_input + 'baseline/Tobs3.csv' 


# Predicted trips between MSOAS per mode. Data are predicted by the baseline scenario that was ran in Quant2
# Structure: MSOA_i - MSOA_j number_of_trips
# Number of trips are in individuals. 
# Only pairs with 1 person or more are taken into these files. 

inputfile_Tpred_car= foldername_input + 'baseline/TPred1.csv' 
inputfile_Tpred_bus= foldername_input + 'baseline/TPred2.csv'
inputfile_Tpred_rail= foldername_input + 'baseline/TPred3.csv' 


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
#2.1.1 Read in the Dij files which are stored as zip files because they are large.
######################

#Python package zipfile does not work with thes zips because Richard compressed them 
#using a type 9: Deflate64/Enhanced Deflate (PKWare's proprietary format which is 
#not supported by Python

#One solution is to unzip in the terminal first
#1) Type “unzip” and a space, then drag/drop the zip file into the Terminal window.
#2) Press Enter and the zip file will be unzipped, storing all files on your computer.
#3) Your unzipped files will go to your user account folder which you can easily access using Finder or sporligth (command + R).


while dij:
	print("\nWe are treating the dij input")

	while car:
		start_time = time.time()

		print("\nReading in the Dij file for car: " + '\n' + str(inputfile_Dij_car))
		
		df_Dij_car=pd.read_csv(inputfile_Dij_car, sep=',', lineterminator='\n') 
		df_Dij_car=df_Dij_car.rename(columns={'data\r': 'Dij_car'})

		print ('\n The number of rows and columns in the Dij_car dataframe are:')
		print(df_Dij_car.shape)

		print ('\n The first five lines of the Dij_car dataframe look like this:')
		print(df_Dij_car.head())

		available_inputfiles['Dij']['car']=df_Dij_car

		print ("\nRead in time for Dij_car:", time.time()-start_time)
		break


	while bus:
		start_time = time.time()

		print("\nReading in the Dij file for bus: " + '\n' + str(inputfile_Dij_bus))
		
		df_Dij_bus=pd.read_csv(inputfile_Dij_bus, sep=',', lineterminator='\n')
		df_Dij_bus=df_Dij_bus.rename(columns={'data\r': 'Dij_bus'}) 

		print ('\n The number of rows and columns in the Dij_bus dataframe are:')
		print(df_Dij_bus.shape)

		print ('\n The first five lines of the Dij_bus dataframe look like this:')
		print(df_Dij_bus.head())

		print ("\nRead in time for Dij_bus:", time.time()-start_time)

		available_inputfiles['Dij']['bus']=df_Dij_bus

		break


	while rail:
		start_time = time.time()
		
		print("\nReading in the Dij file for rail: " + '\n' + str(inputfile_Dij_rail))
		
		df_Dij_rail=df_Dij_rail=pd.read_csv(inputfile_Dij_rail, sep=',', lineterminator='\n') 
		df_Dij_rail=df_Dij_rail.rename(columns={'data\r': 'Dij_rail'})
		
		print ('\n The number of rows and columns in the Dij_rail dataframe are:')
		print(df_Dij_rail.shape)

		print ('\n The first five lines of the Dij_rail dataframe look like this:')
		print(df_Dij_rail.head())

		print ("\nRead in time for Dij_rail:", time.time()-start_time)

		available_inputfiles['Dij']['rail']=df_Dij_rail

		break

	break


######################
#2.1.2 Read in the Tobs files.
######################

while tobs:
	print("\nWe are treating the tobs input")

	while car:
		start_time = time.time()

		print("\nReading in the Tobs file for car: " + '\n' + str(inputfile_Tobs_car))

		df_Tobs_car=pd.read_csv(inputfile_Tobs_car, sep=',', lineterminator='\n') 
		df_Tobs_car=df_Tobs_car.rename(columns={'data\r': 'Tobs_car'})

		print ('\n The number of rows and columns in the Tobs_car dataframe are:')
		print(df_Tobs_car.shape)

		print ('\n The first five lines of the Tobs_car dataframe look like this:')
		print(df_Tobs_car.head())

		print ("\nRead in time for Tobs_car:", time.time()-start_time)

		available_inputfiles['Tobs']['car']=df_Tobs_car

		break

	while bus:
		start_time = time.time()

		print("\nReading in the Tobs file for bus: " + '\n' + str(inputfile_Tobs_bus))
		
		df_Tobs_bus=pd.read_csv(inputfile_Tobs_bus, sep=',', lineterminator='\n')
		df_Tobs_bus=df_Tobs_bus.rename(columns={'data\r': 'Tobs_bus'}) 

		print ('\n The number of rows and columns in the Tobs_bus dataframe are:')
		print(df_Tobs_bus.shape)

		print ('\n The first five lines of the Tobs_bus dataframe look like this:')
		print(df_Tobs_bus.head())

		print ("\nRead in time for Tobs_bus:", time.time()-start_time)

		available_inputfiles['Tobs']['bus']=df_Tobs_bus

		break

	while rail:
		start_time = time.time()

		print("\nReading in the Tobs file for rail: " + '\n' + str(inputfile_Tobs_rail))
		
		df_Tobs_rail=df_Tobs_rail=pd.read_csv(inputfile_Tobs_rail, sep=',', lineterminator='\n') 
		df_Tobs_rail=df_Tobs_rail.rename(columns={'data\r': 'Tobs_rail'})
		
		print ('\n The number of rows and columns in the Tobs_rail dataframe are:')
		print(df_Tobs_rail.shape)

		print ('\n The first five lines of the Tobs_rail dataframe look like this:')
		print(df_Tobs_rail.head())

		available_inputfiles['Tobs']['rail']=df_Tobs_rail

		print ("\nRead in time for Tobs_rail:", time.time()-start_time)

		break

	break

######################
#2.1.3 Read in the Tpred files 
######################


while tpred:
	print("\nWe are treating the tpred input")

	while car:
		start_time = time.time()

		print("\nReading in the Tpred file for car: " + '\n' + str(inputfile_Tpred_car))

		df_Tpred_car=pd.read_csv(inputfile_Tpred_car, sep=',', lineterminator='\n') 
		df_Tpred_car=df_Tpred_car.rename(columns={'data\r': 'Tpred_car'})

		print ('\n The number of rows and columns in the Tpred_car dataframe are:')
		print(df_Tpred_car.shape)

		print ('\n The first five lines of the Tpred_car dataframe look like this:')
		print(df_Tpred_car.head())

		print ("\nRead in time for Tpred_car:", time.time()-start_time)

		available_inputfiles['Tpred']['car']=df_Tpred_car

		break

	while bus:
		start_time = time.time()

		print("\nReading in the Tpred file for bus: " + '\n' + str(inputfile_Tpred_bus))
		
		df_Tpred_bus=pd.read_csv(inputfile_Tpred_bus, sep=',', lineterminator='\n')
		df_Tpred_bus=df_Tpred_bus.rename(columns={'data\r': 'Tpred_bus'}) 

		print ('\n The number of rows and columns in the Tpred_bus dataframe are:')
		print(df_Tpred_bus.shape)

		print ('\n The first five lines of the Tpred_bus dataframe look like this:')
		print(df_Tpred_bus.head())

		available_inputfiles['Tpred']['bus']=df_Tpred_bus

		print ("\nRead in time for Tpred_bus:", time.time()-start_time)

		break

	while rail:
		start_time = time.time()
		
		print("\nReading in the Tpred file for rail: " + '\n' + str(inputfile_Tpred_rail))
		
		df_Tpred_rail=pd.read_csv(inputfile_Tpred_rail, sep=',', lineterminator='\n') 
		df_Tpred_rail=df_Tpred_rail.rename(columns={'data\r': 'Tpred_rail'})
		
		print ('\n The number of rows and columns in the Tpred_rail dataframe are:')
		print(df_Tpred_rail.shape)

		print ('\n The first five lines of the Tpred_rail dataframe look like this:')
		print(df_Tpred_rail.head())

		available_inputfiles['Tpred']['rail']=df_Tpred_rail

		print ("\nRead in time for Tpred_rail:", time.time()-start_time)

		break

	break


######################
#1.2.4 MSOA Shapefile
######################
'''
#Read in shapefile in geopandas
gp_MSOA=gpd.read_file(inputfile_shapefile_MSOA)


#Plot map from shapefile
print ('\n We are now plotting the MSOAs of GB')
print(gp_MSOA.plot())
plt.show()
plt.close("all")

#Have a look at the database behind the shapefile
print ('\n The number of rows and columns in the dij_car dataframe are:')
print(gp_MSOA.shape)

print ('\n The first five lines of the shapefile on MSOA look like this')
print(gp_MSOA.head())#Get first 10 lines to be printed
'''

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



########################################################
#3. Unfold data to become dataframe in matrix style. 
########################################################

# Our aim is to construct a 8436 by 8436 dataframe that can hold the trips, dij, etc for each MSOA pair. 
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


infile = open('/Users/Metti_Hoof/Desktop/Test/Pickle_storage/E02000003_work_to_home_Tobs_rail','rb')
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
df_Dij_rail.head(10000).to_csv('/Users/Metti_Hoof/Desktop/Test/df_Dij_rail_subset.csv')
"""

#Read in stored subset
print('\nWe are reading in the stored subsets for developing purposes')
df_Dij_rail_subset=pd.read_csv('/Users/Metti_Hoof/Desktop/Test/df_Dij_rail_subset.csv',sep=',', lineterminator='\n') 
df_Dij_rail_subset=df_Dij_rail_subset.drop(columns=['Unnamed: 0'])

print ('\n The first five lines of the df_Dij_rail_subset dataframe look like this:')
print(df_Dij_rail_subset.head())

MSOA_list_of_origins_in_subset=list(df_Dij_rail_subset['origin_msoacode'].unique())

print ('\n The unique origins in the subset are:')
print(MSOA_list_of_origins_in_subset)
########################################################

## Trying to construct a 8436 by 8436 dataframe that can hold the trips, dij, etc for each MSOA pair. 

df_to_merge=df_MSOA_unique_values
df_storage=df_MSOA_unique_values

#Set origin msoa_code to be the index, this makes the filtering a lot faster
df_Dij_rail_for_filtering=df_Dij_rail_subset[['origin_msoacode','destination_msoacode','Dij_rail']].copy()
df_Dij_rail_for_filtering=df_Dij_rail_for_filtering.set_index('origin_msoacode')

msoa_counter=0

for MSOA in MSOA_list_of_origins_in_subset:
	if colcounter%1000==0:
		print('The code is at column number: ' + str(msoa_counter) + ' and there are ' + str(len(MSOA_list_of_origins_in_subset)) + ' columns to process')

	print(MSOA)

	#Select only those rows where the index (origin_msoacode) == a value
	df_filtered=df_Dij_rail_for_filtering.loc[MSOA]
	df_filtered=df_filtered.reset_index()

	print("Filtered")
	print(df_filtered.shape)
	print(df_filtered.head())

	#
	df_tussen=pd.merge(df_to_merge, df_filtered[['destination_msoacode','Dij_rail']], how='left',left_on='MSOA', right_on='destination_msoacode')
	print("Tussen")
	print(df_tussen.shape)
	print(df_tussen.head())

	df_storage[MSOA]=df_tussen['Dij_rail']
	print("Storage")
	print(df_storage.head())


'''



'''
# The dij files are matrices with headers and columns available. 
# Remember that the initial dij data is in 1/minutes, so we do 1 / dij to get to minutes. 
# Some of the dij values are '∞' because it is 1/time and if time is 0
# They are replaced by a value of choice which is hardcoded in the beginning of the file
# inside the hardcoded_infinity_replace_value variable. 


while car:
	print("Reading in the dij file for car: " +'\n' + str(inputfile_dij_car))
	df_dij_car_in=pd.read_csv(inputfile_dij_car,sep=',', lineterminator='\n', header=0) 
	df_dij_car_in.set_index('MSOA',inplace=True)

	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_dij_car_in=df_dij_car_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_dij_bus to be float entirely. 
	df_dij_car_in= df_dij_car_in.astype(float)

	#Set the df_dij to be in minutes. Remember that the initial dij data is in 1/minutes
	df_dij_car=1/df_dij_car_in

	print ('\n The number of rows and columns in the dij_car dataframe are:')
	print(df_dij_car.shape)

	print ('\n The first five lines of the dij_car dataframe look like this:')
	print(df_dij_car.head())

	break

	# When importing we get a warning that columns 4588 and 6640 have mixed dtypes, 
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
	df_dij_bus_in=pd.read_csv(inputfile_dij_bus,sep=',',header=0,index_col='MSOA')

	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_dij_bus_in=df_dij_bus_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_dij_bus to be float entirely. 
	df_dij_bus_in = df_dij_bus_in.astype(float)

	#Set the df_dij to be in minutes. Remember that the initial dij data is in 1/minutes
	df_dij_bus=1/df_dij_bus_in

	print ('\n The number of rows and columns in the dij_bus dataframe are:')
	print(df_dij_bus.shape)

	print ('\n The first five lines of the dij_bus dataframe look like this:')
	print(df_dij_bus.head())

	break

while rail:
	print("Reading in the dij file for rail: " +'\n' + str(inputfile_dij_rail))
	df_dij_rail_in=pd.read_csv(inputfile_dij_rail,sep=',', lineterminator='\n', header=0) 
	df_dij_rail_in.set_index('MSOA',inplace=True) 

	####################### Personal hard-coding #####################
	#The input file has quite some infinities in them, we replace them wit an arbitrary value so far. 
	df_dij_rail_in=df_dij_rail_in.replace('∞',hardcoded_infinity_replace_value)
	####################### Personal hard-coding #####################
	
	#Force the d_dij_bus to be float entirely. 
	df_dij_rail_in = df_dij_rail_in.astype(float)

	#Set the df_dij to be in minutes. Remember that the initial dij data is in 1/minutes
	df_dij_rail=1/df_dij_rail_in

	print ('\n The number of rows and columns in the dij_rail dataframe are:')
	print(df_dij_rail.shape)

	print ('\n The first five lines of the dij_rail dataframe look like this:')
	print(df_dij_rail.head())

	break



'''
######################
#2.1.3 Read in the Tobs files 
######################
'''
while car:
	print("Reading in the Tobs file for car: " + '\n' + str(inputfile_Tobs_car))
	df_Tobs_car=pd.read_csv(inputfile_Tobs_car, sep=',', lineterminator='\n') 

	df_Tobs_car=df_Tobs_car.rename(columns={'data\r': 'Tobs_car'})

	print ('\n The number of rows and columns in the Tobs_car dataframe are:')
	print(df_Tobs_car.shape)

	print ('\n The first five lines of the Tobs_car dataframe look like this:')
	print(df_Tobs_car.head())

	break

while bus:
	print("Reading in the Tobs file for bus: " + '\n' + str(inputfile_Tobs_bus))
	df_Tobs_bus=pd.read_csv(inputfile_Tobs_bus, sep=',', lineterminator='\n')

	df_Tobs_bus=df_Tobs_bus.rename(columns={'data\r': 'Tobs_bus'}) 

	print ('\n The number of rows and columns in the Tobs_bus dataframe are:')
	print(df_Tobs_bus.shape)

	print ('\n The first five lines of the Tobs_bus dataframe look like this:')
	print(df_Tobs_bus.head())

	break

while rail:
	print("Reading in the Tobs file for rail: " + '\n' + str(inputfile_Tobs_rail))
	
	df_Tobs_rail=df_Tobs_rail=pd.read_csv(inputfile_Tobs_rail, sep=',', lineterminator='\n') 

	df_Tobs_rail=df_Tobs_rail.rename(columns={'data\r': 'Tobs_rail'})
	
	print ('\n The number of rows and columns in the Tobs_rail dataframe are:')
	print(df_Tobs_rail.shape)

	print ('\n The first five lines of the Tobs_rail dataframe look like this:')
	print(df_Tobs_rail.head())

	break


######################
#2.1.3 Read in the Tpred files 
######################

while car:
	print("Reading in the Tpred file for car: " + '\n' + str(inputfile_Tpred_car))
	df_Tpred_car=pd.read_csv(inputfile_Tpred_car, sep=',', lineterminator='\n') 

	df_Tpred_car=df_Tpred_car.rename(columns={'data\r': 'Tpred_car'})

	print ('\n The number of rows and columns in the Tpred_car dataframe are:')
	print(df_Tpred_car.shape)

	print ('\n The first five lines of the Tpred_car dataframe look like this:')
	print(df_Tpred_car.head())

	break

while bus:
	print("Reading in the Tpred file for bus: " + '\n' + str(inputfile_Tpred_bus))
	df_Tpred_bus=pd.read_csv(inputfile_Tpred_bus, sep=',', lineterminator='\n')

	df_Tpred_bus=df_Tpred_bus.rename(columns={'data\r': 'Tpred_bus'}) 

	print ('\n The number of rows and columns in the Tpred_bus dataframe are:')
	print(df_Tpred_bus.shape)

	print ('\n The first five lines of the Tpred_bus dataframe look like this:')
	print(df_Tpred_bus.head())

	break

while rail:
	print("Reading in the Tpred file for rail: " + '\n' + str(inputfile_Tpred_rail))
	
	df_Tpred_rail=pd.read_csv(inputfile_Tpred_rail, sep=',', lineterminator='\n') 

	df_Tpred_rail=df_Tpred_rail.rename(columns={'data\r': 'Tpred_rail'})
	
	print ('\n The number of rows and columns in the Tpred_rail dataframe are:')
	print(df_Tpred_rail.shape)

	print ('\n The first five lines of the Tpred_rail dataframe look like this:')
	print(df_Tpred_rail.head())

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

'''