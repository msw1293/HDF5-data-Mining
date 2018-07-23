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
#import seaborn as sns
#sns.set_palette(sns.color_palette("hls", 20))

# this is just a pre-formatting for the figures. Setting the axes font size and the title/label fonts. Setting the legend font size as well.
plt.rc('text', usetex=True) #use LaTeX font and interpreter (good for typesetting greek in the axes)
plt.rc('font', family='serif') #set serif family 
matplotlib.rc('xtick', labelsize=20) #set horizontal axis font size
matplotlib.rc('ytick', labelsize=20) #set vertical acid font size
font = {'family' : 'serif',
        'weight' : 'bold',
        'size'   : 14} #set the legend font size

matplotlib.rc('font', **font)
#matplotlib.rcParams.update({'font.size': 22})

#Define cystom "CellObj" object to store data and statistics
class CellObj:
    def __init__(self, ID):   
        self.ID = ID
        self.glue = ''
        self.electrolyte = ''
        self.experiment = ''
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
IDs = range(17094,17133)

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
    cell.experiment = cell_db['Experiment ID']
    #Filter cycling data by discharge energy
    #mask = np.nan_to_num(stats['RT_Energy_Efficiency'])
    #mask = [np.add(stats['CV_Discharge_Energy'],stats['CC_Discharge_Energy']) > 0.1]
    
   
    #SKip if cell has less than 15 cycles
    cell.RTE = np.nan_to_num(stats['RT_Energy_Efficiency'])
    mask = [cell.RTE[i] > 0 and cell.RTE[i] <= 1 for i in range(len(cell.RTE))]
    cell.RTE = 100*cell.RTE[mask]
    #print cell.RTE
    if len(cell.RTE) < 1: continue

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

class population_group:
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
#These populations only have 
pop1 = population_group(cellData[0:3], 'R421 undoped control')
pop2 = population_group(cellData[3:6], 'R421 0.5M')
pop3 = population_group(cellData[6:9], 'R421 1.5M')
pop4 = population_group(cellData[9:12], 'R421 3.1M')
pop5 = population_group(cellData[12:15], 'R493 0.5M')
pop6 = population_group(cellData[15:18], 'R493 1.5M')
pop7 = population_group(cellData[18:21], 'R493 3.1M')
pop8 = population_group(cellData[21:24], 'R494 0.5M')
pop9 = population_group(cellData[24:27], 'R494 1.5M')
pop10 = population_group(cellData[27:30], 'R494 3.1M')
pop11 = population_group(cellData[30:33], 'R495 0.5M')
pop12 = population_group(cellData[33:36], 'R495 1.5M')
pop13 = population_group(cellData[36:39], 'R495 3.1M')
#List containing all experimental groups:
population = [pop1, pop2, pop3, pop4, pop5, pop6, pop7, pop8, pop9, pop10,pop11, pop12,pop13]
c_pop = [pop1, pop2, pop3, pop4]
low_pop = [pop1, pop5, pop6, pop7]
mid_pop = [pop1, pop8, pop9, pop10]
high_pop = [pop1, pop11, pop12, pop13]
el_population = [c_pop, low_pop, mid_pop, high_pop]
# Modified lifecycle populations
lc_control = cellData[0]
#Control 421
lc_pop1 = population_group(np.take(cellData,[4,8,9]), 'R421 (0.97 wt\% TMPA) control')

#Low TMPA 0.5 wt%
lc_pop2 = population_group(np.take(cellData,[13,16,20]),'R493 (0.5 wt\% TMPA)')

# Mid TMPA 2 wt%
lc_pop3 = population_group(np.take(cellData, [23,26,28]), 'R494 (2.0 wt\% TMPA)')
#High TMPA 3wt%
lc_pop4 = population_group(np.take(cellData, [30,33,37]), 'R495 (3.0 wt\% TMPA)')

