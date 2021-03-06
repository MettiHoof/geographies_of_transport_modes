
##############################################################################################
# -*- coding: utf-8 -*-
# Script to investigate the signatures per MSOA
# In this script, we will explore characteristics per MSOA from Dij, Tobj and Tpred data from Quant2.
# Written by Maarten Vanhoof, in MARCH 2020.
# Python 3
#
# Source files are produced by the Read_in_baseline_quant2.py script
# Which is using inputdata from Quant 2 as provided by Richard Miltion the 20th of March 2020
#
# The inputfile are pickles with the following naming:
# {MSOA}_home_to_work or {MSOA}work_to_home e.g. E02000518_home_to_work
#
# within these files is a dataframe containing the following columns. 
#
# MSOA_home: MSOA that is considered as home: in home_to_work this is one MSOA only 
# MSOA_work: MSOA that is considered work, in work_to_hone this is one MSOA only
#
# Tobs: observed commuting flows based on census data (in people)
# Tpred: Quant2 prediction for a baseline scenario (in people)
# Dij: distance between MSOA based on shordf_to_plot route in Quant2 (in minutes)
#
#
##############################################################################################

########################################################
#-1. User Decisions.
########################################################

#Put to True if you want to use this direction. 
#Note that you can only use one direction at the time
home_to_work=True
work_to_home=False

if home_to_work and work_to_home:
	raise Exception('You have selected both home_to_work and work_to_home to be True, please choose only one to be True.')
elif home_to_work==False and work_to_home==False:
	raise Exception('You have selected both home_to_work and work_to_home to be False, please choose one of them to be True.')


#Put to True if you want to use the observed commuters (from census) or the predicted commuters (from the quant model) 
#Note that you can only use one direction at the time
observed=False
predicted=True

if observed and predicted:
	raise Exception('You have selected both observed and predicted to be True, please choose only one to be True.')
elif observed==False and predicted==False:
	raise Exception('You have selected both observed and predicted to be False, please choose one of them to be True.')



########################################################
#-1. Hard-coded elements
########################################################
########################################################
#0. Setup environment
########################################################

############################
#0.1 Import dependencies
############################
import pandas as pd #For data handling
import numpy as np #For matrix handling
import time #For timing 
import math #For math handling
import geopandas as gpd #For geographic work
import matplotlib #for plotting
#matplotlib.use("TkAgg") #matplotlibs needs to use this backend to not crash on the new mac. 
import matplotlib.pylab as plt #For interactive plotting
import brewer2mpl #Colors for matplotlib
import pickle #For storing data in pickles 

############################
#0.2 Setup in and output paths
############################

#Where inputdata lives and output will be put
foldername_input_pickle ='/Users/Metti_Hoof/Desktop/Heavy_data/Pickle_storage_baseline/'  
foldername_output ='/Users/Metti_Hoof/Desktop/Test/' 


############################
#0.3 Setup iterators
############################

#make a mode_list storing the active modes.
mode_list=['car','bus','rail']

#make an input_list storing the metrics we will be using.
metric_list=['Dij','Tobs','Tpred']


############################
#0.4 Setup figure specifications
############################

label_titles={'retained_number_of_msoas': 'Amount of MSOAs commuted to per MSOA',
			'retained_number_of_commuters':'Amount of commuters per MSOA',
			'absolute': 'Cumulative sum',
			'percentage': 'Weighted cumulative sum (%)'
			}


subplot_titles={'retained_number_of_msoas': 'number of MSOAs commuted to',
			'retained_number_of_commuters':'number of commuters',
			'trips': 'number of trips',
			'shordf_to_plot_route':'shordf_to_plot route',
			'time_spent':'time spent on shortest route',
			'absolute': 'Cumulative sum',
			'percentage': 'Weighted cumulative sum',
			'observed':'observed number of trips',
			'predicted':'predicte number of trips'
			}


bmap = brewer2mpl.get_map('Set1', 'qualitative', 3)
colorbrew=bmap.hex_colors
#colorbrew.append('#808080') #put extra color grey to end because set2 only goes to 8 and we need 9 colors.
color_dict_mode={'car':colorbrew[0],
            'bus':colorbrew[1],
            'rail':colorbrew[2]
            }


########################################################
#1. Read in inputfiles
########################################################

############################
#1.1 Set names of inputfiles
############################

# The files we will be using in this script are dataframes, stored as pickles (one per MSOA).
# We will thus have to read in these files on the fly when treating them. The following section just
# gives you an example for one MSOA (E02000003) of how to read in these pickles into pandas. 

MSOA='E02000003'
MSOA_list=['E02000003']



if home_to_work:
	filename=foldername_input_pickle+MSOA+'_home_to_work'
	
	infile = open(filename,'rb')
	df_input = pickle.load(infile)
	infile.close()

	print ('The first five rows of the home to work pickle for MSOA {0} look like this:'.format(MSOA))
	print(df_input.head())

	print ('The available columns in the home to work pickle for MSOA {0} are:'.format(MSOA))
	print(df_input.columns)

elif work_to_home:
	filename=filename=foldername_input_pickle+MSOA+'_work_to_home'

	infile = open(filename,'rb')
	df_input = pickle.load(infile)
	infile.close()

	print ('The first five rows of the work to home pickle for MSOA {0} look like this:'.format(MSOA))
	print(df_input.head())

	print ('The available columns in the work to home pickle for MSOA {0} are:'.format(MSOA))
	print(df_input.columns)


else:
	print('Please put either home_to_work or work_to_home to True to continue.')



######################
#1.2 MSOA Shapefile
######################
'''

#Shapefile with MSOA locations
inputfile_shapefile_MSOA= '/Users/Metti_Hoof/Desktop/Quant Developing/data/shapefiles/EPSG7405_MSOA_2011/EPSG7405_MSOA_2011.shp'

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
#1.3 MSOA Unique values file
######################
'''
#Csv file with all unique MSOAs
inputfile_unique_MSOA='/Users/Metti_Hoof/Desktop/Quant Developing/data/Signatures/MSOA11_unique.csv'

#Read in file.
df_MSOA_unique_values=pd.read_csv(inputfile_unique_MSOA,sep=',', lineterminator='\n') 

#Drop unneccesary line
df_MSOA_unique_values=df_MSOA_unique_values.drop(columns=['Unnamed: 0'])

print ('\n The number of rows and columns in the MSOA unique values dataframe are:')
print(df_MSOA_unique_values.shape)

print ('\n The first five lines of the MSOA unique values dataframe look like this:')
print(df_MSOA_unique_values.head())

MSOA_list=list(df_MSOA_unique_values['MSOA'])
'''



########################################################
#2. Plotting information per MSOA
########################################################


############################
#2.1 Visualising number of trips per mode for a given distance for each MSOA.
############################

'''
df_to_plot=df_input

if observed:
	df_to_plot=df_input[['Tobs_car','Tobs_bus', 'Tobs_rail','Dij_car','Dij_bus', 'Dij_rail']]
	df_to_plot=df_to_plot.rename(columns={'Tobs_car': 'Abs_car','Tobs_bus': 'Abs_bus','Tobs_rail': 'Abs_rail'}) #Rename for use
	print('\nWe will be plotting for the observed cases.')

if predicted:
	df_to_plot=df_input[['Tpred_car','Tpred_bus', 'Tpred_rail','Dij_car','Dij_bus', 'Dij_rail']]
	df_to_plot=df_to_plot.rename(columns={'Tpred_car': 'Abs_car','Tpred_bus': 'Abs_bus','Tpred_rail': 'Abs_rail'}) #Rename for use
	print('\nWe will be plotting for the predicted cases.')

#Create values for the CDF. 
df_to_plot['Rel_car']=df_to_plot['Abs_car']/df_to_plot['Abs_car'].sum()
df_to_plot=df_to_plot.sort_values(by='Dij_car', ascending=True)
df_to_plot['Cumsum_percentage_car']=df_to_plot['Rel_car'].cumsum()

df_to_plot['Rel_bus']=df_to_plot['Abs_bus']/df_to_plot['Abs_bus'].sum()
df_to_plot=df_to_plot.sort_values(by='Dij_bus', ascending=True)
df_to_plot['Cumsum_percentage_bus']=df_to_plot['Rel_bus'].cumsum()

df_to_plot['Rel_rail']=df_to_plot['Abs_rail']/df_to_plot['Abs_rail'].sum()
df_to_plot=df_to_plot.sort_values(by='Dij_rail', ascending=True)
df_to_plot['Cumsum_percentage_rail']=df_to_plot['Rel_rail'].cumsum()



