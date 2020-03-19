##############################################################################################
# -*- coding: utf-8 -*-
# Script to create a classification of signatures from commuting data and shortest paths
# that served as an input to Quant, or was an output from Quant.
# Written by Maarten Vanhoof, DECEMBER 2019
# Python 3
#
# The preparation of the input files is done in the file signatures_preparation.py
# The columnnames of the inputfiles are made up as follows:
# 'sum_{0}_{1}_{2}_{3}'.format(mode,metric,direction,hardcoded_percentage_filter)
# 'avg_{0}_{1}_{2}_{3}'.format(mode,metric,direction,hardcoded_percentage_filter)
# 'max_{0}_{1}_{2}_{3}'.format(mode,metric,direction,hardcoded_percentage_filter)
# 
# sum = aggregation per MSOA is done by summing up the metric
# avg = aggregation per MSOA is done by taking the mean of the metric
# max = aggregation per MSOA is done by taking the maximum value of the metric
#
# mode = either car, bus or rail
#
# metric = either trips, shortest_route (in minutes) or time spent (trips*shortest_route)
#
# direction = home_to_work; is the direction of the aggregation. work to home is not yet supported in the signatures_preparation.py
#
# hardcoded percentage filter = MSOA to MSOA connections that made up less than
#   x percent of the trips departing from an MSOA are not considered. 
#
#
##############################################################################################

print("The script is starting")


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
import matplotlib.colors as clr #For color adaptations in matplotlib
import ternary #For ternary plots

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

#Signatures per MSOA as prepared by signatures_preparation.py
inputfile_signatures = foldername_input + 'Signatures/df_output_001.csv'

#Shapefile with MSOA locations
inputfile_shapefile_MSOA = foldername_input + 'shapefiles/EPSG7405_MSOA_2011/EPSG7405_MSOA_2011.shp'


############################
#1.2. Read in data
############################

######################
#1.2.1 Signatures data
######################

#Read in csv in pandas
print("Reading in the files: " + inputfile_signatures)
df_signatures=pd.read_csv(inputfile_signatures,sep=',', lineterminator='\n')

#Print out basic statistics
print ('\n The number of rows and columns in the df_signatures dataframe are:')
print(df_signatures.shape)

print ('\n The first five lines of the df_signatures look like this:')
print(df_signatures.head())






df_sum_trips_shares=df_signatures[[	'MSOA',
									'sum_car_trips_home_to_work_0.01',
									'sum_bus_trips_home_to_work_0.01',
									'sum_rail_trips_home_to_work_0.01']]

df_sum_trips_shares = df_sum_trips_shares.set_index('MSOA')
df_sum_trips_shares = df_sum_trips_shares.div(df_sum_trips_shares.sum(axis=1), axis=0)

df_sum_trips_shares=df_sum_trips_shares.rename(
					columns={'sum_car_trips_home_to_work_0.01':'share_car_sum_trips',
							'sum_bus_trips_home_to_work_0.01':'share_bus_sum_trips',
							'sum_rail_trips_home_to_work_0.01':'share_rail_sum_trips'
							})

df_sum_trips_shares=np.round(df_sum_trips_shares*100)






######################
#1.2.2 MSOA Shapefile
######################

#Read in shapefile in geopandas
gp_MSOA=gpd.read_file(inputfile_shapefile_MSOA)

'''
#Plot map from shapefile
print ('\n We are now plotting the MSOAs of GB')
print(gp_MSOA.plot())
plt.show()
plt.close("all")
'''

#Have a look at the database behind the shapefile

print ('\n The number of rows and columns in the dij_car dataframe are:')
print(gp_MSOA.shape)

print ('\n The first five lines of the shapefile on MSOA look like this')
print(gp_MSOA.head())#Get first 10 lines to be printed



########################################################
#2. Explore signatures data by plotting. 
########################################################

############################
#2.0 Plot value distributions of columns.
############################

df_signatures[[	'MSOA',
				'avg_car_shortest_route_home_to_work_0.01',
				'retained_percentage_of_trips_by_car_with_filter_0.01',
				'avg_bus_shortest_route_home_to_work_0.01',
				'retained_percentage_of_trips_by_bus_with_filter_0.01',
				'avg_rail_shortest_route_home_to_work_0.01',
				'retained_percentage_of_trips_by_rail_with_filter_0.01']].hist()

plt.show()

############################
#2.1 Plot relations between elements of the signatures in a ternary plot.
############################