lc_population = [lc_control, lc_pop1, lc_pop2, lc_pop3, lc_pop4]
# extract the population mean, lowest and highest performing cells.
def Stats(pop,x):
    temp = []
    last_cycle = []
    for cell in pop.cells: #find the least common amount of cycles per triplicate cells.
        last_cycle.append(len(cell.RTE))
    min_cycle = min(last_cycle)
    #print pop.cells
    for cell in pop.cells: 
        obj_dict = vars(cell) #obj_dict is a dictionary that contains the attributes of the Cell object and can thus be called as a dictionary
        temp.append(obj_dict[x][:min_cycle]) #here we ask the code to extract the value for the 'x' key which can be passed to the function as an argument.
    if len(temp) == 3:
        mat = np.column_stack((temp[0],temp[1],temp[2]))
    else:
        mat = np.column_stack((temp[0],temp[1]))   
    n = len(temp)
    output = np.zeros((min_cycle,2))
    lower = np.zeros((min_cycle,1))
    upper = np.zeros((min_cycle,1))
    for i in range(min_cycle):
        diff = 10**20
        cell1 = 0
        cell2 = 0
        # Find the min diff by comparing difference
        # of each possible cell for every cycle. Find the two closest cells. 
        for j in range(n-1):
            for k in range(j+1,n):
                #print mat[i,j]-mat[i,k]
                if abs(mat[i,j]-mat[i,k]) < diff:
                    diff = abs(mat[i,j] - mat[i,k])
                    cell1 = j
                    cell2 = k
        
        output[i,0] = mat[i,cell1]
        output[i,1] = mat[i,cell2] 
    mu = np.mean(output,axis=1) #average of the two closest performing cells per cycle.
    for i in range(min_cycle):    
        lower[i] = mu[i] - np.min(mat[i,:])
        upper[i] = np.max(mat[i,:]) - mu[i]
    err = np.column_stack((lower,upper))  #print mu
    #print sd
    stats = np.column_stack((mu,err))
    return stats

def LC_stats(cellpop,x):
    temp = []
    last_cycle = []
    mu = []
    sd = []
    
#    if len(cellpop) == 1:
#        obj_dict = vars(cellpop[0])
#        mat = obj_dict[x]
#        mu = np.average(mat[10:])
#        sd = np.std(mat[10:])
#        
#        return np.array([mu,sd])
#    else:      
    for cell in cellpop: #find the least common amount of cycles per triplicate cells.
        last_cycle.append(len(cell.RTE))
    min_cycle = min(last_cycle)
    #print pop.cells
    for cell in cellpop: 
        obj_dict = vars(cell) #obj_dict is a dictionary that contains the attributes of the Cell object and can thus be called as a dictionary
        temp.append(obj_dict[x][:min_cycle]) #here we ask the code to extract the value for the 'x' key which can be passed to the function as an argument.
    if len(temp) == 3:
        mat = np.column_stack((temp[0],temp[1],temp[2]))
    else:
        mat = np.column_stack((temp[0],temp[1]))
    for dat in range(len(temp)):
        av = np.average(mat[10:,dat]) #take only the data after the 9th cycle
        dev = np.std(mat[10:,dat]) #only take the data after the 9th cycle
        mu.append(av)
        sd.append(dev)
    return np.array([mu,sd])

for pop in population:#add statistics to the population objects
    obj_dict = vars(pop)
    pop.CC = Stats(pop,'CC')
    pop.CE = Stats(pop,'CE')
    pop.CLE = Stats(pop,'CLE')
    pop.CP = Stats(pop,'CP')
    pop.CT = Stats(pop,'CT')
    pop.DC = Stats(pop,'DC')
    pop.DE = Stats(pop,'DE')
    pop.DP = Stats(pop,'DP')
    pop.DT = Stats(pop,'DT')
    pop.EE = Stats(pop,'EE')
    pop.RTE = Stats(pop,'RTE')
    print len(pop.DE)


for pop in lc_population[1:]:
    #obj_dict = vars(pop.cells)
    pop.CC = LC_stats(pop.cells,'CC')
    pop.CE = LC_stats(pop.cells,'CE')
    pop.CLE = LC_stats(pop.cells,'CLE')
    pop.CP = LC_stats(pop.cells,'CP')
    pop.CT = LC_stats(pop.cells,'CT')
    pop.DC = LC_stats(pop.cells,'DC')
    pop.DE = LC_stats(pop.cells,'DE')
    pop.DP = LC_stats(pop.cells,'DP')
    pop.DT = LC_stats(pop.cells,'DT')
    pop.EE = LC_stats(pop.cells,'EE')
    pop.RTE = LC_stats(pop.cells,'RTE')
    #print len(pop.DE)
