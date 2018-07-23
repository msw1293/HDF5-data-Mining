# -*- coding: utf-8 -*-
"""
Created on Thu Jan 04 09:24:52 2018

@author: lfuchshofen
"""

#This Script will Demonstrate Pulling Data for a Single Cell
#Using the loadHDF5 tool.

#Import packages and custom "loadHDF5" sheet
import numpy as np
import loadHDF5
import matplotlib.pyplot as plt


#Give a Cell ID
cell = '13790'

#Load Data. Load test time, current, and voltage
tt = loadHDF5.loadData(cell,'Test_Time')
I = loadHDF5.loadData(cell,'Current')
V = loadHDF5.loadData(cell,'Voltage')


#Load the cycle stats dictionary
stats = loadHDF5.loadStat(cell)


#Plot (remove both """ instances). Create plot object, plot two dataseries
#Plot IV Curve
fig, ax = plt.subplots()
ax.plot(tt,I)
ax.plot(tt,V)