######################
#2.1.1 Prepare signatures data for ternary plot
######################
#Calculate shares.
#For sum of trips
df_sum_trips_shares=df_signatures[[	'MSOA',
									'sum_car_trips_home_to_work_0.01',
									'sum_bus_trips_home_to_work_0.01',
									'sum_rail_trips_home_to_work_0.01']]

df_sum_trips_shares = df_sum_trips_shares.set_index('MSOA')
df_sum_trips_shares = df_sum_trips_shares.div(df_sum_trips_shares.sum(axis=1), axis=0)

df_sum_trips_shares=df_sum_trips_shares.rename(
					columns={'sum_car_trips_home_to_work_0.01':'share_car_sum_trips',
							'sum_bus_trips_home_to_work_0.01':'share_bus_sum_trips',
							'sum_rail_trips_home_to_work_0.01':'share_rail_sum_trips'
							})

df_sum_trips_shares=np.round(df_sum_trips_shares*100)
 
#Prepare input for the ternary plot
list_sum_trips_shares_points_to_plot=[] 

# Iterate over each row 
for index, rows in df_sum_trips_shares.iterrows(): 
    # Create tuple for the current row 
    tuple_to_plot = (rows.share_rail_sum_trips, #bottom coordinate
    				rows.share_bus_sum_trips,   #right coordinate
    				rows.share_car_sum_trips) #left coordinate
    # append the list to the final list 
    list_sum_trips_shares_points_to_plot.append(tuple_to_plot) 
  


#Calculate shares.
#For sum of time spent.
df_sum_time_spent_shares=df_signatures[[	'MSOA',
									'sum_car_time_spent_home_to_work_0.01',
									'sum_bus_time_spent_home_to_work_0.01',
									'sum_rail_time_spent_home_to_work_0.01']]

df_sum_time_spent_shares = df_sum_time_spent_shares.set_index('MSOA')
df_sum_time_spent_shares = df_sum_time_spent_shares.div(df_sum_time_spent_shares.sum(axis=1), axis=0)

df_sum_time_spent_shares=df_sum_time_spent_shares.rename(
					columns={'sum_car_time_spent_home_to_work_0.01':'share_car_sum_time_spent',
							'sum_bus_time_spent_home_to_work_0.01':'share_bus_sum_time_spent',
							'sum_rail_time_spent_home_to_work_0.01':'share_rail_sum_time_spent'
							})

df_sum_time_spent_shares=np.round(df_sum_time_spent_shares*100)

#Prepare input for the ternary plot
list_sum_time_spent_shares_points_to_plot=[] 

# Iterate over each row 
for index, rows in df_sum_time_spent_shares.iterrows(): 
    # Create tuple for the current row 
    tuple_to_plot = (rows.share_rail_sum_time_spent, #bottom coordinate
    				rows.share_bus_sum_time_spent,   #right coordinate
    				rows.share_car_sum_time_spent) #left coordinate
    # append the list to the final list 
    list_sum_time_spent_shares_points_to_plot.append(tuple_to_plot) 



######################
#2.1.2 Plot ternary plot
######################

# Set up ternary plot.
## Boundary and Gridlines
scale = 100
figure, tax = ternary.figure(scale=scale)

#Get points to plot
tax.scatter(list_sum_trips_shares_points_to_plot, marker='.', color='b', s=2, label="All points")
#list_sum_trips_shares_points_to_plot
#list_sum_time_spent_shares_points_to_plot

# Draw Boundary and Gridlines
tax.boundary(linewidth=2.0)
tax.gridlines(color="black", multiple=10, linewidth=1) #primary gridlines
#tax.gridlines(color="blue", multiple=1, linewidth=0.5) #secondary gridlines

# Set Axis labels and Title
fontsize_title = 16
fontsize_axes = 12
offset_title=0.09
offset_axes=0.15

tax.set_title("Share of commuters", fontsize=fontsize_title)
tax.bottom_axis_label("by Rail", fontsize=fontsize_axes,offset=0.08)
tax.right_axis_label("by Bus", fontsize=fontsize_axes,offset=offset_axes)
tax.left_axis_label("by Car", fontsize=fontsize_axes,offset=offset_axes)

# Set ticks
offset_ticks=0.02
tax.ticks(axis='lbr', multiple=10, linewidth=1, offset=offset_ticks)
tax.get_axes().axis('off') #remove square around the figure

# Remove default Matplotlib Axes tickes
tax.clear_matplotlib_ticks()