[cav_ee , csd_ee] = [np.average(lc_control.EE[10:]),np.std(lc_control.EE[10:])]
[cav_ce , csd_ce] = [np.average(lc_control.CLE[10:]),np.std(lc_control.CLE[10:])]
[cav_de , csd_de] = [np.average(lc_control.DC[10:]),np.std(lc_control.DC[10:])] 
leg1 = []
#Energy Efficiency of lifecycle cells. 
plt.figure()
for pop in lc_population[1:]:
    leg1.append(pop.name)
    y_data = np.column_stack(([cav_ee,csd_ee],pop.EE))
    x_data = [0,0.5,1.5,3.1]
    plt.errorbar(x_data, y_data[0,:],yerr= y_data[1,:], fmt = 'o',capsize = 4, elinewidth = 1.5)
plt.title(r'\textbf{Average Lifecycle Energy Efficiency}' , fontsize = 25)
plt.xlabel(r'\textbf{Molarity of Doping Solution (M)}' , fontsize = 25)
plt.ylabel(r'\textbf{Energy Efficiency} (\%)', fontsize = 25)
plt.legend(leg1)

#Coulombic Efficiency of lifecycle cells. 
plt.figure()
for pop in lc_population[1:]:
    leg1.append(pop.name)
    y_data = np.column_stack(([cav_ce,csd_ce],pop.CLE))
    x_data = [0,0.5,1.5,3.1]
    plt.errorbar(x_data, y_data[0,:],yerr= y_data[1,:], fmt = 'o',  capsize = 4, elinewidth = 1.5)
plt.title(r'\textbf{Average Lifecycle Coulombic Efficiency}' , fontsize = 25)
plt.xlabel(r'\textbf{Molarity of Doping Solution (M)}' , fontsize = 25)
plt.ylabel(r'\textbf{Coulombic Efficiency} (\%)', fontsize = 25)
plt.legend(leg1)

#Discharge Energy of Lifecycle cells. 

plt.figure()
for pop in lc_population[1:]:
    leg1.append(pop.name)
    y_data = np.column_stack(([cav_de,csd_de],pop.DC))
    x_data = [0,0.5,1.5,3.1]
    plt.errorbar(x_data, y_data[0,:],yerr= y_data[1,:], fmt = 'o',  capsize = 4, elinewidth = 1.5)
plt.title(r'\textbf{Average Lifecycle Discharge Energy}' , fontsize = 25)
plt.xlabel(r'\textbf{Molarity of Doping Solution (M)}' , fontsize = 25)
plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
plt.legend(leg1)




# Lifecycle Plots using total Moles of TMPA in the system #################################################################
###########################################################################################################################

#Energy Efficiency of lifecycle cells. 
plt.figure()
for pop in lc_population[1:]:
    leg1.append(pop.name)
    if pop.name == 'R421 (0.97 wt\% TMPA) control':
        y_data = np.column_stack(([cav_ee,csd_ee],pop.EE))
        x_data = [.022, .072, 0.172, 0.332]
    elif pop.name == 'R493 (0.5 wt\% TMPA)':
        y_data = pop.EE
        x_data = [.0614, 0.1614, 0.3214]
    elif pop.name ==  'R494 (2.0 wt\% TMPA)':
        y_data = pop.EE
        x_data = [.0952, .1952, 0.3552]
    else:
        y_data = pop.EE
        x_data = [.11747, .21747, 0.37747]
    plt.errorbar(x_data, y_data[0,:],yerr= y_data[1,:], fmt = 'o',capsize = 4, elinewidth = 1.5)
plt.title(r'\textbf{Average Lifecycle Energy Efficiency}' , fontsize = 25)
plt.xlabel(r'\textbf{Total Moles of TMPA}' , fontsize = 25)
plt.ylabel(r'\textbf{Energy Efficiency} (\%)', fontsize = 25)
plt.legend(leg1)

#Coulombic Efficiency of lifecycle cells. 
plt.figure()
for pop in lc_population[1:]:
    leg1.append(pop.name)
    if pop.name == 'R421 (0.97 wt\% TMPA) control':
        y_data = np.column_stack(([cav_ce,csd_ce],pop.CLE))
        x_data = [.022, .072, 0.172, 0.332]
    elif pop.name == 'R493 (0.5 wt\% TMPA)':
        y_data = pop.CLE
        x_data = [.0614, 0.1614, 0.3214]
    elif pop.name ==  'R494 (2.0 wt\% TMPA)':
        y_data = pop.CLE
        x_data = [.0952, .1952, 0.3552]
    else:
        y_data = pop.CLE
        x_data = [.11747, .21747, 0.37747]
    plt.errorbar(x_data, y_data[0,:],yerr= y_data[1,:], fmt = 'o',  capsize = 4, elinewidth = 1.5)
