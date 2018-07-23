# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 14:08:33 2018

@author: mwilliams
"""

#This Script contains a data mining example using cycling data and 
#the build matrix

#Import packages and loadHDF5 custom script
import numpy as np
import pymongo
import sys
import loadHDF5
import matplotlib
import matplotlib.pyplot as plt


# this is just a pre-formatting for the figures. Setting the axes font size and the title/label fonts. Setting the legend font size as well.
plt.rc('text', usetex=True) #use LaTeX font and interpreter (good for typesetting greek in the axes)
plt.rc('font', family='serif') #set serif family 
matplotlib.rc('xtick', labelsize=20) #set horizontal axis font size
matplotlib.rc('ytick', labelsize=20) #set vertical acid font size
font = {'family' : 'serif',
        'weight' : 'bold',
        'size'   : 18} #set the legend font size

matplotlib.rc('font', **font)
#matplotlib.rcParams.update({'font.size': 22})

#Define cystom "CellObj" object to store data and statistics
class CellObj:
    def __init__(self, ID):   
        self.ID = ID
        self.glue = ''
        self.electrolyte = ''
        self.RTE = []
        self.CLE = []
        self.EE = []
        self.CE = []
        self.DE = []
        self.CC = []
        self.DC = []
        self.CT = []
        self.DT = []
        self.CP = []
        self.DP = []

#Set Credentials
user = 'view'
password = 'EosNewViewer$'

#Create "connection" object
connection = pymongo.MongoClient('192.168.40.40',27017)    
if not connection.build_matrix.authenticate(user,password): sys.exit()

#Navigate to correct doc in database
db = connection.build_matrix
collection = db.build_matrix

#Set range of IDs to consider. Use build matrix to find the serial numbers for the experiment in question.
IDs = range(15025,15085)

#Initialize list for cells meeting criteria
cellData = []

#Iterate over IDs
for ID in IDs:
    
    #Get database field for given ID
    cell_db = collection.find_one({'_id' : ID})
    
    #Check that result has 'dict' type
    if type(cell_db) != dict:
        print ID,' skipped'
        continue
    
    #Type cast ID for use with loadHDF5
    ID = str(ID)
    
    #Load the cycle stats dictionary
    stats = loadHDF5.loadStat(ID)
    
    #Check that load was successful
    if type(stats) == str:
        print 'error ',ID
        continue
    
    #Create instance of CellObj to store data for cell number ID
    cell = CellObj(ID)
    cell.glue = cell_db['Adhesive']
    cell.electrolyte = cell_db['Electrolyte Recipe'][0:10]
    
    #Filter cycling data by discharge energy
    mask = [np.add(stats['CV_Discharge_Energy'],stats['CC_Discharge_Energy']) > 0.1]
    
   
    #SKip if cell has less than 15 cycles
    cell.RTE = stats['RT_Energy_Efficiency'][mask]*100
    if len(cell.RTE) < 15: continue

    #Populate CellObj container with cycling stats data
    cell.CE = np.add(stats['CV_Charge_Energy'],stats['CC_Charge_Energy'])[mask]
    cell.DE = np.add(stats['CV_Discharge_Energy'],stats['CC_Discharge_Energy'])[mask]
    cell.CC = np.add(stats['CV_Charge_Capacity'],stats['CC_Charge_Capacity'])[mask]
    cell.DC = np.add(stats['CV_Discharge_Capacity'],stats['CC_Discharge_Capacity'])[mask]
    cell.CT = np.add(stats['CV_Charge_Time'],stats['CC_Charge_Time'])[mask]/3600.0
    cell.DT = np.add(stats['CV_Discharge_Time'],stats['CC_Discharge_Time'])[mask]/3600.0
    cell.CP = np.array([cell.CE[i]/cell.CT[i] for i in range(len(cell.RTE))])
    cell.DP = np.array([cell.DE[i]/cell.DT[i] for i in range(len(cell.RTE))])
    cell.CLE = np.array([cell.DC[i]/cell.CC[i] for i in range(len(cell.RTE))])*100  
    cell.EE = np.array([cell.DE[i]/cell.CE[i] for i in range(len(cell.RTE))])*100  
   
    
    #you can filter the cells obtained by adding a conditional statement. The one shown below filters out the cells that achieved an RTE above 70%
    #In the cycles 4-13
    #Append object to list if final criteria met
    
    #if np.mean(cell.RTE[4:14]) > 70:
    
    
    cellData.append(cell)

#Close database connection
connection.close()
#sort out experimental populations


#The following object was created because the experiment studied different electrolytes. However any kind of object can be created to group data
#alternatively, the Cell object can have attributes that describe it's felt, frame, etc.
# Define the properties of a electrolyte recipe group of cells

class Recipe_group:
     def __init__(self, cells,name):
        self.cells = cells
        self.name = name
        self.RTE = []
        self.CLE = []
        self.EE = []
        self.CE = []
        self.DE = []
        self.CC = []
        self.DC = []
        self.CT = []
        self.DT = []
        self.CP = []
        self.DP = []

#create Recipe objects containing the data for the appropriate cells:
control = Recipe_group(cellData[:3], 'R302 control')
R308 = Recipe_group(cellData[3:6], 'R308')
R309 = Recipe_group(cellData[6:9], 'R309')
R310 = Recipe_group(cellData[9:12], 'R310')
R311 = Recipe_group(cellData[12:15], 'R311')
R312 = Recipe_group(cellData[15:18], 'R312')
R313 = Recipe_group(cellData[18:21], 'R313')
R314 = Recipe_group(cellData[21:24], 'R314')
R315 = Recipe_group(cellData[24:27], 'R315')
R316 = Recipe_group(cellData[27:30], 'R316')
R317 = Recipe_group(cellData[30:33], 'R317')
R318 = Recipe_group(cellData[33:36], 'R318')
R319 = Recipe_group(cellData[36:39], 'R319')
R320 = Recipe_group(cellData[39:42], 'R320')
R321 = Recipe_group(cellData[42:45], 'R321')
R322 = Recipe_group(cellData[45:48], 'R322')
R323 = Recipe_group(cellData[48:51], 'R323')
R324 = Recipe_group(cellData[51:54], 'R324')
R325 = Recipe_group(cellData[54:57], 'R325')
R326 = Recipe_group(cellData[57:60], 'R326')

#List containing all experimental groups:
population = [control, R308, R309,R310,R311,R312, R313,R314,R315,R316,R317,R318,R319,R320,R321,R322,R323,R324,R325,R326]

# extract the population mean and standard deviation for each recipe for any attribute listed in the cell object.
def Stats(pop,x):
    temp = []
    last_cycle = []
    for cell in pop.cells: #find the least common amount of cycles per triplicate cells.
        last_cycle.append(len(cell.RTE))
    min_cycle = min(last_cycle)
    for cell in pop.cells: 
        obj_dict = vars(cell) #obj_dict is a dictionary that contains the attributes of the Cell object and can thus be called as a dictionary
        temp.append(obj_dict[x][:min_cycle]) #here we ask the code to extract the value for the 'x' key which can be passed to the function as an argument.
    if len(temp) == 3:
        mat = np.column_stack((temp[0],temp[1],temp[2]))
    else:
        mat = np.column_stack((temp[0],temp[1]))
    mu = np.mean(mat,axis=1)    
    sd = np.std(mat,axis=1)
    #print mu
    #print sd
    stats = np.column_stack((mu,sd))
    return stats

for pop in population: #populate the recipe objects with statistics (mean, standard deviation) about their triplicate cells on all the variables. 
    obj_dict = vars(pop)
    pop.CC = Stats(pop,'CC')
    pop.CE = Stats(pop,'CE')
    pop.CLE = Stats(pop,'CLE')
    pop.CP = Stats(pop,'CLE')
    pop.CT = Stats(pop,'CT')
    pop.DC = Stats(pop,'DC')
    pop.DE = Stats(pop,'DE')
    pop.DP = Stats(pop,'DP')
    pop.DT = Stats(pop,'DT')
    pop.EE = Stats(pop,'EE')
    pop.RTE = Stats(pop,'RTE')
    
    
    


# create an object that compiles all the recipes with the same molarity of quat salts
class Molarity_group:
    def __init__(self,M, recipes):
        self.M = M
        self.recipes = recipes
        
# initialize the different molarity groups        
M_25 = Molarity_group(0.25, [control,R313])
M_35 = Molarity_group(0.35, [control,R319])
M_45 = Molarity_group(0.45, [control, R325,R326])
M_5 = Molarity_group(0.5, [control,R308,R309,R310,R311,R312])
M_6 = Molarity_group(0.6, [control,R314,R315,R316,R317,R318])
M_7 = Molarity_group(0.7, [control,R320,R321,R322,R323,R324])


Molarity = [M_25, M_35 , M_45, M_5, M_6, M_7]

# plot the ramp cycles#
#_____________________NOTE_____________________________________________
# The cycle indices might be different for your experiment, first identify the cycle indices for each ramp or set of cycles
#you'd like to obtain data for. 

#standard 4X ramp values for power, capacity, TOC rest.
powers = [1.3 , 2.8, 4.2, 5.6, 7] #in Watts
caps = [8.8, 12.7, 16.6, 20.5, 24.3] #in Ah
TOC = [0.5, 2, 4, 10, 24,36,48] #in hours
d = np.arange(1,7) #cycle indices for the 2d power and capacity ramp. 


#In the following blocks, we iterate across the experimental group, and for each recipe in the molarity groups. 
#TOC rest ramp
for M in Molarity:
    obj_dict = vars(M)
    legend = []
    plt.figure()
    for recipe in M.recipes:
        if recipe.name == 'R302 control':
                TOC1 = [0.5, 2, 4, 10, 24]
                plt.errorbar(TOC1,recipe.DE[22:27,0], yerr = recipe.DE[22:27,1], fmt = '-o', ms = 8 , capsize = 4, elinewidth = 1.5)
        else:
                plt.errorbar(TOC, recipe.DE[22:29,0], yerr = recipe.DE[22:29,1], fmt = '-o', ms = 8 , capsize = 4, elinewidth = 1.5)
                #plt.title()
                plt.xlabel(r'\textbf{Top of Charge Rest Time} (hr)' , fontsize = 25)
                plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
        legend.append(recipe.name)
        plt.legend(legend)
    
    #Power ramp
for M in Molarity:
    obj_dict = vars(M)
    legend = []
    plt.figure()
    for recipe in M.recipes:
        plt.errorbar(powers, recipe.DE[4:9,0], yerr = recipe.DE[4:9,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
                    #plt.title()
        plt.xlabel(r'\textbf{Discharge Power} (W)' , fontsize = 25)
        plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
        legend.append(recipe.name)
        plt.legend(legend)
           
   
#Capacity Ramp         
for M in Molarity:
    obj_dict = vars(M)
    legend = []
    plt.figure()
    for recipe in M.recipes:
        plt.errorbar(caps, recipe.DE[10:15,0], yerr = recipe.DE[10:15,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
                    #plt.title()
        plt.xlabel(r'\textbf{Charge Capacity} (Ah)' , fontsize = 25)
        plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
        legend.append(recipe.name)
        plt.legend(legend)
           
        
 #2D Ramp        
for M in Molarity:
    obj_dict = vars(M)
    legend = []
    plt.figure()
    for recipe in M.recipes:
        plt.errorbar(d, recipe.DE[16:22,0], yerr = recipe.DE[16:22,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
                    #plt.title()
        plt.xlabel(r'\textbf{2D Ramp Cycle}' , fontsize = 25)
        plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
        legend.append(recipe.name)
        plt.legend(legend)
           
        
 # Peak Power Efficiencies        
for M in Molarity:
    obj_dict = vars(M)
    legend = []
    plt.figure()
    for recipe in M.recipes:
        plt.errorbar(recipe.EE[8,0], recipe.CLE[8,0],xerr = recipe.EE[8,1], yerr = recipe.CLE[8,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
                    #plt.title()
        plt.xlabel(r'\textbf{Peak Power Energy Efficiency} (\%)' , fontsize = 25)
        plt.ylabel(r'\textbf{Peak Power Coulombic Efficiency} (\%)', fontsize = 25)
        legend.append(recipe.name)
        plt.legend(legend)
           
        
# Peak Capacity Efficiencies        
for M in Molarity:
    obj_dict = vars(M)
    legend = []
    plt.figure()
    for recipe in M.recipes:
        plt.errorbar(recipe.EE[14,0], recipe.CLE[14,0],xerr = recipe.EE[14,1], yerr = recipe.CLE[14,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
                    #plt.title()
        plt.xlabel(r'\textbf{Peak Capacity Energy Efficiency} (\%)' , fontsize = 25)
        plt.ylabel(r'\textbf{Peak Capacity Coulombic Efficiency} (\%)', fontsize = 25)
        legend.append(recipe.name)
        plt.legend(legend)
           
#Print SNR values on Discharge Energy            
for M in Molarity:
    print "------Group:", M.M ,'----------'
    c = np.mean(control.DE[0:4])
    c_sd = np.std(control.DE[0:4])
    for recipe in M.recipes[1:]:
        mu = np.mean(recipe.DE[0:4])
        sd = np.std(recipe.DE[0:4])
        csd = np.sqrt(c_sd**2 + sd**2)
        snr = (mu-c)/csd
        print recipe.name , snr
        

#Print resulting list
#print 'Filtered Cell Population:'
#for cell in cellData:
 #   print cell.ID, ' ', np.mean(cell.DE)
  
  
##Sort list according to chosen criteria and reprint
#cellData.sort(key=lambda x: np.mean(x.DE))
##
##print 'Filtered Cell Population Sorted:'
#for cell in cellData:
#    print cell.ID, ' ', np.mean(cell.DE)
#    
#


