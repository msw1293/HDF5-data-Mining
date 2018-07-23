# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 15:40:02 2018

@author: mwilliams
"""

import numpy as np

m_br =  -0.109
m_zn = -0.0004
b_br = 45.454
b_zn = 0.559
R = 8.314# [J / mol. K.]
n = 2
F = 96485.3329 #[s A / mol]


T = np.arange(18,35,0.2) + 273.15

dU_br = (-R/(n*F))*((m_br)/(m_br*T+b_br)+np.log(m_br*T+b_br))
dU_zn  = (-R/(n*F))*((m_zn)/(m_zn*T+b_zn)+np.log(m_zn*T+b_zn))
print T*dU_br
print T*dU_zn
