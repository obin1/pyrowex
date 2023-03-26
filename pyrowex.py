#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 21:23:45 2023

@author: psturm
"""

""" 

pyrowex: the Python Recorder of Wildfire Exceptional Events

Notes:
Design to be Standard agnostic: 
    rather than only mattering for exceedances (35.7) apply to any deviation above a certain percentile
Moving average for identifying exceptional exceedance?
There are 1380 
"""

import numpy as np
import pandas as pd
import os 
import matplotlib.pyplot as plt

dfHMS = pd.read_csv("Data for SCAQMD Project/ExceedancesWithHMSsmokeOverhead.csv")

parameter_codes = dfHMS["ParameterCode"].unique()
sites = dfHMS['LocalSiteName'].unique()

# for 



# for site in site_names:
#     for year in 

# site = 'Riverside (Magnolia)'
site = 'Anaheim'
code = str(88502)
filelist = []
for file in os.listdir('Data for SCAQMD Project/'):
    if file[0:11] == "daily_"+code:
        filelist.append(file)        
filelist.sort()

i = 0
for file in filelist:
    dftemp = pd.read_csv("Data for SCAQMD Project/"+file)
    mask = (dftemp['Local Site Name'] == site) & (dftemp['Sample Duration'] == '24-HR BLK AVG')

    i += 1
    if i == 1:
        dfsite = dftemp[mask]

    else:
        dfsite = pd.concat((dfsite,dftemp[mask]),
                           ignore_index=True)
        
rolling_ave = dfsite["Arithmetic Mean"].rolling(30,min_periods=1,closed='both').mean()
rolling_pct = dfsite["Arithmetic Mean"].rolling(30,min_periods=1,closed='both').quantile(.98)
rolling_std = dfsite["Arithmetic Mean"].rolling(30,min_periods=1,closed='both').std()
rolling_exp = dfsite["Arithmetic Mean"].ewm(halflife=30).std()



threshold = 35.7
exceedances = dfsite.loc[dfsite["Arithmetic Mean"]>threshold]["Arithmetic Mean"]


# plot time range

start_date = '2011-01-01'
end_date = '2014-01-01'
start_loc = dfsite.loc[dfsite['Date Local'] == start_date].index[0]
end_loc = dfsite.loc[dfsite['Date Local'] == end_date].index[0]

plt.plot(rolling_ave[start_loc:end_loc],color='red')
time = range(0,len(rolling_ave))
# 2.06 standard deviations is the 98% percentile for a normal curve
plt.fill_between(time[start_loc:end_loc], rolling_ave[start_loc:end_loc],
                 rolling_ave[start_loc:end_loc]+2.06*rolling_std[start_loc:end_loc],
                 alpha=0.2,color='red')
mask_x = np.logical_and(exceedances.index>start_loc,exceedances.index<end_loc)
plt.scatter(exceedances.index[mask_x],exceedances[mask_x])
# plt.scatter(dfsite)