#Setting up figure specifications 
figsize_x_cm=21 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
figsize_y_cm=14
figsize_y_inches=figsize_y_cm/2.54

#define number of subplots.
ncols=3
nrows=2

#Set up fig and ax
fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
#axarr[row][col]

#Adjust subplots
left   =  0.08  # the left side of the subplots of the figure
right  =  0.97    # the right side of the subplots of the figure
bottom =  0.13    # the bottom of the subplots of the figure
top    =  0.9    # the top of the subplots of the figure
wspace =  .15     # the amount of width reserved for blank space between subplots
hspace =  .23    # the amount of height reserved for white space between subplots

# This function adjusts the subplots using the parameters defined earlier
plt.subplots_adjust(
left    =  left, 
bottom  =  bottom, 
right   =  right, 
top     =  top, 
wspace  =  wspace, 
hspace  =  hspace
)

#Absolute values
sc0= axarr[0][0].scatter(x=df_to_plot['Dij_car'],y=df_to_plot['Abs_car'], c=color_dict_mode['car'],s=df_to_plot['Abs_car'])
sc1= axarr[0][1].scatter(x=df_to_plot['Dij_bus'],y=df_to_plot['Abs_bus'], c=color_dict_mode['bus'],s=df_to_plot['Abs_bus'])
sc2= axarr[0][2].scatter(x=df_to_plot['Dij_rail'],y=df_to_plot['Abs_rail'], c=color_dict_mode['rail'], s=df_to_plot['Abs_rail'])


#CDF
sc0= axarr[1][0].scatter(x=df_to_plot['Dij_car'],y=df_to_plot['Cumsum_percentage_car'], c=color_dict_mode['car'],s=1)
sc1= axarr[1][1].scatter(x=df_to_plot['Dij_bus'],y=df_to_plot['Cumsum_percentage_bus'], c=color_dict_mode['bus'],s=1)
sc2= axarr[1][2].scatter(x=df_to_plot['Dij_rail'],y=df_to_plot['Cumsum_percentage_rail'], c=color_dict_mode['rail'], s=1)

#Set titles
if home_to_work:
	if observed:
		title='Observed number of commuters leaving home from MSOA: {0}'.format(MSOA)
	if predicted:
		title='Predicted number of commuters leaving home from MSOA: {0}'.format(MSOA)

elif work_to_home:
	if observed:
		title='Observed number of commuters leaving work from MSOA: {0}'.format(MSOA)
	if predicted:
		title='Predicted number of commuters leaving work from MSOA: {0}'.format(MSOA)

plt.suptitle(title, fontsize=14)

