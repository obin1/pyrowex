#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 21:23:45 2023

@author: psturm
"""

""" 

pyrowex: Python Retrieval of Wildfire Exceptional Events

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
    pm25temp = pd.read_csv("Data for SCAQMD Project/"+file,parse_dates=["Date Local"])
    mask = (pm25temp['Local Site Name'] == site) & (pm25temp['Sample Duration'] == '24-HR BLK AVG')

    i += 1
    if i == 1:
        pm25site = pm25temp[mask]

    else:
        pm25site = pd.concat((pm25site,pm25temp[mask]),
                           ignore_index=True)
        
rolling_ave = pm25site["Arithmetic Mean"].rolling(90,min_periods=1,closed='both').mean()
rolling_pct = pm25site["Arithmetic Mean"].rolling(90,min_periods=1,closed='both').quantile(.98)
rolling_std = pm25site["Arithmetic Mean"].rolling(90,min_periods=1,closed='both').std()
std = pm25site["Arithmetic Mean"].std()

rolling_exp = pm25site["Arithmetic Mean"].ewm(halflife=5).std()

compare_years = 5
rolling_ave_years = rolling_ave.groupby(pm25site['Date Local'].dt.dayofyear).nth(range(0,compare_years))
rolling_ave_years = rolling_ave_years.groupby(np.arange(len(rolling_ave_years))//compare_years).mean()


threshold = 35.7
exceedances = pm25site.loc[pm25site["Arithmetic Mean"]>threshold]["Arithmetic Mean"]
exceedances_dates = pm25site.loc[pm25site["Arithmetic Mean"]>threshold]["Date Local"]



# plot time range

start_date = '2011-01-01'
end_date = '2016-01-01'
start_loc = pm25site.loc[pm25site['Date Local'] == start_date].index[0]
end_loc = pm25site.loc[pm25site['Date Local'] == end_date].index[0]

fig, timeseries = plt.subplots()

dates = pd.to_datetime(pm25site['Date Local'][start_loc:end_loc])

timeseries.plot(dates,rolling_ave[start_loc:end_loc],color='red')
time = pd.to_datetime(pm25site['Date Local'][start_loc:end_loc])
# 2.06 standard deviations is the 98% percentile for a normal curve
timeseries.fill_between(dates, rolling_ave[start_loc:end_loc],
                 rolling_ave[start_loc:end_loc]+2.06*std,
                 alpha=0.2,color='red')
mask_x = np.logical_and(exceedances.index>start_loc,exceedances.index<end_loc)

timeseries.scatter(exceedances_dates[mask_x],exceedances[mask_x])

timeseries.set_ylabel("$PM_{2.5} \:[\mu g \: m^{-3}$]")
timeseries.set_xlabel("Time index")
# timeseries.set_title(site+" outlier threshold rolling average + 5.1 $\mu g \: m^{-3}$ ")
timeseries.set_title(site+" outlier threshold rolling average + 2.06 * std ")
plt.savefig("OutlierThreshStd.pdf")
# plt.savefig("OutlierThresh5.pdf")

# plt.scatter(pm25site)


