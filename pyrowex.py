#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 21:23:45 2023

@author: psturm
"""

""" 

pyrowex: Python Retrieval of Wildfire Exceptional Events

Designed to be standard agnostic: 
    rather than only mattering for exceedances (35.7) apply to any deviation above a certain percentile

"""

import numpy as np
import pandas as pd
import os 
import matplotlib.pyplot as plt
import datetime
from geopy import distance
# import geopandas as gpd


# Master file of exceedances with HMS smoke overhead
dfHMS = pd.read_csv("Data for SCAQMD Project/ExceedancesWithHMSsmokeOverhead.csv")

# Emissions
dfEmissions = pd.read_csv("WFEIS_NIFS_aggregate_2007-01-01-2021-01-06_burnedarea_by_date_202304230344_YM8F.csv")
burned_radius = (dfEmissions["area_km2"]/np.pi)**0.5 * (1/95) # calculate burned radius in degrees, assuming latitude of 31.34


parameter_codes = dfHMS["ParameterCode"].unique()
sites = dfHMS['LocalSiteName'].unique()

# Initialize new columns
DistinctiveLevel = [0]*len(dfHMS)
FireAlongTrajectory = [0]*len(dfHMS)
QDratio = [0]*len(dfHMS)
Category = [0]*len(dfHMS)

# Some parameters
outlier_threshold = 2.06 # How many standard deviations for a measurement to be considered an outlier?

# How close does a trajectory need to be to an actively burning area? 
# Default: 20 km (on each side), pulling from Appendix A3 (Grid cells are usually 40 km in width and length)
# https://www.epa.gov/sites/default/files/2018-10/documents/exceptional_events_guidance_9-16-16_final.pdf
proximity_to_fire = 0.2



for ind in range(0,len(dfHMS)):
    print("analyzing case " + str(ind+1) + " out of " + str(len(dfHMS)))
    site = dfHMS["LocalSiteName"][ind]
    level = dfHMS["ArithmeticMean"][ind]
    code = str(dfHMS["ParameterCode"][ind])
    date = dfHMS["DateLocal"][ind]
    lat = dfHMS["Latitude"][ind]
    lon = dfHMS["Longitude"][ind]
    sitenum = dfHMS["SiteNum"][ind]
    
    
    #%% Assess outliers: does this measurement qualify as a "distinctive level"?
    filelist = []
    for file in os.listdir('Data for SCAQMD Project/'):
        if file[0:11] == "daily_"+code:
            filelist.append(file)        
    filelist.sort()
    
    i = 0
    for file in filelist:
        pm25temp = pd.read_csv("Data for SCAQMD Project/"+file)#,parse_dates=["Date Local"])
        # Site Num added because last row had no Local Site Name
        if dfHMS["SampleDuration"][ind] == 24:
            mask =  ( (pm25temp['Local Site Name'] == site) | \
            (pm25temp['Site Num'] == sitenum) ) & \
            ( (pm25temp['Sample Duration'] == '24 HOUR')  | \
            (pm25temp['Sample Duration'] == '24-HR BLK AVG') )
        elif dfHMS["SampleDuration"][ind] == 1:
            mask = ( (pm25temp['Local Site Name'] == site) | \
            (pm25temp['Site Num'] == sitenum) ) & \
            (pm25temp['Sample Duration'] == '1 HOUR')
            
        i += 1
        if i == 1:
            pm25site = pm25temp[mask]
    
        else:
            pm25site = pd.concat((pm25site,pm25temp[mask]),
                               ignore_index=True)
            
    rolling_ave = pm25site["Arithmetic Mean"].rolling(90,min_periods=1,closed='both').mean()
    std = pm25site["Arithmetic Mean"].std()
    # Rolling percentile (98th, can be adjusted)
    # rolling_pct = pm25site["Arithmetic Mean"].rolling(90,min_periods=1,closed='both').quantile(.98)
    # Rolling Standard Deviation
    # rolling_std = pm25site["Arithmetic Mean"].rolling(90,min_periods=1,closed='both').std()
    # Standard deviation over entire available time period

    if level > (rolling_ave[pm25site[pm25site["Date Local"]==date].index[0]] + outlier_threshold*std):
        DistinctiveLevel[ind] = 1
    
    #%% Trajectory and Emissions
    dfTraj = pd.read_csv("HYSPLIT_Trajectories/"+date+"_"+str(sitenum)+".csv")
    prevday = (datetime.date(*map(int, date.split('-'))) - datetime.timedelta(1)).strftime('%Y-%m-%d')
    
    
    for traj_i in range(0,len(dfTraj)):
        fire_mask = ( (date == dfEmissions["date"]) | \
                  (date == prevday) ) &  \
               (abs(dfTraj["lon"][traj_i] - dfEmissions["longitude"]) < (proximity_to_fire+burned_radius) ) & \
               (abs(dfTraj["lat"][traj_i] - dfEmissions["latitude"]) < (proximity_to_fire+burned_radius))
        if any( fire_mask ):
            FireAlongTrajectory[ind] = 1
            print("Fire along trajectory for "+site+" on "+date)
            
            # Calculate Q/D ratio
            fireloc = (dfEmissions["latitude"][fire_mask].values, dfEmissions["longitude"][fire_mask].values)
            D = [distance.distance( (fireloc[0][i],fireloc[1][i]), (lat,lon) ).km for i in range(0,sum(fire_mask))]
            Q = dfEmissions["consume_output__pm25_mg"][fire_mask].values
            QDratio[ind] += np.sum(Q/D)
    
    #%% Categorical assignment
    # Wildfire exceptional event: 1
    # Possibly caused by wildfire: 0.5 (any nonzero new category paired with smoke overhead)
    # Likely not caused by wildfire: 0
    
    if FireAlongTrajectory[ind] == 1: 
        if DistinctiveLevel[ind] == 1: # then it is Tier 1
            Category[ind] = 1
        # elif QDratio[ind] > 100*(35/70): # scale for ozone QD ratio
        # note only studying primary pm: 
        # exclusion of precursors is a competing effect against deposition, dilution
        else:
            Category[ind] = 0.5
    elif DistinctiveLevel[ind] == 1: # if this is a distinctive level and there is smoke overhead, then maybe was caused by wildfire
        Category[ind] = 0.5
        
            
    
    
# Write new columns to dataframe and save the updated csv file
print("writing new CSV file")
dfHMS["DistinctiveLevel"] = DistinctiveLevel
dfHMS["FireAlongTrajectory"] = FireAlongTrajectory
dfHMS["QDratio"] = QDratio
dfHMS["Category"] = Category
dfHMS.to_csv("ExceedancesCategorization.csv",index=False)

print("success! file saved in current directory as ExceedancesCategorization.csv")
    


# plot time range

def plot_timerange(ind=1):
    print("analyzing case " + str(ind) + " out of " + str(len(dfHMS)))
    site = dfHMS["LocalSiteName"][ind]
    # level = dfHMS["ArithmeticMean"][ind]
    code = str(dfHMS["ParameterCode"][ind])
    # date = dfHMS["DateLocal"][ind]
    # lat = dfHMS["Latitude"][ind]
    # lon = dfHMS["Longitude"][ind]
    sitenum = dfHMS["SiteNum"][ind]
    filelist = []
    for file in os.listdir('Data for SCAQMD Project/'):
        if file[0:11] == "daily_"+code:
            filelist.append(file)        
    filelist.sort()
    
    i = 0
    for file in filelist:
        pm25temp = pd.read_csv("Data for SCAQMD Project/"+file)#,parse_dates=["Date Local"])
        # Site Num added because last row had no Local Site Name
        if dfHMS["SampleDuration"][ind] == 24:
            mask =  ( (pm25temp['Local Site Name'] == site) | \
            (pm25temp['Site Num'] == sitenum) ) & \
            ( (pm25temp['Sample Duration'] == '24 HOUR')  | \
            (pm25temp['Sample Duration'] == '24-HR BLK AVG') )
        elif dfHMS["SampleDuration"][ind] == 1:
            mask = ( (pm25temp['Local Site Name'] == site) | \
            (pm25temp['Site Num'] == sitenum) ) & \
            (pm25temp['Sample Duration'] == '1 HOUR')
            
        i += 1
        if i == 1:
            pm25site = pm25temp[mask]
    
        else:
            pm25site = pd.concat((pm25site,pm25temp[mask]),
                               ignore_index=True)
            
    rolling_ave = pm25site["Arithmetic Mean"].rolling(90,min_periods=1,closed='both').mean()
    std = pm25site["Arithmetic Mean"].std()
    site = 'Azusa'
    code = str(88502)
    # code = str(88101)
    start_date = '2008-01-01'
    end_date = '2009-12-30'
    start_loc = pm25site.loc[pm25site['Date Local'] == start_date].index[0] #0 
    end_loc = pm25site.loc[pm25site['Date Local'] == end_date].index[0] # len(pm25site['Date Local'])  #731 #
    
    threshold = 35.7
    exceedances = pm25site.loc[pm25site["Arithmetic Mean"]>threshold]["Arithmetic Mean"]
    exceedances_dates = pm25site.loc[pm25site["Arithmetic Mean"]>threshold]["Date Local"]
    
    
    
    fig, timeseries = plt.subplots()
    
    dates = pd.to_datetime(pm25site['Date Local'][start_loc:end_loc])
    
    timeseries.plot(dates,rolling_ave[start_loc:end_loc],color='red',label="Rolling mean")
    time = pd.to_datetime(pm25site['Date Local'][start_loc:end_loc])
    # 2.06 standard deviations is the 98% percentile for a normal curve
    timeseries.fill_between(dates, rolling_ave[start_loc:end_loc],
                      rolling_ave[start_loc:end_loc]+2.06*std,
                      alpha=0.2,color='red', label = "Within 2.06 std")
    mask_x = np.logical_and(exceedances.index>start_loc,exceedances.index<end_loc)
    
    timeseries.scatter(exceedances_dates[mask_x],exceedances[mask_x],label="Exceedances")
    
    timeseries.set_ylabel("$PM_{2.5} \:[\mu g \: m^{-3}$]")
    timeseries.set_xlabel("Time index")
    timeseries.set_title(site+" distinctive level analysis")
    plt.gcf().autofmt_xdate()
    plt.legend()
    # plt.show()
    plt.savefig(site+"OutlierThreshStd.pdf")
    # timeseries.set_title(site+" outlier threshold rolling average + 5.1 $\mu g \: m^{-3}$ ")
    # plt.savefig("OutlierThresh5.pdf")