#Set boxes
axarr[0][0].text(.97, .97, 'by car', ha='right', va='top', rotation=0, fontsize=11, color='black',transform=axarr[0][0].transAxes,
			bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':color_dict_mode['car']})
axarr[0][1].text(.97, .97, 'by bus', ha='right', va='top', rotation=0, fontsize=11, color='black',transform=axarr[0][1].transAxes,
			bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':color_dict_mode['bus']})
axarr[0][2].text(.97, .97, 'by rail', ha='right', va='top', rotation=0, fontsize=11, color='black',transform=axarr[0][2].transAxes,
			bbox={'facecolor':'white', 'alpha':0.8,'edgecolor':color_dict_mode['rail']})

#Set up x axis (log scale)
logticks=[1,10,30,100,500]
loglabels=[1,10,30,100,500]

#All subplots
for axrow in axarr:
	for ax in axrow:
		ax.set_xlim(1,1000)
		ax.set_xscale('log')
		ax.set_xticks(logticks)
		ax.set_xticklabels(loglabels)
		#ax.set_xlabel('Distance (km)',fontsize=9)
		ax.tick_params(axis='x',which='major',labelsize=9,length=4,direction='out',color='0.4')
		ax.tick_params(axis='x',which='minor',labelsize=9,length=2,direction='out',color='0.6')


#Absolute number subplots
for ax in axarr[0]:
	#Set up y axis (max of observations as limit)
	y_max=df_to_plot[['Abs_car','Abs_bus','Abs_rail']].max().max()
	y_max=y_max+y_max*0.1
	ax.set_ylim(1,y_max)
	ax.tick_params(axis='y',labelsize=9,length=2,direction='in',color='0.4')

#Relative numbers subplots
for ax in axarr[1]:
	#Set up y axis
	ax.set_ylim(0,1.02)
	ax.tick_params(axis='y',labelsize=9,length=2,direction='in',color='0.4')


#Title for left plot
axarr[0][0].set_ylabel('Number of commuters',fontsize=10)
#Title for left plot
axarr[1][0].set_ylabel('Cumulative share of commuters',fontsize=10)
#Title for midle plot
axarr[1][1].set_xlabel('Distance of commute (km)',fontsize=10)


#Change outlook of boxes of visuals for all subplots
for axrow in axarr:
	for ax in axrow:
		#Set gridlines
		ax.grid(axis='y', color="0.85", linestyle='--', alpha=0.6, linewidth=0.5)
		ax.grid(axis='x', which='major', color="0.6", linestyle='--', alpha=0.6, linewidth=0.8)		
		ax.grid(axis='x', which='minor', color="0.85", linestyle='--', alpha=0.6, linewidth=0.5)		
		# put the grid behind
		ax.set_axisbelow(True)

		#Make frame lighter and change line-width:
		for pos in ['top','bottom','left','right']:
			ax.spines[pos].set_linewidth(0.8)
			ax.spines[pos].set_color('0.6')

#save or show
#plt.show()

if home_to_work:
	if observed:
		outputname='Distance_distribution_{0}_home_to_work_observed.png'.format(MSOA)
	if predicted:
		outputname='Distance_distribution_{0}_home_to_work_predicted.png'.format(MSOA)

if work_to_home:
	if observed:
		outputname='Distance_distribution_{0}_work_to_home_observed.png'.format(MSOA)
	if predicted:
		outputname='Distance_distribution_{0}_work_to_home_predicted.png'.format(MSOA)

output=foldername_output+outputname
plt.savefig(output)
plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
#plt.clf() #clear the entire figure. Since we define this one outside the loop, we don't want that.
print ('Figure saved')

'''

############################
#2.2 Plot of cumulative percentage of individual MSOAs
############################

#Create a plot showing the cumulative percentage or absolute values of trips, spent_time or shordf_to_plot route per MSOA by transport mode. 

################
#2.2.1 Set helper functions ready:
################


def msoa_df_creator_cumsum_abs_value(df, cut_off=False):
	"""This function calculates the cumulative sum of the values in a dataframe for each column
	The output of the filter is a dict with, for each column, a dataframe containing the values, percentage, and cumsum.
	If cut_off=True, then the MSOA pairs for which no commuters where observed will be cut off from the dataframe."""

	if cut_off:
		print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
	else:
		print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')

	#Setting up intermediate storage
	dict_out={}
	for col in df.columns:
		dict_out[col]={}
	colcounter=0

	print('\nWe are calculating the cumsum absolute values for all the MSOAs')
	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by=col, ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum_absvalues']=df_subset_sorted[col].cumsum()

		if cut_off==True:
			#print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
			
			#Cut off the pairs that do not contribute.	
			df_subset_sorted_cut_off=df_subset_sorted.loc[(df_subset_sorted[col]> 0)]
			
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted_cut_off

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted_cut_off.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted_cut_off[col].sum()
		
		else:
			#print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted[col].sum()
	
	return dict_out




def msoa_df_creator_cumsum_percentage(df, cut_off=False):
	"""This function calculates the cumulative sum of the percentage of values in a dataframe for each column
	The output of the filter is a dict with, for each column, a dataframe containing the values, percentage, and cumsum.
	If cut_off=True, then the MSOA pairs for which no commuters where observed will be cut off from the dataframe."""

	if cut_off:
		print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
	else:
		print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')

	#Setting up intermediate storage
	dict_out={}
	for col in df.columns:
		dict_out[col]={}
	colcounter=0

	print('\nWe are calculating the cumsum percentage for all the MSOAs')
	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by='percentage', ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum_percentage']=df_subset_sorted['percentage'].cumsum()

		if cut_off==True:
			#print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
			
			#Cut off the pairs that do not contribute.	
			df_subset_sorted_cut_off=df_subset_sorted.loc[(df_subset_sorted['percentage']> 0)]
			
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted_cut_off

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted_cut_off.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted_cut_off[col].sum()
		
		else:
			#print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted[col].sum()
	
	return dict_out


############################
#2.2.2 Start plotting for each individual MSOA and mode. 
############################
'''
value_type_list=['absolute','percentage'] #choose one or both 'absolute','percentage'
mode_list=['rail']
metric_list=['predicted'] #'observed','predicted'
MSOA_list=['E02000003','E02000004']

home_to_work=True
work_to_home=False


#Setting up figure specifications 
figsize_x_cm=12 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
figsize_y_cm=10
figsize_y_inches=figsize_y_cm/2.54

#define number of subplots.
ncols=1
nrows=1

#Set up fig and ax
fig, ax = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
#axarr[row][col]

#Adjust subplots
left   =  0.15  # the left side of the subplots of the figure
right  =  0.90    # the right side of the subplots of the figure
bottom =  0.25    # the bottom of the subplots of the figure
top    =  0.85    # the top of the subplots of the figure
wspace =  .0     # the amount of width reserved for blank space between subplots
hspace =  .0    # the amount of height reserved for white space between subplots

# This function adjusts the subplots using the parameters defined earlier
plt.subplots_adjust(
left    =  left, 
bottom  =  bottom, 
right   =  right, 
top     =  top, 
wspace  =  wspace, 
hspace  =  hspace
)


for MSOA in MSOA_list:
	#Read in data
	if home_to_work:
		filename=foldername_input_pickle+MSOA+'_home_to_work'
		infile = open(filename,'rb')
		df_input = pickle.load(infile)
		infile.close()

	elif work_to_home:
		filename=filename=foldername_input_pickle+MSOA+'_work_to_home'
		infile = open(filename,'rb')
		df_input = pickle.load(infile)
		infile.close()

	else:
		print('Please put either home_to_work or work_to_home to True to continue.')


	#Create storage
	storage_dict={}

	for metric in metric_list:
		for mode in mode_list:
			for value_type in value_type_list:
				print('\nWe are creating the cumulative {0} value graph for {1} of for mode {2} and MSOA: {3}'.format(value_type, metric, mode,MSOA))

				#Set the name of the rows we want to use:
				if metric=='observed':
					col_to_plot='Tobs_{}'.format(mode)

				elif metric=='predicted':
					col_to_plot='Tpred_{}'.format(mode)


				#Get the data we need from the helper functions
				if value_type=='absolute':
					storage_dict=msoa_df_creator_cumsum_abs_value(df_input[[col_to_plot]],cut_off=True) #we do [[]] here so it becomes a df, which is the required input for our helper function creator.
				elif value_type=='percentage':
					storage_dict=msoa_df_creator_cumsum_percentage(df_input[[col_to_plot]],cut_off=True)
				

				#Get the cumulative, ordered data into a numpy array using values function. We will use this array to plot.
				if value_type=='absolute':
					a=storage_dict[col_to_plot]['retained_df']['cumsum_absvalues'].values
				elif value_type=='percentage':
					a=storage_dict[col_to_plot]['retained_df']['cumsum_percentage'].values
					#Get percentages.
					a=a*100

				#Insert a zero value so the line can start from 0,0.	
				a=np.insert(a, 0, 0)
				#Create rank values for x_axis
				x_a=list(range(0,len(a)))

				#Get color:
				#bmap = brewer2mpl.get_map('Blues', 'sequential', 3)
				#colorbrew=bmap.hex_colors

				#Plot on currently active axis.
				ax.plot(a,color=color_dict_mode[mode], alpha=0.75)

				#Helpline
				slope=max(a)/max(x_a)
				yhelp=[i *slope for i in x_a] 
				help_line=ax.plot(x_a,yhelp,ls='--',lw=1,color='.4',alpha=0.6)

				#Set titles
				title1='{0} of {1} by {2}'.format(subplot_titles[value_type],subplot_titles[metric],mode)
				ax.set_title(title1, y = 0.98, fontsize=10)

				#Set y limits
				#ax.set_ylim(0,1)

				#Set label titles
				ax.set_xlabel('Rank of destination MSOA (by contribution)',fontsize=9)
				ax.set_ylabel('{0}'.format(label_titles[value_type]),fontsize=9)

				# Set grid
				ax.grid(which = 'major', alpha = 0.4,ls=':')

				# put the grid behind
				ax.set_axisbelow(True)
				
				# Set ticks parameters
				ax.tick_params(axis = 'x', which = 'major', length=2, labelsize = 8) 
				ax.tick_params(axis = 'y', which = 'major', length=2, labelsize = 8) 
				
				# Make frame lighter and change line-width:
				for pos in ['top','bottom','left','right']:
					ax.spines[pos].set_linewidth(0.5)
					ax.spines[pos].set_color('0.6')

				# #save or show
				# plt.show()
				if home_to_work:
					outputname='Cumsum_individual_modes/{3}_cumsum_{0}_{1}_by_{2}_home_to_work.png'.format(value_type,metric,mode,MSOA)
				if work_to_home:
					outputname='Cumsum_individual_modes/{3}_cumsum_{0}_{1}_by_{2}_work_to_home.png'.format(value_type,metric,mode,MSOA)

				output=foldername_output+outputname
				plt.savefig(output)
				plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
				#plt.clf() #clear the entire figure. Since we define this one outside the loop, we don't want that.
				print ('Figure saved')
'''



############################
#2.2.3 Start plotting all modes for each individual MSOA, compare predicted with observed. 
############################

value_type_list=['absolute','percentage'] #choose one or both 'absolute','percentage'
mode_list=['car','bus','rail']
MSOA_list=['E02000003','E02000004']

home_to_work=True
work_to_home=False


for MSOA in MSOA_list:
	#Read in data
	if home_to_work:
		filename=foldername_input_pickle+MSOA+'_home_to_work'
		infile = open(filename,'rb')
		df_input = pickle.load(infile)
		infile.close()

	elif work_to_home:
		filename=filename=foldername_input_pickle+MSOA+'_work_to_home'
		infile = open(filename,'rb')
		df_input = pickle.load(infile)
		infile.close()

	else:
		print('Please put either home_to_work or work_to_home to True to continue.')



	#Setting up figure specifications 
	figsize_x_cm=19 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
	figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
	figsize_y_cm=12
	figsize_y_inches=figsize_y_cm/2.54

	#define number of subplots.
	ncols=3
	nrows=2

	#Set up fig and ax
	fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
	#axarr[row][col]

	#Adjust subplots
	left   =  0.08  # the left side of the subplots of the figure
	right  =  0.97    # the right side of the subplots of the figure
	bottom =  0.13    # the bottom of the subplots of the figure
	top    =  0.85    # the top of the subplots of the figure
	wspace =  .20     # the amount of width reserved for blank space between subplots
	hspace =  .23    # the amount of height reserved for white space between subplots

	# This function adjusts the subplots using the parameters defined earlier
	plt.subplots_adjust(
	left    =  left, 
	bottom  =  bottom, 
	right   =  right, 
	top     =  top, 
	wspace  =  wspace, 
	hspace  =  hspace
	)



	#Create storage
	storage_dict_obs={}
	storage_dict_pred={}

	col=0
	for mode in mode_list:
		row=0
		for value_type in value_type_list:
			print('\nWe are creating the cumulative {0} value graph for {1} of for mode {2} and MSOA: {3}'.format(value_type, metric, mode,MSOA))

			#Set the name of the rows we want to use:
			col_to_plot_obs='Tobs_{}'.format(mode)
			col_to_plot_pred='Tpred_{}'.format(mode)


			#Get the data we need from the helper functions
			if value_type=='absolute':
				storage_dict_obs=msoa_df_creator_cumsum_abs_value(df_input[[col_to_plot_obs]],cut_off=True) #we do [[]] here so it becomes a df, which is the required input for our helper function creator.
				storage_dict_pred=msoa_df_creator_cumsum_abs_value(df_input[[col_to_plot_pred]],cut_off=True)
			elif value_type=='percentage':
				storage_dict_obs=msoa_df_creator_cumsum_percentage(df_input[[col_to_plot_obs]],cut_off=True)
				storage_dict_pred=msoa_df_creator_cumsum_percentage(df_input[[col_to_plot_pred]],cut_off=True)
			

			#Get the cumulative, ordered data into a numpy array using values function. We will use this array to plot.
			if value_type=='absolute':
				val_obs=storage_dict_obs[col_to_plot_obs]['retained_df']['cumsum_absvalues'].values
				val_pred=storage_dict_pred[col_to_plot_pred]['retained_df']['cumsum_absvalues'].values
			elif value_type=='percentage':
				val_obs=storage_dict_obs[col_to_plot_obs]['retained_df']['cumsum_percentage'].values
				val_pred=storage_dict_pred[col_to_plot_pred]['retained_df']['cumsum_percentage'].values
				#Get percentages.
				val_obs=val_obs*100
				val_pred=val_pred*100

			#Insert a zero value so the line can start from 0,0.	
			val_obs=np.insert(val_obs, 0, 0)
			val_pred=np.insert(val_pred, 0, 0)

			#Create rank values for x_axis
			x_val_obs=list(range(0,len(val_obs)))
			x_val_pred=list(range(0,len(val_obs)))

			#Plot on currently active axis.
			axarr[row][col].plot(val_obs,color=color_dict_mode[mode], alpha=0.75,label="observed")
			axarr[row][col].plot(val_pred,ls='--',color=color_dict_mode[mode], alpha=0.5,label="predicted")

			#Helpline
			# slope=max(val_obs)/max(x_val_obs)
			# yhelp=[i *slope for i in x_val_obs] 
			# help_line=axarr[row][col].plot(x_val_obs,yhelp,ls='--',lw=1,color='.4',alpha=0.6)

			row=row+1
		col=col+1

	#Set legends for some subplots
	axarr[1][0].legend(loc='lower right',prop={'size': 7})
	axarr[1][1].legend(loc='lower right',prop={'size': 7})
	axarr[1][2].legend(loc='lower right',prop={'size': 7})

	#Set titles
	title1=('Cumulative sum of number of trips by ranked destinations for \n MSOA {0}'.format(MSOA))
	fig.suptitle(title1, y = 0.98, fontsize=12)

	axarr[0][0].set_title('By car',fontsize=10)
	axarr[0][1].set_title('By bus',fontsize=10)
	axarr[0][2].set_title('By rail',fontsize=10)

	#Set labels
	axarr[1][1].set_xlabel('Rank of destination MSOA (by contribution)',fontsize=9)
	axarr[0][0].set_ylabel('{0}'.format(label_titles[value_type_list[0]]),fontsize=9)
	axarr[1][0].set_ylabel('{0}'.format(label_titles[value_type_list[1]]),fontsize=9)

	#All subplots
	for axrow in axarr:
		for ax in axrow:

			# Set ticks parameters
			ax.tick_params(axis = 'x', which = 'major', length=2, labelsize = 8) 
			ax.tick_params(axis = 'y', which = 'major', length=2, labelsize = 8, direction='in') 

			#Set gridlines
			ax.grid(axis='y', color="0.85", linestyle='--', alpha=0.6, linewidth=0.5)
			ax.grid(axis='x', color="0.85", linestyle='--', alpha=0.6, linewidth=0.5)		

			# put the grid behind
			ax.set_axisbelow(True)

			#Make frame lighter and change line-width:
			for pos in ['top','bottom','left','right']:
				ax.spines[pos].set_linewidth(0.8)
				ax.spines[pos].set_color('0.6')

	#Delete y lables van sommige subplots wegens overbodig. 
	y_labels=['','','','','','','']
	axarr[1][1].set_yticklabels(y_labels)
	axarr[1][1].tick_params(axis = 'y', which = 'major', length=2, labelsize = 0)
	axarr[1][2].set_yticklabels(y_labels)
	axarr[1][2].tick_params(axis = 'y', which = 'major', length=2, labelsize = 0)

	#save or show
	# plt.show()

	if home_to_work:
		outputname='Cumsum_three_modes/{0}_cumsum_three_modes_obs_vs_predicted_home_to_work.png'.format(MSOA)	
	if work_to_home:
		outputname='Cumsum_three_modes/{0}_cumsum_three_modes_obs_vs_predicted_work_to_home.png'.format(MSOA)

	output=foldername_output+outputname
	plt.savefig(output)
	plt.clf() #clear the entire figure. Since we define this one outside the loop, we don't want that.
	print ('Figure saved')



################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################
################################################################################################################
################################################################################################################
#######################################     Development zone    ################################################
################################################################################################################
################################################################################################################


########################################################
#5. Investigate filters and their effect on signatures per MSOA
########################################################

############################
#5.1 Define some filter help functions
############################
'''
def msoa_filter_absolute(df,filter_threshold):
	"""This function filters a df column-wise based on a filter-threshold is an absolute value (int or float) 
	The output of the filter is a dict with, for each column, a list of the ids that passed the filter
	and the retained percentage of the values that are associated with the cells."""

	#Setting up intermediate storage
	dict_filter={}
	for col in df.columns:
		dict_filter[col]={}
	colcounter=0

	print('\nWe are setting up the filtering based on absolute value > {0} '.format(filter_threshold))

	for col in df.columns:
		#Print progress
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Set evaluation thing
		df_subset['evaluation']=df_subset[col]

		#Caclulate percentual contribution of all pairs
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Apply filter.
		df_subset_selection=df_subset.query("{0} > {1}".format(col,filter_threshold))
		
		#Create a filter dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter[col]['filtered_list']=df_subset_selection.index.to_list() 

		#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
		dict_filter[col]['retained_number_of_msoas']=df_subset_selection.shape[0] 

		#Create a filter dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter[col]['retained_percentage_sum']=np.round(df_subset_selection['percentage'].sum()*100,decimals=1)

		#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
		dict_filter[col]['retained_number_of_commuters']=df_subset_selection[col].sum()

	return dict_filter


df_to_plot=msoa_filter_absolute(df_input1,10)
'''

'''
def msoa_filter_percentage(df,filter_threshold):
	"""This function filters a df column-wise based on a filter-threshold is a percentage (between 0 and 1) 
	The output of the filter is a dict with, for each column, a list of the ids that passed the filter
	and the retained percentage of the values that are associated with the cells."""

	#Input check
	if filter_threshold >1 and absolute==False:
		print('\nERROR: The value for filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')
	elif filter_threshold <0 and absolute==False:
		print('\nERROR: The value for filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')

	#Setting up intermediate storage
	dict_filter={}
	for col in df.columns:
		dict_filter[col]={}
	colcounter=0

	print('\nWe are setting up the filtering based on percentage > {0} '.format(filter_threshold))

	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Apply filter.
		df_subset_selection=df_subset.query("percentage > {1}".format(col,filter_threshold))
		
		#Create a filter dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter[col]['filtered_list']=df_subset_selection.index.to_list() 

		#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
		dict_filter[col]['retained_number_of_msoas']=df_subset_selection.shape[0] 

		#Create a filter dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter[col]['retained_percentage_sum']=np.round(df_subset_selection['percentage'].sum()*100,decimals=1)

		#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
		dict_filter[col]['retained_number_of_commuters']=df_subset_selection[col].sum()

	return dict_filter


def msoa_df_creator_cumsum_abs_value(df, cut_off=False):
	"""This function calculates the cumulative sum of the values in a dataframe for each column
	The output of the filter is a dict with, for each column, a dataframe containing the values, percentage, and cumsum.
	If cut_off=True, then the MSOA pairs for which no commuters where observed will be cut off from the dataframe."""

	if cut_off:
		print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
	else:
		print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')

	#Setting up intermediate storage
	dict_out={}
	for col in df.columns:
		dict_out[col]={}
	colcounter=0

	print('\nWe are calculating the cumsum absolute values for all the MSOAs')
	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by=col, ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum_absvalues']=df_subset_sorted[col].cumsum()

		if cut_off==True:
			#print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
			
			#Cut off the pairs that do not contribute.	
			df_subset_sorted_cut_off=df_subset_sorted.loc[(df_subset_sorted[col]> 0)]
			
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted_cut_off

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted_cut_off.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted_cut_off[col].sum()
		
		else:
			#print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted[col].sum()
	
	return dict_out




def msoa_df_creator_cumsum_percentage(df, cut_off=False):
	"""This function calculates the cumulative sum of the percentage of values in a dataframe for each column
	The output of the filter is a dict with, for each column, a dataframe containing the values, percentage, and cumsum.
	If cut_off=True, then the MSOA pairs for which no commuters where observed will be cut off from the dataframe."""

	if cut_off:
		print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
	else:
		print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')

	#Setting up intermediate storage
	dict_out={}
	for col in df.columns:
		dict_out[col]={}
	colcounter=0

	print('\nWe are calculating the cumsum percentage for all the MSOAs')
	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by='percentage', ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum_percentage']=df_subset_sorted['percentage'].cumsum()

		if cut_off==True:
			#print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
			
			#Cut off the pairs that do not contribute.	
			df_subset_sorted_cut_off=df_subset_sorted.loc[(df_subset_sorted['percentage']> 0)]
			
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted_cut_off

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted_cut_off.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted_cut_off[col].sum()
		
		else:
			#print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted[col].sum()
	
	return dict_out


def msoa_filter_cumsum_percentage(df,cumulative_filter_threshold):
	"""This function filters a df column-wise based on a filter-threshold. 
	   The filter tresholds is the cumulative sum of the percentages (between 0 and 1) based on a sorted list. 
	   In other words, it filters the MSOA pairs that contribute most to a cumsum that is under a threshold.  
	   The output of the filter is a dict with, for each column, a list of the ids that passed the filter
	   the number of retained MSOAs and retained percentage of the values that are associated with these pairs (has to be the same as the filter threshold)."""


	#Input check
	if cumulative_filter_threshold >1:
		print('\nERROR: The value for cumulative_filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')
	elif cumulative_filter_threshold <0:
		print('\nERROR: The value for cumulative_filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')

	#Setting up intermediate storage
	dict_filter={}
	for col in df.columns:
		dict_filter[col]={}
	dict_filter_retained_percentage={}
	colcounter=0

	print('\nWe are setting up the filtering based on cumsum < {0} '.format(cumulative_filter_threshold))

	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by='percentage', ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum']=df_subset_sorted['percentage'].cumsum()

		#Apply filter.
		df_subset_sorted_selection=df_subset_sorted.query("cumsum < {0}".format(cumulative_filter_threshold))
		
		#Create a filter dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter[col]['filtered_list']=df_subset_sorted_selection.index.to_list() 

		#Create a filter dict with keys being col names and values being the number of pertained MSOA pairs.
		dict_filter[col]['retained_number_of_msoas']=df_subset_sorted_selection.shape[0] 

		#Create a filter dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter[col]['retained_percentage_sum']=np.round(df_subset_sorted_selection['percentage'].sum()*100,decimals=1)

		#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
		dict_filter[col]['retained_number_of_commuters']=df_subset_sorted_selection[col].sum()

	
	return dict_filter

'''

'''
#df_to_plot cases for the helper functions.
df=df_Tobs_rail.copy()
a = msoa_filter_absolute(df,20) 
b = msoa_filter_percentage(df,0.20) 
c = msoa_df_creator_cumsum_value(df,cut_off=True)
d = msoa_df_creator_cumsum_percentage(df,cut_off=True)
e = msoa_filter_cumsum_percentage(df,0.40)
'''
'''
df=df_Tobs_rail.copy()
c = msoa_df_creator_cumsum_abs_value(df,cut_off=True)
c['E02000010']

'''

















########################################################
#1. Read in inputfiles
########################################################
'''
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

#Calculated shordf_to_plot routes by Quant for OD between MSOAS. They serve as input for Quant
#Values in these files are 1/time(minutes)
inputfile_dij_car= foldername_input + 'Quant_forMaarten/dijRoad_min.csv' 
inputfile_dij_bus= foldername_input + 'Quant_forMaarten/dijBus_min.csv' 
inputfile_dij_rail= foldername_input + 'Quant_forMaarten/dijRail_min.csv'


#Shapefile with MSOA locations
inputfile_shapefile_MSOA= foldername_input + 'shapefiles/EPSG7405_MSOA_2011/EPSG7405_MSOA_2011.shp'


########################################################
#2. Read in and pre-process data
########################################################

# Our aim is to explore the information available per MSOA so that we can make informed 
# decision on what filters, or features to use best. 

############################
#2.1 Read in data
############################

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


######################
#2.1.2 Copy the structure of the Dij files to be used later. 
######################

# We create an empty dataframe that has the same structure as the dij dataframe so it can be transferred to the Tobs files
# since those don't have a structure but Roberto told me their structure was the same. 
if car:
	df_structure_storage=pd.DataFrame().reindex_like(df_dij_car)
elif bus:
	df_structure_storage=pd.DataFrame().reindex_like(df_dij_bus)
elif rail:
	df_structure_storage=pd.DataFrame().reindex_like(df_dij_rail)


######################
#2.1.3 Read in the Tobs files 
######################
# The Tobs files don't have the headers and columns, but Roberto told us it was the same as the ones in DIJ so we transfer them.


while car:
	print("Reading in the Tobs file for car: " + '\n' + str(inputfile_Tobs_car))
	df_Tobs_car=pd.read_csv(inputfile_Tobs_car, header=None, sep=',', lineterminator='\n') 

	df_Tobs_car.columns = list(df_structure_storage.columns)
	df_Tobs_car.set_index(df_structure_storage.index,inplace=True)

	print ('\n The number of rows and columns in the Tobs_car dataframe are:')
	print(df_Tobs_car.shape)

	print ('\n The first five lines of the Tobs_car dataframe look like this:')
	print(df_Tobs_car.head())

	break

while bus:
	print("Reading in the Tobs file for bus: " + '\n' + str(inputfile_Tobs_bus))
	df_Tobs_bus=pd.read_csv(inputfile_Tobs_bus, header=None, sep=',', lineterminator='\n') 

	df_Tobs_bus.columns = list(df_structure_storage.columns)
	df_Tobs_bus.set_index(df_structure_storage.index,inplace=True)

	print ('\n The number of rows and columns in the Tobs_bus dataframe are:')
	print(df_Tobs_bus.shape)

	print ('\n The first five lines of the Tobs_bus dataframe look like this:')
	print(df_Tobs_bus.head())

	break

while rail:
	print("Reading in the Tobs file for rail: " + '\n' + str(inputfile_Tobs_rail))
	df_Tobs_rail=pd.read_csv(inputfile_Tobs_rail, header=None, sep=',', lineterminator='\n') 

	df_Tobs_rail.columns = list(df_structure_storage.columns)
	df_Tobs_rail.set_index(df_structure_storage.index,inplace=True)

	print ('\n The number of rows and columns in the Tobs_rail dataframe are:')
	print(df_Tobs_rail.shape)

	print ('\n The first five lines of the Tobs_rail dataframe look like this:')
	print(df_Tobs_rail.head())

	break




########################################################
#3. Create a minutes spent on mode matrix
########################################################

############################
#3.1 Create a minutes spent on mode matrix
############################

# We create a table which tells us the minutes spent for each trip, which = number of obs trips * the shordf_to_plot route distance (in minutes)

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
#4. Order input files in dict for easy access later on. 
########################################################

print ('This part is still in developing at 10 march 2020')

input_dict={}

while car:
	input_dict['car']={}
	while trips:
		input_dict['car']['trips']=df_Tobs_car
		break
	while shordf_to_plot_route:
		input_dict['car']['shordf_to_plot_route']=df_dij_car
		break
	while time_spent:
		input_dict['car']['time_spent']=df_time_spent_car
		break
	break

while bus:
	input_dict['bus']={}
	while trips:
		input_dict['bus']['trips']=df_Tobs_bus
		break
	while shordf_to_plot_route:
		input_dict['bus']['shordf_to_plot_route']=df_dij_bus
		break
	while time_spent:
		input_dict['bus']['time_spent']=df_time_spent_bus
		break
	break

while rail:
	input_dict['rail']={}
	while trips:
		input_dict['rail']['trips']=df_Tobs_rail
		break
	while shordf_to_plot_route:
		input_dict['rail']['shordf_to_plot_route']=df_dij_rail
		break
	while time_spent:
		input_dict['rail']['time_spent']=df_time_spent_rail
		break
	break
'''

########################################################
#5. Investigate filters and their effect on signatures per MSOA
########################################################


########################################################
# QUICK SAVE OF A SUBSET FOR DEVELOPING PURPOSES
########################################################
'''
#Write out to csv.
df_time_spent_rail[['E02000001', 'E02000002', 'E02000003', 'E02000004', 'E02000005','E02000007', 'E02000008', 'E02000009', 'E02000010']].to_csv('/Users/Metti_Hoof/Desktop/Quant Developing/data/df_time_spent_rail_subset.csv')
df_Tobs_rail[['E02000001', 'E02000002', 'E02000003', 'E02000004', 'E02000005','E02000007', 'E02000008', 'E02000009', 'E02000010']].to_csv('/Users/Metti_Hoof/Desktop/Quant Developing/data/df_Tobs_rail_subset.csv')
df_dij_rail[['E02000001', 'E02000002', 'E02000003', 'E02000004', 'E02000005','E02000007', 'E02000008', 'E02000009', 'E02000010']].to_csv('/Users/Metti_Hoof/Desktop/Quant Developing/data/df_dij_rail_subset.csv')


'''
'''
#Read in stored subset
print('\nWe are reading in the stored subsets for developing purposes')

df_time_spent_rail=pd.read_csv('/Users/Metti_Hoof/Desktop/Quant Developing/data/df_time_spent_rail_subset.csv',sep=',', lineterminator='\n', header=0) 
df_Tobs_rail=pd.read_csv('/Users/Metti_Hoof/Desktop/Quant Developing/data/df_Tobs_rail_subset.csv',sep=',', lineterminator='\n', header=0) 
df_dij_rail=pd.read_csv('/Users/Metti_Hoof/Desktop/Quant Developing/data/df_dij_rail_subset.csv',sep=',', lineterminator='\n', header=0) 

df_time_spent_rail=df_time_spent_rail.set_index('MSOA')
df_Tobs_rail=df_Tobs_rail.set_index('MSOA')
df_dij_rail=df_dij_rail.set_index('MSOA')


############################
#5.1 Define some filter help functions
############################
print('\nWe start filtering but BE CAREFULL! Filtering is only coded for the HOME-WORK direction')

def msoa_filter_absolute(df,filter_threshold):
	"""This function filters a df column-wise based on a filter-threshold is an absolute value (int or float) 
	The output of the filter is a dict with, for each column, a list of the ids that passed the filter
	and the retained percentage of the values that are associated with the cells."""

	#Setting up intermediate storage
	dict_filter={}
	for col in df.columns:
		dict_filter[col]={}
	colcounter=0

	print('\nWe are setting up the filtering based on absolute value > {0} '.format(filter_threshold))

	for col in df.columns:
		#Print progress
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Set evaluation thing
		df_subset['evaluation']=df_subset[col]

		#Caclulate percentual contribution of all pairs
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Apply filter.
		df_subset_selection=df_subset.query("{0} > {1}".format(col,filter_threshold))
		
		#Create a filter dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter[col]['filtered_list']=df_subset_selection.index.to_list() 

		#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
		dict_filter[col]['retained_number_of_msoas']=df_subset_selection.shape[0] 

		#Create a filter dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter[col]['retained_percentage_sum']=np.round(df_subset_selection['percentage'].sum()*100,decimals=1)

		#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
		dict_filter[col]['retained_number_of_commuters']=df_subset_selection[col].sum()

	return dict_filter


def msoa_filter_percentage(df,filter_threshold):
	"""This function filters a df column-wise based on a filter-threshold is a percentage (between 0 and 1) 
	The output of the filter is a dict with, for each column, a list of the ids that passed the filter
	and the retained percentage of the values that are associated with the cells."""

	#Input check
	if filter_threshold >1 and absolute==False:
		print('\nERROR: The value for filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')
	elif filter_threshold <0 and absolute==False:
		print('\nERROR: The value for filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')

	#Setting up intermediate storage
	dict_filter={}
	for col in df.columns:
		dict_filter[col]={}
	colcounter=0

	print('\nWe are setting up the filtering based on percentage > {0} '.format(filter_threshold))

	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Apply filter.
		df_subset_selection=df_subset.query("percentage > {1}".format(col,filter_threshold))
		
		#Create a filter dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter[col]['filtered_list']=df_subset_selection.index.to_list() 

		#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
		dict_filter[col]['retained_number_of_msoas']=df_subset_selection.shape[0] 

		#Create a filter dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter[col]['retained_percentage_sum']=np.round(df_subset_selection['percentage'].sum()*100,decimals=1)

		#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
		dict_filter[col]['retained_number_of_commuters']=df_subset_selection[col].sum()

	return dict_filter


def msoa_df_creator_cumsum_abs_value(df, cut_off=False):
	"""This function calculates the cumulative sum of the values in a dataframe for each column
	The output of the filter is a dict with, for each column, a dataframe containing the values, percentage, and cumsum.
	If cut_off=True, then the MSOA pairs for which no commuters where observed will be cut off from the dataframe."""

	if cut_off:
		print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
	else:
		print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')

	#Setting up intermediate storage
	dict_out={}
	for col in df.columns:
		dict_out[col]={}
	colcounter=0

	print('\nWe are calculating the cumsum absolute values for all the MSOAs')
	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by=col, ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum_absvalues']=df_subset_sorted[col].cumsum()

		if cut_off==True:
			#print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
			
			#Cut off the pairs that do not contribute.	
			df_subset_sorted_cut_off=df_subset_sorted.loc[(df_subset_sorted[col]> 0)]
			
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted_cut_off

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted_cut_off.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted_cut_off[col].sum()
		
		else:
			#print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted[col].sum()
	
	return dict_out




def msoa_df_creator_cumsum_percentage(df, cut_off=False):
	"""This function calculates the cumulative sum of the percentage of values in a dataframe for each column
	The output of the filter is a dict with, for each column, a dataframe containing the values, percentage, and cumsum.
	If cut_off=True, then the MSOA pairs for which no commuters where observed will be cut off from the dataframe."""

	if cut_off:
		print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
	else:
		print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')

	#Setting up intermediate storage
	dict_out={}
	for col in df.columns:
		dict_out[col]={}
	colcounter=0

	print('\nWe are calculating the cumsum percentage for all the MSOAs')
	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by='percentage', ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum_percentage']=df_subset_sorted['percentage'].cumsum()

		if cut_off==True:
			#print('\nYou have opted for a cut-off, the pairs that do not contribute to the cumulative sum will be discarded')
			
			#Cut off the pairs that do not contribute.	
			df_subset_sorted_cut_off=df_subset_sorted.loc[(df_subset_sorted['percentage']> 0)]
			
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted_cut_off

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted_cut_off.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted_cut_off[col].sum()
		
		else:
			#print('\nYou did not opt for a cut-off, all pairs will be included in the dataframe')
			#Create a filter dict with keys being col names and values being a dataframe with, for each MSOA the MSOA pairs
			# their percentual contribution and the cumulative sum of contributions starting from the most contributing
			dict_out[col]['retained_df']=df_subset_sorted

			#Create a filter dict with keys being col names and values being the number of pertained MSOA pairst.
			dict_out[col]['retained_number_of_msoas']=df_subset_sorted.shape[0] 

			#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
			dict_out[col]['retained_number_of_commuters']=df_subset_sorted[col].sum()
	
	return dict_out


def msoa_filter_cumsum_percentage(df,cumulative_filter_threshold):
	"""This function filters a df column-wise based on a filter-threshold. 
	   The filter tresholds is the cumulative sum of the percentages (between 0 and 1) based on a sorted list. 
	   In other words, it filters the MSOA pairs that contribute most to a cumsum that is under a threshold.  
	   The output of the filter is a dict with, for each column, a list of the ids that passed the filter
	   the number of retained MSOAs and retained percentage of the values that are associated with these pairs (has to be the same as the filter threshold)."""


	#Input check
	if cumulative_filter_threshold >1:
		print('\nERROR: The value for cumulative_filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')
	elif cumulative_filter_threshold <0:
		print('\nERROR: The value for cumulative_filter_threshold was not passed correctly. You will be using percentages, please choose a value between 0 and 1')

	#Setting up intermediate storage
	dict_filter={}
	for col in df.columns:
		dict_filter[col]={}
	dict_filter_retained_percentage={}
	colcounter=0

	print('\nWe are setting up the filtering based on cumsum < {0} '.format(cumulative_filter_threshold))

	for col in df.columns:
		#Print progress
		if colcounter%100==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df.columns)) + ' columns to process')
		colcounter=colcounter+1

		#Evaluate one col only
		df_subset=df[[col]].copy()

		#Caclulate percentual contribution of all
		df_subset['percentage']=df_subset[col]/df_subset[col].sum()

		#Sort by most contributing
		df_subset_sorted=df_subset.sort_values(by='percentage', ascending=False)

		#Calculate the cumulative sum of the the contributors, starting from the most contributing
		df_subset_sorted['cumsum']=df_subset_sorted['percentage'].cumsum()

		#Apply filter.
		df_subset_sorted_selection=df_subset_sorted.query("cumsum < {0}".format(cumulative_filter_threshold))
		
		#Create a filter dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter[col]['filtered_list']=df_subset_sorted_selection.index.to_list() 

		#Create a filter dict with keys being col names and values being the number of pertained MSOA pairs.
		dict_filter[col]['retained_number_of_msoas']=df_subset_sorted_selection.shape[0] 

		#Create a filter dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter[col]['retained_percentage_sum']=np.round(df_subset_sorted_selection['percentage'].sum()*100,decimals=1)

		#Create a filter dict with keys being col names and values number of commuters that are pertained by the filter
		dict_filter[col]['retained_number_of_commuters']=df_subset_sorted_selection[col].sum()

	
	return dict_filter