plt.title(r'\textbf{Average Lifecycle Coulombic Efficiency}' , fontsize = 25)
plt.xlabel(r'\textbf{Total Moles of TMPA}' , fontsize = 25)
plt.ylabel(r'\textbf{Coulombic Efficiency} (\%)', fontsize = 25)
plt.legend(leg1)

#Discharge Energy of Lifecycle cells. 

plt.figure()
for pop in lc_population[1:]:
    leg1.append(pop.name)
    if pop.name == 'R421 (0.97 wt\% TMPA) control':
        y_data = np.column_stack(([cav_de,csd_ee],pop.DE))
        x_data = [.022, .072, 0.172, 0.332]
    elif pop.name == 'R493 (0.5 wt\% TMPA)':
        y_data = pop.DE
        x_data = [.0614, 0.1614, 0.3214]
    elif pop.name ==  'R494 (2.0 wt\% TMPA)':
        y_data = pop.DE
        x_data = [.0952, .1952, 0.3552]
    else:
        y_data = pop.DE
        x_data = [.11747, .21747, 0.37747]
    plt.errorbar(x_data, y_data[0,:],yerr= y_data[1,:], fmt = 'o',  capsize = 4, elinewidth = 1.5)
plt.title(r'\textbf{Average Lifecycle Discharge Energy}' , fontsize = 25)
plt.xlabel(r'\textbf{Total Moles of TMPA}' , fontsize = 25)
plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
plt.legend(leg1)






###################################
################### Pre-Ramp Cycle Plots###########################

for p in el_population:    
    leg2 = []     
    marks = ['o','>','x','d','h','^','p']
    plt.figure()
    for pop in p:
            leg2.append(pop.name)
            dict_obj = vars(pop)
            y_data = dict_obj['DE'][:,0][:9]
            y_low = dict_obj['DE'][:,1][:9]
            y_high = dict_obj['DE'][:,2][:9]
            x_data = np.arange(1,len(y_data)+1)
            if pop.name == 'R421 undoped control':
                plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'kd', ms = 6 , capsize = 4, elinewidth = 1.5)
#            elif pop.name == 'R495 3.1M':
#                 plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'rx', ms = 6 , capsize = 4, elinewidth = 1.5)
#            elif pop.name == 'R495 1.5M':
#                 plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'g^', ms = 6 , capsize = 4, elinewidth = 1.5)
            else:
                plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'o', ms = 6 , capsize = 4, elinewidth = 1.5)
            plt.title(r'\textbf{Discharge Energy} (Wh)' , fontsize = 25)
            plt.xlabel(r'\textbf{Cycle}' , fontsize = 25)
            plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
    plt.legend(leg2)
    
    plt.figure()
    for pop in p:
            dict_obj = vars(pop)
            y_data = dict_obj['EE'][:,0][:9]
            y_low = dict_obj['EE'][:,1][:9]
            y_high = dict_obj['EE'][:,2][:9]
            x_data = np.arange(1,len(y_data)+1)
            if pop.name == 'R421 undoped control':
                plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'kd', ms = 6 , capsize = 4, elinewidth = 1.5)
#            elif pop.name == 'R495 3.1M':
#                 plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'rx', ms = 6 , capsize = 4, elinewidth = 1.5)
#            elif pop.name == 'R495 1.5M':
#                 plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'g^', ms = 6 , capsize = 4, elinewidth = 1.5)
            else:
                plt.errorbar(x_data, y_data, yerr = [y_low, y_high],fmt = 'o', ms = 6 , capsize = 4, elinewidth = 1.5)
            plt.title(r'\textbf{Energy Efficiency} (\%)' , fontsize = 25)
            plt.xlabel(r'\textbf{Cycle}' , fontsize = 25)
            plt.ylabel(r'\textbf{Energy Efficiency} (\%)', fontsize = 25)
    plt.legend(leg2)
    
    plt.figure()
    for pop in p:
            dict_obj = vars(pop)
            y_data = dict_obj['CLE'][:,0][:9]
            y_low = dict_obj['CLE'][:,1][:9]
            y_high = dict_obj['CLE'][:,2][:9]
            x_data = np.arange(1,len(y_data)+1)
            if pop.name == 'R421 undoped control':
                plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'kd', ms = 6 , capsize = 4, elinewidth = 1.5)
