# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 14:08:33 2018

@author: lfuchshofen
"""

#This Script contains a data mining example using cycling data and 
#the build matrix

#Import packages and loadHDF5 custom script
import numpy as np
import pymongo
import sys
import loadHDF5

#Define cystom "CellObj" object to store data
class CellObj:
    def __init__(self, ID):   
        self.ID = ID
        self.glue = ''
        self.RTE = []
        self.CLE = []
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

#Set range of IDs to consider
IDs = range(15038,15084)

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
    
    #Append object to list if final criteria met
    #if np.mean(cell.RTE[4:14]) > 70:
    cellData.append(cell)

#Close database connection
connection.close()

#Print resulting list
print 'Filtered Cell Population:'
for cell in cellData:
    print cell.ID, ' ', np.mean(cell.DE)
    
#Sort list according to chosen criteria and reprint
#cellData.sort(key=lambda x: np.mean(x.DE))

#print 'Filtered Cell Population Sorted:'
#for cell in cellData:
    #print cell.ID, ' ', np.mean(cell.DE)
    