'''

'''
#df_to_plot cases for the helper functions.
df=df_Tobs_rail.copy()
a = msoa_filter_absolute(df,20) 
b = msoa_filter_percentage(df,0.20) 
c = msoa_df_creator_cumsum_value(df,cut_off=True)
d = msoa_df_creator_cumsum_percentage(df,cut_off=True)
e = msoa_filter_cumsum_percentage(df,0.40)
'''
'''
df=df_Tobs_rail.copy()
c = msoa_df_creator_cumsum_abs_value(df,cut_off=True)
c['E02000010']

'''


############################
#5.2 Create visuals to explore effects of filters
############################
'''

########################################################
# QUICK CREATION OF INPUTDICT FOR DEVELOPING PURPOSES. WE DO THIS IN PART 4 NORMALLY
########################################################
input_dict={}
while rail:
	input_dict['rail']={}
	while trips:
		input_dict['rail']['trips']=df_Tobs_rail
		break
	while shordf_to_plot_route:
		input_dict['rail']['shordf_to_plot_route']=df_dij_rail
		break
	while time_spent:
		input_dict['rail']['time_spent']=df_time_spent_rail
		break
	break


'''
############################
#5.2.1 Histogram of number of commuters and number of MSOA's people commute to from each MSOA per mode
############################
'''
#Create a histogram showing the distribution of the amount of neighbouring MSOAs that have commuters for all MSOAs 
#or the distribution of the amount of commuters

