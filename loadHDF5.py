import h5py
import numpy as np
import time
import sys
import os
import glob
import subprocess

categories = [
              'Data_Point',
              'Test_Time',
              'Step_Time',
              'DateTime',
              'Step_Index',
              'Cycle_Index',
              'Current',
              'Voltage',
              'Charge_Capacity',
              'Discharge_Capacity',
              'Charge_Energy',
              'Discharge_Energy',
              ]

statCategories = [
                  'cycle',
                  'CC_Charge_Capacity',
                  'CC_Charge_Energy',
                  'CC_Charge_Time',
                  'CV_Charge_Capacity',
                  'CV_Charge_Energy',
                  'CV_Charge_Time',
                  'CC_Discharge_Capacity',
                  'CC_Discharge_Energy',
                  'CC_Discharge_Time',
                  'CV_Discharge_Capacity',
                  'CV_Discharge_Energy',
                  'CV_Discharge_Time',
                  'RT_Energy_Efficiency'
                  ]


targetDirectory = '//192.168.40.40/Processed_Data/'


def loadData(cellID,category):
    try:
    
        if not '.hdf5' in cellID:
            cellID += '.hdf5'
        cellgroup = cellID.split('.')[0][0:-3]+'000_cells/'
        
        with h5py.File(targetDirectory+cellgroup+cellID,'r') as f:        
            
            raw_data = f['Raw_Data']
            dataFiles = []
            for dataFile in raw_data:
                dataFiles.append(raw_data[dataFile])
            
            dataFiles.sort(key=lambda x: x.attrs['Start_Time'])

            data = np.array([])
            for dataFile in dataFiles:
                
                if category == 'Test_Time' or category == 'Cycle_Index':
                    try:
                        firstPoint = dataFile[category][0]
                        if firstPoint < data[-1]:
                            data = np.append(data,np.add(dataFile[category][:],np.subtract(data[-1],firstPoint)))
                        else:
                            data = np.append(data,dataFile[category])
                            
                    except IndexError:
                        data = np.append(data,dataFile[category])

                else:
                    data = np.append(data,dataFile[category])

        return data
    except:
        print sys.exc_info()[0]
        return ''
        
def loadTemp(cellID):
    try:    
        if not '.hdf5' in cellID:
            cellID += '.hdf5'
        cellgroup = cellID.split('.')[0][0:-3]+'000_cells/'
        
        with h5py.File(targetDirectory+cellgroup+cellID,'r') as f:           
            raw_data = f['Raw_Data']
            dataFiles = []
            for dataFile in raw_data:
                dataFiles.append(raw_data[dataFile])
            
            dataFiles.sort(key=lambda x: x.attrs['Start_Time'])
            dim = len(dataFiles[0]['AuxTemp'])
            
            data = []
            for i in range(dim):
                data.append(np.array([]))
                       
            for dataFile in dataFiles:
                for i,key in enumerate(dataFile['AuxTemp']):     
                    data[i] = np.append(data[i],dataFile['AuxTemp'][key])    

        return data
    except:
        print sys.exc_info()[0]
        return ''
    
    

def loadStat(cellID):
    try:
        if not '.hdf5' in cellID:
            cellID += '.hdf5'
        cellgroup = cellID.split('.')[0][0:-3]+'000_cells/'
        
        with h5py.File(targetDirectory+cellgroup+cellID,'r') as f:
            stat = {}
            for category in statCategories:
                stat[category] = f['Statistics'][category][1:]


        return stat
    except:
        print sys.exc_info()[0]
        return ''

def loadAttrs(cellID):
    rootAttrs = {}
    fileAttrs = {}

    if not '.hdf5' in cellID:
        cellID += '.hdf5'
        cellgroup = cellID.split('.')[0][0:-3]+'000_cells/'
        with h5py.File(targetDirectory+cellgroup+cellID,'r') as f:
            
            for attr in f.attrs:
                rootAttrs[attr] = f.attrs[attr]
            
            for g in f:
                attrs = {}
                for attr in f[g].attrs:
                    attrs[attr] = f[g].attrs[attr]
                fileAttrs[g] = attrs
                
        return rootAttrs,fileAttrs






