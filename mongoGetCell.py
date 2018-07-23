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


cell = 12345

#Use this command to find cells in build matrix
cell_db = collection.find_one({'_id' : cell})

#Close connection when done. cell_db dic still populated
connection.close()

#Print dictionary indexes
print cell_db.keys()

for item in cell_db.keys():
    print item