############# Developing ###############
mode_list=['rail']
metric_list=['trips']
############# Developing ###############

#Setting up figure specifications 
figsize_x_cm=12 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
figsize_y_cm=5
figsize_y_inches=figsize_y_cm/2.54
#define number of subplots.
ncols=1
nrows=1

#Set up fig and ax
fig, ax = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
#axarr[row][col] when ncols or nrows is larger than 1

#Adjust subplots parameters
left   =  0.15  # the left side of the subplots of the figure
right  =  0.90    # the right side of the subplots of the figure
bottom =  0.25    # the bottom of the subplots of the figure
top    =  0.85    # the top of the subplots of the figure
wspace =  .0     # the amount of width reserved for blank space between subplots
hspace =  .0    # the amount of height reserved for white space between subplots

# This function actually adjusts the subplots using the above paramters
plt.subplots_adjust(
left    =  left, 
bottom  =  bottom, 
right   =  right, 
top     =  top, 
wspace  =  wspace, 
hspace  =  hspace
)


#Create storage
storage_dict={}

indicator_list=['retained_number_of_msoas','retained_number_of_commuters']


for indicator in indicator_list:
	for mode in mode_list:
		#Print out current situation
		if indicator=='retained_number_of_commuters':
			print('\nWe are creating a histogram of number of commuters per MSOA for mode {0}'.format(mode))
		elif indicator=='retained_number_of_msoas':
			print('\nWe are creating a histogram of the number of different MSOAS that have trips for mode {0} for each MSOA in the dataset'.format(mode))

		#Create storage
		storage_list=[]
		
		#Use function to get a dict with, per MSOA, the retained msoas that do not have zero commuters (the cut off option) 
		in_between_dict=msoa_df_creator_cumsum_percentage(input_dict[mode]['trips'],cut_off=True)

		#Storage_list is filled with the retained number of msoas for all msoas.
		for key in in_between_dict.keys():
			storage_list.append(in_between_dict[key][indicator])
		#Storage is filled
		storage_dict[mode]=storage_list


	#Create a histogram for each mode 
	for mode in mode_list:


		#Set list to numpy array
		a=np.array(storage_dict[mode])

		#Define weights so that sum of bars = 1
		weighta=np.ones_like(a)/float(len(a))

		#Get color:
		#bmap = brewer2mpl.get_map('Blues', 'sequential', 3)
		#colorbrew=bmap.hex_colors

		n1, bins1, patches1 = ax.hist(a, bins=50, weights=weighta, facecolor='blue', alpha=0.75)

		#Set titles
		title1='Histogram of {0} by {1}'.format(subplot_titles[indicator],mode)
		ax.set_title(title1, y = 0.98, fontsize=10)


		#Set x limits
		max_x=max(a)
		ax.set_xlim(0,max_x)

		#Set label titles
		ax.set_xlabel(label_titles[indicator],fontsize=9)
		ax.set_ylabel('Probability',fontsize=9)

		# Set grid
		ax.grid(which = 'major', alpha = 0.4,ls=':')

		# put the grid behind
		ax.set_axisbelow(True)
		
		# Set ticks parameters
		ax.tick_params(axis = 'x', which = 'major', length=2, labelsize = 8) 
		ax.tick_params(axis = 'y', which = 'major', length=2, labelsize = 8) 
		
		# Make frame lighter and change line-width:
		for pos in ['top','bottom','left','right']:
			ax.spines[pos].set_linewidth(0.5)
			ax.spines[pos].set_color('0.6')


		#save or show
		#plt.show()
		
		#save or show
		outputname='Histogram/Histogram_{0}_by_{1}_for_each_MSOA.png'.format(indicator,mode)
		output=foldername_output+outputname
		plt.savefig(output)
		plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
		#plt.clf() #clear the entire figure. Since we define this one outside the loop, we don't want that.
		print ('Figure saved')

