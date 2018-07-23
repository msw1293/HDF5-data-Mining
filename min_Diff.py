# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 13:12:45 2018

@author: mwilliams
"""

# Python implementation of simple method to find
# minimum difference between any pair
 
# Returns minimum difference between any pair
def findMinDiff(arr, n):
    # Initialize difference as infinite
    diff = 10**20
    cell1 = 0
    cell2 = 0
    # Find the min diff by comparing difference
    # of all possible pairs in given array
    for i in range(n-1):
        for j in range(i+1,n):
            if abs(arr[i]-arr[j]) < diff:
                diff = abs(arr[i] - arr[j])
                cell1 = i
                cell2 = j
 
    # Return min diff
    return diff, cell1, cell2
 
# Driver code
arr = [1, 5, 3, 19, 18, 25]
n = len(arr)
print("Minimum difference is " + str(findMinDiff(arr, n)))
 