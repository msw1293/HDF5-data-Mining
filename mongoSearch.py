# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 14:08:33 2018

@author: lfuchshofen
"""

#Import packages
import numpy as np
import pymongo
import sys

#Set Credentials
user = 'view'
password = 'EosNewViewer$'

#Create "connection" object
connection = pymongo.MongoClient('192.168.40.40',27017)    
if not connection.build_matrix.authenticate(user,password): sys.exit()

#Navigate to correct doc in database  
db = connection.build_matrix
collection = db.build_matrix

#Define cell range to examine (can use 0,20000 or similar)
cells = range(12000,14000)

#Initiate list for matching cells
filtered = []

#Iterate over cell range
for cell in cells:
    
    #Get database field for given ID
    cell_db = collection.find_one({'_id' : cell})
    
    #Check that result has 'dict' type
    if type(cell_db) != dict:
        continue
    
    #Check if cell fails certain criteria. If yes, skip it
    try:
        if '18A' not in cell_db['Adhesive'].upper():
            continue
        
        if 'jmcmahon' not in cell_db['Owner'].lower():
            continue
        
        if 'RECIPE_245' not in cell_db['Electrolyte Recipe'].upper():
            continue
    except:
        print cell,' skipped'
        continue
    
    #If cell was not filtered out, add it to list
    filtered.append(cell)

#Close connection
connection.close()

