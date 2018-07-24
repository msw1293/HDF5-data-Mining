# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 15:40:02 2018

@author: mwilliams
"""

import numpy as np
import matplotlib.pyplot as pl


#Local current density of electrodes 
i_cathode_nlc = 0.511*(.186*.1055) #[A]
i_anode_nlc = 95.1*(.186*.1055) #[A]

i_cathode_120B = 1.6385*(.2719*.325) #[A]
i_anode_120B = 99*(.2719*.325) #[A]

i_cathode_stack = 40*1.6385*(.2719*.325)
i_anode_stack = 40*99*(.2719*.325)


#dU_dT of the ZnBr2 half cells using OLI activity data:
T_A = 293.15 #[K] Ambient Temperature. 
m_br =  -0.109
m_zn = -0.0004
b_br = 45.454
b_zn = 0.559
R = 8.314# [J / mol. K.]
n = 2
F = 96485.3329 #[s A / mol]
T = np.arange(18,35,0.2) + 273.15
t = 14400 #seconds in 4 hours. 


dU_br = (-R/(n*F))*((m_br)/(m_br*T+b_br)+np.log(m_br*T+b_br)) #[W/ A K]
dU_zn  = (-R/(n*F))*((m_zn)/(m_zn*T+b_zn)+np.log(m_zn*T+b_zn)) #[W/ A K ]

dU_dT = (R/(n*F))*(T*(m_zn*b_br-m_br*b_zn)/(m_zn*m_br*T**2 +T*(m_zn*b_br+m_br*b_zn)+b_zn*b_br)+np.log(m_zn*T + b_zn) - np.log(m_br*T + b_br))
print T*(dU_br + dU_zn) #[W/A]
#print T*(dU_dT)

#TEMPERATURE CHANGE RATES FOR NLC
m_nlc = .7628 #[kg]
Cp_nlc = 343.74 #[ J / kg C] KEEP TRACK OF UNITS!
dT_dt_chg1 = -9.7e-5 #[degrees celsius/ s] for ~3 [A] CURRENT
dt_dt_dchg1 = 1.38e-4 #[degrees celsius / s]


#TEMPERATURE CHANGE RATES FOR 40STACK
m_40 = 86.382 #[kg]
Cp_40 = 219.93 #[J / kg C]
dT_dt_chg2 = 4.5e-4 #[Degrees celsius / s]
dT_dt_dchg2 = 2.0e-4 #[Degrees celsius / s]


#Heat Transfer

h_avg = 16.67 # [W / m^2 K] average total heat transfer coefficient. 
A_nlc = 8.162e-3 #boundary surface area [m^2]
A_stack = 0.66853  #boundary surface area [m^2]