'''

############################
#5.2.1 Plot of cumulative percentage of individual MSOAs
############################
'''
#Create a plot showing the cumulative percentage or absolute values of trips, spent_time or shordf_to_plot route per MSOA by transport mode. 

value_type_list=['absolute','percentage'] #choose one or both

############# Developing ###############
mode_list=['rail']
metric_list=['trips']
############# Developing ###############

#Setting up figure specifications 
figsize_x_cm=12 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
figsize_y_cm=10
figsize_y_inches=figsize_y_cm/2.54

#define number of subplots.
ncols=1
nrows=1

#Set up fig and ax
fig, ax = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
#axarr[row][col]

#Adjust subplots
left   =  0.15  # the left side of the subplots of the figure
right  =  0.90    # the right side of the subplots of the figure
bottom =  0.25    # the bottom of the subplots of the figure
top    =  0.85    # the top of the subplots of the figure
wspace =  .0     # the amount of width reserved for blank space between subplots
hspace =  .0    # the amount of height reserved for white space between subplots

# This function adjusts the subplots using the parameters defined earlier
plt.subplots_adjust(
left    =  left, 
bottom  =  bottom, 
right   =  right, 
top     =  top, 
wspace  =  wspace, 
hspace  =  hspace
)


#Create storage
storage_dict={}