#            elif pop.name == 'R495 3.1M':
#                 plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'rx', ms = 6 , capsize = 4, elinewidth = 1.5)
#            elif pop.name == 'R495 1.5M':
#                 plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'g^', ms = 6 , capsize = 4, elinewidth = 1.5)
            else:
                plt.errorbar(x_data, y_data, yerr = [y_low, y_high],fmt = 'o', ms = 6 , capsize = 4, elinewidth = 1.5)
            plt.title(r'\textbf{Coulombic Efficiency} (\%)' , fontsize = 25)
            plt.xlabel(r'\textbf{Cycle}' , fontsize = 25)
            plt.ylabel(r'\textbf{Coulombic Efficiency} (\%)', fontsize = 25)
    plt.legend(leg2)



#SNR Values
values = ['DE','EE','CLE']
for pop in population:
    print "_______________" , pop.name , "____________________________________"
    obj_dict = vars(pop)
    control_dict = vars(pop1)
    for v in values:
        print "--SNR--:" , v
        mu_c = control_dict[v][:,0][:9]
        mu_e = obj_dict[v][:,0][:9]
        sig_c = np.std(control_dict[v][:,0][:9])
        sig_e = np.std(obj_dict[v][:,0][:9])
        diff = np.subtract(mu_e,mu_c)
        p_diff = (diff/mu_c)*100
        print "------% difference-------" , p_diff
        error = np.sqrt(sig_c**2 + sig_e**2)
        SNR = diff/error
        print SNR
        
        

#Power Ramp
#plt.figure()
#for pop in population:
#        dict_obj = vars(pop)
#        y_data = dict_obj['EE'][:,0]
#        y_low = dict_obj['EE'][:,1]
#        y_high = dict_obj['EE'][:,2]
#        x_data = np.arange(1,len(y_data)+1)
#        if pop.name == 'R421 control':
#            plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'kd', ms = 8 , capsize = 4, elinewidth = 1.5)
#        elif pop.name == 'R495 3.1M':
#             plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'rx', ms = 8 , capsize = 4, elinewidth = 1.5)
#        elif pop.name == 'R495 1.5M':
#             plt.errorbar(x_data, y_data, yerr = [y_low,y_high],fmt = 'g^', ms = 8 , capsize = 4, elinewidth = 1.5)
#        else:
#            plt.errorbar(x_data, y_data, yerr = [y_low, y_high],fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
#        plt.title(r'\textbf{Energy Efficiency} (\%)' , fontsize = 25)
#        plt.xlabel(r'\textbf{Discharge Power} (W)' , fontsize = 25)
#        plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
#plt.legend(leg)

                    #plt.title()
   






#plt.figure()
#for cell in lc_pop1.cells:
#        x = np.arange(1,len(cell.RTE)+1)
#        y = cell.EE
#        plt.plot(x,y)
#    
    #        
#

# create an object that compiles all the recipes with the same molarity of quat salts
#class Molarity_group:
#    def __init__(self,M, recipes):
#        self.M = M
#        self.recipes = recipes
#        
## initialize the different molarity groups        
#M_25 = Molarity_group(0.25, [control,R313])
#M_35 = Molarity_group(0.35, [control,R319])
#M_45 = Molarity_group(0.45, [control, R325,R326])
#M_5 = Molarity_group(0.5, [control,R308,R309,R310,R311,R312])
#M_6 = Molarity_group(0.6, [control,R314,R315,R316,R317,R318])
#M_7 = Molarity_group(0.7, [control,R320,R321,R322,R323,R324])
#
#
#Molarity = [M_25, M_35 , M_45, M_5, M_6, M_7]
#
## plot the ramp cycles#
##_____________________NOTE_____________________________________________
## The cycle indices might be different for your experiment, first identify the cycle indices for each ramp or set of cycles
##you'd like to obtain data for. 
#
##standard 4X ramp values for power, capacity, TOC rest.
#powers = [1.3 , 2.8, 4.2, 5.6, 7] #in Watts
#caps = [8.8, 12.7, 16.6, 20.5, 24.3] #in Ah
#TOC = [0.5, 2, 4, 10, 24,36,48] #in hours
#d = np.arange(1,7) #cycle indices for the 2d power and capacity ramp. 
#
#
##In the following blocks, we iterate across the experimental group, and for each recipe in the molarity groups. 
##TOC rest ramp
#for M in Molarity:
#    obj_dict = vars(M)
#    legend = []
#    plt.figure()
#    for recipe in M.recipes:
#        if recipe.name == 'R302 control':
#                TOC1 = [0.5, 2, 4, 10, 24]
#                plt.errorbar(TOC1,recipe.DE[22:27,0], yerr = recipe.DE[22:27,1], fmt = '-o', ms = 8 , capsize = 4, elinewidth = 1.5)
#        else:
#                plt.errorbar(TOC, recipe.DE[22:29,0], yerr = recipe.DE[22:29,1], fmt = '-o', ms = 8 , capsize = 4, elinewidth = 1.5)
#                #plt.title()
#                plt.xlabel(r'\textbf{Top of Charge Rest Time} (hr)' , fontsize = 25)
#                plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
#        legend.append(recipe.name)
#        plt.legend(legend)
#    
    #Power ramp