#save or show
ternary.plt.show()

############################
#2.2 Map signatures
############################


######################
#Test the weird rail distance things so we can map out only the ones that are within reasonable avg time use. 
######################

#df_rail_selection=df_signatures[df_signatures['avg_rail_time_spent_home_to_work_0.01'].notnull() #get out nans
#			 & (df_signatures['avg_rail_time_spent_home_to_work_0.01'] <240)]  #travel time lower than 4 hours.

df_signatures['rail_selection']=np.where(df_signatures['avg_rail_time_spent_home_to_work_0.01']<240, 'Ok', 'Not ok')


df_signatures[['rail_selection','sum_rail_trips_home_to_work_0.01']].groupby(['rail_selection']).describe()

######################
#2.2.1 Join shapefile and signatures dataframe
######################

#We use the MSOA identiefier to merge shapefile and dataframe
gp_MSOA_signatures = gp_MSOA.merge(df_signatures, left_on='MSOA11CD', right_on='MSOA')

#Check whether dimensions are still the same after the merge. 
if gp_MSOA_signatures.shape[0] != df_signatures.shape[0]:
	print ('\n !!! The merge that was just performed has reduced the dimensions of your data')
	print (gp_MSOA.shape)
	print (df_signatures.shape)
else:
	print ('\nThe merge has not reduced your data, this is good\n')

######################
#2.2.2 Map signatures dataframe
######################

######################
# Individual metrics
######################

variable_to_plot='rail_selection' #'avg_rail_time_spent_home_to_work_0.01'

#Setup figure
figsize_x_cm=30 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
ratio_x_y=0.9 #0.9 for two rows, 
figsize_y_inches=figsize_x_inches*ratio_x_y 

fig, ax = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches))
#axarr[row][col]

left   =  0.05  # the left side of the subplots of the figure
right  =  0.97    # the right side of the subplots of the figure
bottom =  0.03    # the bottom of the subplots of the figure
top    =  0.90    # the top of the subplots of the figure
wspace =  .15     # the amount of width reserved for blank space between subplots
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

print('We are mapping: ' + variable_to_plot)
gp_MSOA_signatures.plot(ax=ax,column=variable_to_plot,legend=True,
						cmap='OrRd', scheme='Quantiles', k=2)

#Set figure title 
title='Maps of the UK for ' + variable_to_plot  
plt.suptitle(title, fontsize=20)

# set aspect to equal. This is done automatically when using *geopandas* plot on it's own, but not when working with pyplot directly. 
ax.set_aspect('equal')

#Set ticks and labels van de assen invisible, niemand is geinteresseerd in de lat,lon coords.
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

# Make frame lighter and change line-width:
for pos in ['top','bottom','left','right']:
	ax.spines[pos].set_linewidth(0.5)
	ax.spines[pos].set_color('0.6')

#position legend
#ax.get_legend().set_bbox_to_anchor((1,0.5))
#ax.legend(loc='upper right')
#ax.get_legend().set_title('lol') 

plt.show()




######################
# 9 figures (still ugly)
######################
'''
#Setup figure
ncols=3
nrows=3

figsize_x_cm=30 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
ratio_x_y=0.9 #0.9 for two rows, 
figsize_y_inches=figsize_x_inches*ratio_x_y 

fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
#axarr[row][col]

left   =  0.05  # the left side of the subplots of the figure
right  =  0.97    # the right side of the subplots of the figure
bottom =  0.03    # the bottom of the subplots of the figure
top    =  0.90    # the top of the subplots of the figure
wspace =  .15     # the amount of width reserved for blank space between subplots
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
title=str('Maps of the UK for')
plt.suptitle(title, fontsize=20)

#gp_MSOA_GM.plot(ax=axarr[0][0],column='employment',legend=False)
#gp_MSOA_GM.plot(ax=axarr[0][1],column='E',legend=False)
#gp_MSOA_GM.plot(ax=axarr[1][0],column='X',legend=False)
#gp_MSOA_GM.plot(ax=axarr[1][1],column='S',legend=False)

variables_to_plot=['sum_car_trips_home_to_work_0.01',
					'sum_car_shortest_route_home_to_work_0.01',
					'sum_car_time_spent_home_to_work_0.01',
					'sum_bus_trips_home_to_work_0.01',
					'sum_bus_shortest_route_home_to_work_0.01',
					'sum_bus_time_spent_home_to_work_0.01',
					'sum_rail_trips_home_to_work_0.01',
					'sum_rail_shortest_route_home_to_work_0.01',
					'sum_rail_time_spent_home_to_work_0.01'
					]

variables_to_plot=[	'avg_car_time_spent_home_to_work_0.01',
					'avg_bus_time_spent_home_to_work_0.01',
					'avg_rail_time_spent_home_to_work_0.01'
					]

counter=0
print('We start the plotting of maps now.')
for row in range(nrows):
	for col in range(ncols):
		print('Row: ' + str(row) + ' Col: ' + str(col))
		print('We are mapping: ' + str(variables_to_plot[counter]))

		#color_max=50000
		gp_MSOA_signatures.plot(ax=axarr[row][col],column=variables_to_plot[counter],legend=True)
		#	norm=clr.Normalize(vmin=0,vmax=50000),cmap='RdBu_r')

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

plt.show()
plt.close('all')

'''

