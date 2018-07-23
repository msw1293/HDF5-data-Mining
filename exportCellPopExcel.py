# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 09:31:26 2018

@author: lfuchshofen
"""

#This Script will Demonstrate Pulling Data for a Single Cell
#Using the loadHDF5 tool.

#Import packages and loadHDF5 custom script
import numpy as np
import loadHDF5
import matplotlib.pyplot as plt
import xlwings as xw

#Define cystom "CellObj" object to store data
class CellObj:
    def __init__(self, ID):   
        self.ID = ID
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

#Define a group of cells
IDs = range(13620,13643)

#Define empty list to populate
cellData = []

#Get Data for Cells
for ID in IDs:
    ID = str(ID)
    
    #Load the cycle stats dictionary
    stats = loadHDF5.loadStat(ID)
    
    #Check that load was successful
    if type(stats) == str:
        continue
    
    #Create instance of CellObj to store data for cell number ID
    cell = CellObj(ID)
    
    #Filter cycling data by discharge energy
    mask = [np.add(stats['CV_Discharge_Energy'],stats['CC_Discharge_Energy']) > 0.1]    
    
    #Populate CellObj container with cycling stats data
    cell.RTE = stats['RT_Energy_Efficiency'][mask]*100
    cell.CE = np.add(stats['CV_Charge_Energy'],stats['CC_Charge_Energy'])[mask]
    cell.DE = np.add(stats['CV_Discharge_Energy'],stats['CC_Discharge_Energy'])[mask]
    cell.CC = np.add(stats['CV_Charge_Capacity'],stats['CC_Charge_Capacity'])[mask]
    cell.DC = np.add(stats['CV_Discharge_Capacity'],stats['CC_Discharge_Capacity'])[mask]
    cell.CT = np.add(stats['CV_Charge_Time'],stats['CC_Charge_Time'])[mask]/3600.0
    cell.DT = np.add(stats['CV_Discharge_Time'],stats['CC_Discharge_Time'])[mask]/3600.0
    cell.CP = np.array([cell.CE[i]/cell.CT[i] for i in range(len(cell.RTE))])
    cell.DP = np.array([cell.DE[i]/cell.DT[i] for i in range(len(cell.RTE))])
    cell.CLE = np.array([cell.DC[i]/cell.CC[i] for i in range(len(cell.RTE))])*100  

    #Append instance of CellObj to cellData list
    cellData.append(cell)
    
    
#Write Data to Excell Sheet
excelName = 'AAVG_Data.xlsx'
wb = xw.Book()

#Define the sheets to be written in the sheet and the respective units
sheets = ['RTE','CLE','CE','DE','CC','DC','CT','DT','CP','DP']
units = ['(%)','(%)','(Wh)','(Wh)','(Ah)','(Ah)','(h)','(h)','(W)','(W)']

#Add sheets to doc
for i in range(len(sheets)-1):
        wb.sheets.add()

#Iterate over sheets and add data
for i,sheet in enumerate(sheets):
    
    #Set name and activate corresponding sheet
    wb.sheets[i].name = sheet +' - ' + units[i]
    wb.sheets[i].activate()
    
    #Iterate over cells
    for j,cell in enumerate(cellData):
        prefix = chr(66+j)
        
        xw.Range(prefix+'1').value = cell.ID
        indexes = [x+1 for x in range(len(cell.RTE))]
        xw.Range('A2').value = np.array(indexes)[np.newaxis].T
        xw.Range(prefix+'2').value = np.array(getattr(cell,sheet))[np.newaxis].T
        
        
#Save File. Add ".close()" to close it
wb.save(excelName)

    