for metric in metric_list:

	for mode in mode_list:

		for value_type in value_type_list:

			print('\nWe are creating the cumulative {0} value graph for {1} of each MSOA for mode {2}'.format(value_type, metric, mode))
			
			#Get the data we need from the helper functions

			if value_type=='absolute':
				storage_dict=msoa_df_creator_cumsum_abs_value(input_dict[mode][metric],cut_off=True)
			elif value_type=='percentage':
				storage_dict=msoa_df_creator_cumsum_percentage(input_dict[mode][metric],cut_off=True)

			print('\nWe now start plotting for each individual MSOA. This may take a while')
			#Each key in the storage dict corresponds to one MSOA.
			for MSOA in storage_dict.keys():

				#Get the cumulative, ordered data into a numpy array using values function. We will use this array to plot.
				if value_type=='absolute':
					a=storage_dict[MSOA]['retained_df']['cumsum_absvalues'].values
				elif value_type=='percentage':
					a=storage_dict[MSOA]['retained_df']['cumsum_percentage'].values
					#Get percentages.
					a=a*100


				#Insert a zero value so the line can start from 0,0.	
				a=np.insert(a, 0, 0)
				#Create rank values for x_axis
				x_a=list(range(0,len(a)))

				#Get color:
				#bmap = brewer2mpl.get_map('Blues', 'sequential', 3)
				#colorbrew=bmap.hex_colors

				#Plot on currently active axis.
				ax.plot(a,color='blue', alpha=0.75)

				#Helpline
				slope=max(a)/max(x_a)
				yhelp=[i *slope for i in x_a] 
				help_line=ax.plot(x_a,yhelp,ls='--',lw=1,color='.4',alpha=0.6)

				#Set titles
				title1='{0} of {1} by {2}'.format(subplot_titles[value_type],subplot_titles[metric],mode)
				ax.set_title(title1, y = 0.98, fontsize=10)

				#Set y limits
				#ax.set_ylim(0,1)

				#Set label titles
				ax.set_xlabel('Rank of destination MSOA (by contribution)',fontsize=9)
				ax.set_ylabel('{0}'.format(label_titles[value_type]),fontsize=9)

				# Set grid
				ax.grid(which = 'major', alpha = 0.4,ls=':')

				# put the grid behind
				ax.set_axisbelow(True)
				
				# Set ticks parameters
				ax.tick_params(axis = 'x', which = 'major', length=2, labelsize = 8) 
				ax.tick_params(axis = 'y', which = 'major', length=2, labelsize = 8) 
				
				# Make frame lighter and change line-width:
				for pos in ['top','bottom','left','right']:
					ax.spines[pos].set_linewidth(0.5)
					ax.spines[pos].set_color('0.6')


				#save or show
				#plt.show()
				
				#save or show
				outputname='Cumsum/{3}_cumsum_{0}_{1}_by_{2}.png'.format(value_type,metric,mode,MSOA)
				output=foldername_output+outputname
				plt.savefig(output)
				plt.cla() #clears the axis of the current figure. So the next one can be drawn without creating a new figure (and thus window)
				#plt.clf() #clear the entire figure. Since we define this one outside the loop, we don't want that.
				print ('Figure saved')