#   
##Capacity Ramp         
#for M in Molarity:
#    obj_dict = vars(M)
#    legend = []
#    plt.figure()
#    for recipe in M.recipes:
#        plt.errorbar(caps, recipe.DE[10:15,0], yerr = recipe.DE[10:15,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
#                    #plt.title()
#        plt.xlabel(r'\textbf{Charge Capacity} (Ah)' , fontsize = 25)
#        plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
#        legend.append(recipe.name)
#        plt.legend(legend)
#           
#        
# #2D Ramp        
#for M in Molarity:
#    obj_dict = vars(M)
#    legend = []
#    plt.figure()
#    for recipe in M.recipes:
#        plt.errorbar(d, recipe.DE[16:22,0], yerr = recipe.DE[16:22,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
#                    #plt.title()
#        plt.xlabel(r'\textbf{2D Ramp Cycle}' , fontsize = 25)
#        plt.ylabel(r'\textbf{Discharge Energy} (Wh)', fontsize = 25)
#        legend.append(recipe.name)
#        plt.legend(legend)
#           
#        
# # Peak Power Efficiencies        
#for M in Molarity:
#    obj_dict = vars(M)
#    legend = []
#    plt.figure()
#    for recipe in M.recipes:
#        plt.errorbar(recipe.EE[8,0], recipe.CLE[8,0],xerr = recipe.EE[8,1], yerr = recipe.CLE[8,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
#                    #plt.title()
#        plt.xlabel(r'\textbf{Peak Power Energy Efficiency} (\%)' , fontsize = 25)
#        plt.ylabel(r'\textbf{Peak Power Coulombic Efficiency} (\%)', fontsize = 25)
#        legend.append(recipe.name)
#        plt.legend(legend)
#           
#        
## Peak Capacity Efficiencies        
#for M in Molarity:
#    obj_dict = vars(M)
#    legend = []
#    plt.figure()
#    for recipe in M.recipes:
#        plt.errorbar(recipe.EE[14,0], recipe.CLE[14,0],xerr = recipe.EE[14,1], yerr = recipe.CLE[14,1], fmt = 'o', ms = 8 , capsize = 4, elinewidth = 1.5)
#                    #plt.title()
#        plt.xlabel(r'\textbf{Peak Capacity Energy Efficiency} (\%)' , fontsize = 25)
#        plt.ylabel(r'\textbf{Peak Capacity Coulombic Efficiency} (\%)', fontsize = 25)
#        legend.append(recipe.name)
#        plt.legend(legend)
#           
##Print SNR values on Discharge Energy            
#for M in Molarity:
#    print "------Group:", M.M ,'----------'
#    c = np.mean(control.DE[0:4])
#    c_sd = np.std(control.DE[0:4])
#    for recipe in M.recipes[1:]:
#        mu = np.mean(recipe.DE[0:4])
#        sd = np.std(recipe.DE[0:4])
#        csd = np.sqrt(c_sd**2 + sd**2)
#        snr = (mu-c)/csd
#        print recipe.name , snr
#        





##Print resulting list
##print 'Filtered Cell Population:'
##for cell in cellData:
# #   print cell.ID, ' ', np.mean(cell.DE)
#  
#  
###Sort list according to chosen criteria and reprint
##cellData.sort(key=lambda x: np.mean(x.DE))
###
###print 'Filtered Cell Population Sorted:'
##for cell in cellData:
##    print cell.ID, ' ', np.mean(cell.DE)
##    
##
#
#