############################################################################################
######################################               #######################################
####################################  Developing zone ######################################
#######################################             ########################################
############################################################################################


'''
#3.2. Enrich the geopandas shapefile of GM with data on population, working population and XSE.

#We use both the Name and Code of the MSOA11 to merge. Although normally, one should suffice. Safety my friends.
gp_MSOA_GM_PWPXSE = gp_MSOA_GM.merge(df_PWPXSE_GM, on=['MSOA11CD','MSOA11NM'])

#Check whether dimensions are still the same after the merge. 
if gp_MSOA_GM_PWPXSE.shape[0] != df_PWPXSE_GM.shape[0]:
	print ('\n The merge we just performed has reduced the dimensions of your inputdata on employment, population and XSE. This is not what we would expect. The shapes of both datasets are:')
	print (gp_MSOA_GM_PWPXSE.shape)
	print (df_PWPXSE.shape)
else:
	print ('\nThis merge has not reduced the dimensions of your inputdata on employment, population and XSE. This is what we expected since we filtered the data for GM first')
    


#3.2. Use the enriched geopandas shapefile to map data on population, working population and XSE.

print ('\n We are now plotting the MSOAs in Greater Manchester coloring them by their population, employment and occupation numbers')
'''





'''
#Setup figure
ncols=2 
nrows=3

figsize_x_cm=30 #We want our plot to be as wide as the page (21-3left-3right) in centimeter. 
figsize_x_inches=figsize_x_cm/2.54 #matplotlibs figsize (currently) is in inches only. 
ratio_x_y=0.9 #0.9 for two rows, 
figsize_y_inches=figsize_x_inches*ratio_x_y 

fig, axarr = plt.subplots(figsize=(figsize_x_inches,figsize_y_inches), ncols=ncols, nrows=nrows, sharex=False, sharey=False)
#axarr[row][col]

left   =  0.05  # the left side of the subplots of the figure
right  =  0.97    # the right side of the subplots of the figure
bottom =  0.03    # the bottom of the subplots of the figure
top    =  0.90    # the top of the subplots of the figure
wspace =  .15     # the amount of width reserved for blank space between subplots
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
title=str('Maps of the Manchester region for')
plt.suptitle(title, fontsize=20)

#gp_MSOA_GM.plot(ax=axarr[0][0],column='employment',legend=False)
#gp_MSOA_GM.plot(ax=axarr[0][1],column='E',legend=False)
#gp_MSOA_GM.plot(ax=axarr[1][0],column='X',legend=False)
#gp_MSOA_GM.plot(ax=axarr[1][1],column='S',legend=False)

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

plt.show()
plt.close('all')

'''





############################
#1.2. Get columns ready for use in spint
############################
'''
#filter out intrazonal flows
dataset=dataset[dataset['Origin']!=dataset['Destination']]

#sort dataset by Origin first, then destination. 
dataset=dataset.sort_values(['Oi','Dj'])#.copy()
dataset=dataset.reset_index(drop=True)

flows=dataset['Data'].values
Oi=dataset['Oi'].values
Dj=dataset['Dj'].values
Dij=dataset['Dij'].values
Origin=dataset['Origin'].values
Destination=dataset['Destination'].values

#This sort on a numpy array should be the same as the pandsa sort_values used before. 
# Based on the fact that the panda sort_values doc says 'See also ndarray.np.sort for more information'
Origin_unique=dataset['Origin'].unique()
#Origin_unique.sort()       
Destination_unique=dataset['Destination'].unique()                                                                     
#Destination_unique.sort()
'''