'''

############################################################################################
######################################               #######################################
####################################  Developing zone ######################################
#######################################             ########################################
############################################################################################




########################################################
#4. Summarize data per MSOA: aggregate per mode, 
	#for different directions, and with a filter for minimum share
########################################################
'''
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
directions=[] #select one or multiple directions.['home_to_work','work_to_home']
if home_to_work:
	directions.append('home_to_work') 
if work_to_home:
	directions.append('work_to_home')

metrices=[] #select one or multiple inputmatrices to aggregate['trips','shordf_to_plot_route','time_spent']
if trips:
	metrices.append('trips')
if shordf_to_plot_route:
	metrices.append('shordf_to_plot_route')
if time_spent:
	metrices.append('time_spent')


############################
#4.2 Aggregatiom
############################

######################
#4.2.1 Set up a filter based on the amount of trips and a hardcoded minimum percentage. 
######################

######### NOTE THAT THIS FILTER ONLY WORKS FOR THE HOME_TO_WORK DIRECTION ########

print('\nWe start filtering but BE CAREFULL! Filtering is only coded for the HOME-WORK direction')

if car:
	print('\nWe are setting up the filtering based on trip percentage > {0} for the car'.format(hardcoded_percentage_filter)) 
	dict_filter_car={}
	dict_filter_car_retained_percentage={}

	colcounter=0
	for col in df_Tobs_car.columns:
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df_Tobs_car.columns)) + ' columns to process')
		colcounter=colcounter+1

		df_subset_car=df_Tobs_car[[col]].copy()
		df_subset_car['percentage']=df_subset_car[col]/df_subset_car[col].sum()
		#Apply HARDCODED filter.
		df_subset_car_selection=df_subset_car.query("percentage > {0}".format(hardcoded_percentage_filter))
		
		#Create a filter_car dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter_car[col]=df_subset_car_selection.index.to_list() 
		#Create a filter_car dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter_car_retained_percentage[col]=np.round(df_subset_car_selection['percentage'].sum()*100,decimals=1)

if bus:
	print('\nWe are setting up the filtering based on trip percentage > {0} for the bus'.format(hardcoded_percentage_filter)) 
	dict_filter_bus={}
	dict_filter_bus_retained_percentage={}

	colcounter=0
	for col in df_Tobs_bus.columns:
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df_Tobs_bus.columns)) + ' columns to process')
		colcounter=colcounter+1

		df_subset_bus=df_Tobs_bus[[col]].copy()
		df_subset_bus['percentage']=df_subset_bus[col]/df_subset_bus[col].sum()
		#Apply HARDCODED filter.
		df_subset_bus_selection=df_subset_bus.query("percentage > {0}".format(hardcoded_percentage_filter))
		
		#Create a filter_bus dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter_bus[col]=df_subset_bus_selection.index.to_list() 
		#Create a filter_bus dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter_bus_retained_percentage[col]=np.round(df_subset_bus_selection['percentage'].sum()*100,decimals=1)


if rail:
	print('\nWe are setting up the filtering based on trip percentage > {0} for the rail'.format(hardcoded_percentage_filter)) 
	dict_filter_rail={}
	dict_filter_rail_retained_percentage={}
	
	colcounter=0
	for col in df_Tobs_rail.columns:
		if colcounter%1000==0:
			print('The code is at column number: ' + str(colcounter) + ' and there are ' + str(len(df_Tobs_rail.columns)) + ' columns to process')
		colcounter=colcounter+1

		df_subset_rail=df_Tobs_rail[[col]].copy()
		df_subset_rail['percentage']=df_subset_rail[col]/df_subset_rail[col].sum()
		#Apply HARDCODED filter.
		df_subset_rail_selection=df_subset_rail.query("percentage > {0}".format(hardcoded_percentage_filter))
		
		#Create a filter_rail dict with keys being col names and values being a list of all the MSOA that passed the percentage filter
		dict_filter_rail[col]=df_subset_rail_selection.index.to_list() 
		#Create a filter_rail dict with keys being col names and values being the summed percentage of trips that are pertained by the filter
		dict_filter_rail_retained_percentage[col]=np.round(df_subset_rail_selection['percentage'].sum()*100,decimals=1)


######################
#4.2.2 Set up structure of output, add information on retained percentage of filters to it already.
######################

# we copy the structure of the storage for one  MSOA column (E02000001) because this is necessary to copy
# we will delete this one column later on in the code. 
df_output=df_structure_storage['E02000001']

for mode in modes:
	retained_percentage_output_name='retained_percentage_of_trips_by_{0}_with_filter_{1}'.format(mode,hardcoded_percentage_filter)
	if mode=='car':
		df_to_store = pd.DataFrame(list(dict_filter_car_retained_percentage.items()), columns = ['MSOA',retained_percentage_output_name])
	elif mode=='bus':
		df_to_store = pd.DataFrame(list(dict_filter_bus_retained_percentage.items()), columns = ['MSOA',retained_percentage_output_name])
	elif mode=='rail':
		df_to_store = pd.DataFrame(list(dict_filter_rail_retained_percentage.items()), columns = ['MSOA',retained_percentage_output_name])
	
	df_output=df_to_store.join(df_output, how='right', on='MSOA')
	df_output=df_output.set_index('MSOA')

#Drop the 'E02000001' because we do not need it anymore
df_output=df_output.drop(columns=['E02000001']) 


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
				elif metric=='shordf_to_plot_route':
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
file_outputname= "df_output_{0}.csv".format(str(hardcoded_percentage_filter))
file_output=foldername_output + file_outputname

#Write out to csv.
df_output.to_csv(file_output)

'''
############################################################################################
######################################               #######################################
####################################  Developing zone ######################################
#######################################             ########################################
############################################################################################

'''
df_to_plot=df_Tobs_car.iloc[0:30, 0:30]
df_to_plot2=df_time_spent_car.iloc[0:30, 0:30]

filter_dict={}
for col in df_to_plot:
	df_tussen=df_to_plot[[col]].copy()
	df_tussen['percentage']=df_tussen[col]/df_tussen[col].sum()

	df_selectie=df_tussen.query("percentage > {0}".format(hardcoded_percentage_filter))[col]
	filter_dict[col]=df_selectie.index.to_list() 


for col in df_to_plot2:
	df_tussen2=df_to_plot2[col].copy()
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
