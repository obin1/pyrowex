# pyrowex










## Automated Identification of Exceptional Air Pollution Events Caused by Wildfires

Course Project for ENE 428 – Air Pollution Fundamentals at University of Southern California

taught by Professor Jiachen Zhang

Sponsored by the South Coast Air Quality Management District (SCAQMD)

Jessica Deng, Obin Sturm, and Nina Zanghi 




## 1 Introduction

Over 17 million people live in the South Coast Air Basin, which is managed by the South Coast Air Quality Management District (SCAQMD).  This air basin suffers from some of the worst air quality in the US, including the highest ozone levels (South Coast Air Quality Management District, 2015).  Another pollutant of concern is fine particulate matter (PM2.5) which exposure to can result in cardiovascular and respiratory morbidity, and potentially mortality (Pope III and Dockey, 2006). Though air quality has improved over the last few decades, the South Coast Air Basin still has high PM2.5 levels and is designated as a serious nonattainment area for the federal 24 hour PM2.5 standard.

It is of regulatory interest to identify air pollution events that are out of SCAQMD’s control. These air quality events have to meet the EPA’s criteria if they are to be considered “exceptional events” (US EPA, 2016). The label of exceptional events removes those events from the overall air quality calculations. Any exceptional event must fulfill three criteria: the emissions from the event caused the monitored exceedance, the event was not reasonably controllable or preventable, and the event was either natural or caused by human activity but is unlikely to recur at the same location. One major cause for exceedance events in California is wildfires. Wildfires are large acute sources of primary PM2.5 and precursors to both ozone and PM2.5. It is important to identify which exceedances are caused by wildfires because then SCAQMD can focus on controllable sources for PM2.5. 

Determining if a wildfire caused an exceedance requires a holistic approach looking at all many factors that could indicate a wildfire. Different factors include the seasonality of PM2.5 and historical concentrations, trajectory analysis of winds, and wildfire emissions in relation to the air monitor (US EPA, 2016). After analysis of these factors, all historical PM2.5 exceedances in the SCAQMD jurisdiction were evaluated to determine whether wildfire smoke did not cause the monitored exceedance, may have caused the exceedance or did cause the exceedance. 

The demonstration of each exceedance as a potential exceptional event is resource intensive. The EPA guidelines for wildfire-induced ozone exceptional events require tailored analysis and a conceptual narrative for each event. Improved automation of this and similar processes using computational tools will free up the time of experts at air agencies. This would allow for better resource allocation and a standardized and streamlined workflow, potentially increasing the insight that can be gained from analysis of quality trends through generalizable tools.

In this report, we outline an initial implementation of pyrowex (Python Retrieval of Wildfire Exceptional Events, available here: https://github.com/obin1/pyrowex), an automated tool developed in the Python programming language to assess whether or not high PM2.5 events were caused by wildfires. 

## 2 Methodology

## 2.1 Categorization by the Python Retrieval of Wildfire Exceptional Events
As input, pyrowex takes a comma separated value (csv) file containing exceedances that have been shown to contain smoke in the same region as determined by the HMS smoke data product (https://www.ospo.noaa.gov/Products/land/hms.html), available from the National Oceanic and Atmospheric Administration (NOAA) National Environmental Satellite and Data Information Service. Additional input are daily monitor data for the time range of interest, calculated back trajectories for each case in the HMS exceedances file (summarized in section 2.3), and a fire map containing the date, location, area, and emission profile (summarized in section 2.4). Subsequent analysis in pyrowex determines whether each case in the input exceedance file 1) is a “distinctive level”, factoring in seasonality and 2) occurred downstream of an active fire. 

The output of pyrowex is the input csv file with four new columns appended. The first two are boolean and correspond to whether the case is at a distinctive level and downstream in a trajectory passing within 20km of a fire and reaching 10m.  If the case occurred downstream from a fire, a third column reports the fire’s distance-normalized primary PM2.5 emission (represented with the expression Q/D) in megagrams per kilometer, as outlined in the exceptional events guidance for ozone (US EPA, 2016).

The fourth and final column categorizes each case: 1 if wildfire smoke caused the monitored exceedance, 0.5 if wildfire smoke may have caused the monitored exceedance, and 0 if wildfire smoke did not cause the monitored exceedance. If the case is both a distinctive level and downwind from a fire, given the fact that HMS smoke was recorded overhead, it is assigned to be 1 (caused by a wildfire). If the case only fulfills one of the two, given that it also contained HMS smoke overhead, it is assigned 0.5 (maybe caused by a wildfire). Otherwise, it is 0 (as HMS smoke is not alone enough).

## 2.2 Assessment of distinctive level
The exceptional events demonstrations for ozone uses a tiered analysis to identify whether an exceedance reaches a “distinctive level” depending in part on the percentile value for each exceedance. Much of this requires manual assessment of each exceedance, with 5 years of data, and use of domain knowledge such as historic seasonal patterns of ozone formation (US EPA, 2016). The pyrowex tool instead accounts for seasonality fluctuation in an automated fashion by calculating a 90-day rolling average.  Outliers or distinctive levels are identified when they exceed a threshold above the rolling average.  After consultation with the SCAQMD, this threshold was chosen to be 2.06 standard deviations above the rolling average, with the standard deviation calculated over the range of all available data rather than only 5 years.  The 98th percentile of a normal distribution is reached by this threshold: though PM2.5 concentration distributions tend to have a long tail, the normal assumption was used in this analysis, though this design choice could be refined in subsequent versions of the tool. Figure 1 shows several years of distinctive exceedances at one site, for visualization of how the distinctive levels are identified.

![AnaheimOutlierThreshStd](https://user-images.githubusercontent.com/54367380/234380304-3932501f-f08b-4e3e-ad26-65ce26862ebd.jpg)
Figure 1. Automated identification of distinctive levels of PM2.5 in pyrowex, accounting for seasonality. 

## 2.3 Back Trajectory analysis

NOAA's Hybrid Single-Particle Lagrangian Integrated Trajectory model, or HYSPLIT was used to model air parcel trajectories in conjunction with the SplitR package in R. A back trajectory analysis was used to determine the origin of air parcels and if they had previously passed through areas with emissions due to wildfires. The methodology used in detecting these wildfire days was informed by Enayati Ehangar et al. (2021), with a 40-h period back trajectory computed at a height of 10 meters above the ground. The relatively low 10m choice is useful to demonstrate that the air parcel reached the ground: this complements the HMS smoke data, which cannot resolve whether or not the smoke is overhead or reaches the ground The R script utilizes NCEP (National Centers for Environmental Prediction) reanalysis meteorological data, but other meteorological data with less uncertainty and higher resolution may be used to generate more accurate back trajectories. The script models back trajectories for each exceedance, and writes unique trajectories to CSV files. In this process, it was found that within the HMS Exceedances data file given, there were duplicate combinations of latitude, longitude, and date, likely because the same exceedance event triggered multiple monitors. Ultimately, this computational analysis resulted in 243 unique back trajectories. From the data generated through modeling, it was determined that the back trajectory latitudes ranged between 31.34 and 45.442, and the longitudes fell between -127.43 and -110.858, which informed the domain for the fire maps and emissions inventories.

## 2.4 WFEIS Emissions

The Wildland Fire Emissions Inventory System (WFEIS) provides access to historical wildland fire emissions from across the US (French et al., 2014). The calculator tool allowed for the specification of location, date and emissions source. The source chosen was the NIFS/Geomac parameters provided by the National Wildfire Coordinating Group. This source had data from every year needed for the analysis. The data range chosen was from January 2007 through December 2020. The polygonal area of interest shown in Figure 2 was chosen to contain the domain of all 40 hour back trajectories, with the western boundary neglected, as the focus is on wildfires. The spatial aggregation chosen was the “burned area” because this provided essential location information. The data provided includes the PM2.5 emissions in Mg, the total area burned in km^2, and the location for where the wildfire occurred, allowing for the calculation of Q/D and comparison to trajectories. If the Q/D is higher than 1 there is a high probability that the fire is not a prescribed fire event but an uncontrollable fire (US EPA, 2016).  

<img width="283" alt="WFEIS-Polygon" src="https://user-images.githubusercontent.com/54367380/234380711-ff693245-0889-4acd-9388-7b745916d2ca.png">
Figure 2. A manually drawn WFEIS Polygon incorporating the southern, eastern, and northern boundaries such that it contains the domain of all trajectories from the back trajectory analysis. 

## 3 Results

## 3.1 Executive Summary
Using the logic and parameters from section 2, pyrowex identified 60 out of 1380 exceedances as exceptional events caused by a wildfire, as approximately 4.3% of all cases in the input csv file fulfilled all criteria. This strict requirement is one potential reason for a small number of wildfire exceptional events, however, the conservative nature of this estimate reduces the likelihood of false positives. There was much uncertainty: it was identified that 1243 out of 1380 exceedances were maybe caused by a wildfire, approximately 90.1% of the dataset. The remaining 5.6% were ruled out as having been caused by a fire. Potential reasons for this uncertainty are discussed in section 4.

Given all the required input data, pyrowex processes all 1380 cases in an automated fashion, requiring about 15 minutes on a personal computer. However, investigation of individual cases is still possible and can be useful, both for quality assurance and gaining insight.  The following section outlines one selected case that pyrowex identified as a wildfire exceptional event: the Azusa monitoring site during the Station fire in August 2009.

## 3.2 Case Study: Station Fire

The Station Fire occurred in the last week of August 2009 and burned nearly a quarter of the land mass of the Los Angeles National Forest (Thompson et al., 2009). This fire occurred in the absence of large winds, but quite close to populated regions of the South Coast Air Basin, including Azusa and Glendora, shown in Figure 3. 

<img width="519" alt="Azusa_WFEIS_1" src="https://user-images.githubusercontent.com/54367380/234381108-2af41c73-a05b-4df6-ba31-ac6108691ad1.png">
<img width="618" alt="Azusa_WFEIS_2" src="https://user-images.githubusercontent.com/54367380/234381111-4daa49aa-60f2-4522-87fe-ed9110f0b3dd.png">
Figure 3. Location of the station fire as mapped by the WFEIS emissions tool (French et al., 2014) used as input to the pyrowex tool.

The pyrowex tool identifies a measurement of the Azusa station (as well as other stations, including Glendora) exceedance during this time as being caused by wildfire emissions. The Azusa site recorded a PM2.5 measurement of 72 ug per cubic meter on August 26, 2009, which is visually distinguishable from the rolling average in Figure 4,  and second to last event in the displayed time range.

![AzusaOutlierThreshStd](https://user-images.githubusercontent.com/54367380/234381154-1e28c965-bd1b-446f-a066-586a73ef4076.jpg)
Figure 4. The Azusa site reached a distinctive level of 72 ug per cubic meter during the Station Fire.


In this case study, pyrowex also matches the location of the fire to several points of the back trajectory generated for this exceedance. As the fire had such high proximity to the Azusa monitoring site, the Q/D ratio is high, calculated as 90.6 Mg of PM2.5 primary emissions per kilometer.

<img width="625" alt="Backtraject" src="https://user-images.githubusercontent.com/54367380/234381444-5b8b8b3f-00d5-4ec7-a319-e9d1da062e49.png">
Figure 5. Output from SplitR – two 40 hour back trajectories from Azusa on August 26, 2009.


## 4 Discussion

The initial implementation of pyrowex identifies 60 out of 1380 cases as being caused by a wildfire. Large uncertainty could be addressed by exploration of the parameter space, which can be adjusted in pyrowex. The estimate of 4.3% of all cases in the csv file being wildfire exceptional events is conservative: we are quite confident in the designation of these cases as having been caused by wildfire smoke. However, 1243 (90.6%) of cases were designated as maybe caused by wildfire smoke, being either a distinctive level or downstream of a fire, but not both. All cases have HMS smoke overhead.  

Further analysis shows that 1239 of these 1243 cases were a distinctive level but not downstream from a fire according to the back trajectory data provided as input: only 4 cases were downstream of a fire but not a distinctive level. This could indicate that the threshold for determining outliers of above 2.06 standard deviations above the seasonal rolling average might not be strict enough, as an overwhelming fraction of the exceedances in the input csv file fulfilled this criterion.  

Alternatively, it could be that the radius for a trajectory passing near a point of 0.2 degrees (approximately 20 km) is too narrow. This was chosen from Appendix A3 of the EPA guidance on wildfire exceptional events for ozone, which discusses coarse meteorological grid resolution to HYSPLIT (around 40 km) as a source of uncertainty. We chose 20 km in either direction, half the length of such a grid cell, as the threshold under which a trajectory is close enough to a fire.  As a preliminary assessment of the sensitivity of the results to this parameter, we increased this to 1 degree (approximately 100 km) and found an increase to only 11% of cases as being caused by a wildfire.

A more likely cause of uncertainty is the sparsity of back trajectory data, which was only done at 1 time on the date of interest. In reality, more trajectories could have transported smoke to the monitor.  Future analysis could generate back trajectories every 3 hours on the dates of interest similarly to Enayati Ahangar (2021), which could be provided to pyrowex and potentially give a more realistic and filled in assessment of upstream wildfire sources.

## 5 Conclusions

This report focused on creation of an automated tool to identify monitored exceedances that were caused by wildfire smoke. By removing exceedances that were demonstrated to have been caused in part by wildfires, SCAQMD can focus on controllable sources. After analyzing the seasonality and historical concentrations of PM2.5, location of smoke, the back trajectory of air parcels, and the location of known wildfire emissions, 60 out of 1380 exceedances were determined to be caused by a wildfire. It was also determined that 1243 cases were maybe caused by a wildfire. There are many possible reasons for the uncertainty of these cases, which could be addressed by designing sensitivity tests assessing the parameter space. Increasing the set of possible back trajectories might capture more realistic wind patterns could improve on this tool. Further study would help determine which causes have the greatest effect on the classification of exceedances. 


## Author Contributions
JD led the trajectory analyses using SplitR, which produced csv files used as input to the pyrowex tool (Iannone, 2016).  NZ led the emissions analysis and generated preliminary fire maps using the Wildland Fire Emissions Information System (French et al., 2014), also provided as input. OS developed the pyrowex tool with both sources as input. All authors contributed to the analysis, presentation, and writing of the document.

## References
Enayati Ahangar, F., Pakbin, P., Hasheminassab, S., Epstein, S. A., Li, X., Polidori, A., & Low, J. (2021). Long-term trends of PM2.5 and its carbon content in the South Coast Air Basin: A focus on the impact of wildfires. Atmospheric Environment, 255, 118431. https://doi.org/10.1016/j.atmosenv.2021.118431

French, N.H.F., D. McKenzie, T. Erickson, B. Koziol, M. Billmire, K.A. Endsley, N.K.Y. Scheinerman, L. Jenkins, M.E. Miller, R. Ottmar, and S. Prichard (2014). "Modeling regional-scale fire emissions with the Wildland Fire Emissions Information System." Earth Interactions 18, no. 16 

Ianonne, Richard. (2016). splitr [Source Code]. https://github.com/rich-iannone/splitr

Pope III, C.A., Dockery, D.W., 2006. Health effects of fine particulate air pollution: lines that connect. Journal of the Air Waste Management Association. 56, 709–742.
South Coast Air Quality Management District, 2015. Multiple Air Toxics Exposure Study in the South Coast Air Basin (MATES IV).

Stein, A.F., Draxler, R.R, Rolph, G.D., Stunder, B.J.B., Cohen, M.D., and Ngan, F., (2015). NOAA’s HYSPLIT atmospheric transport and dispersion modeling system, Bull. Amer. Meteor. Soc., 96, 2059-2077, http://dx.doi.org/10.1175/BAMS-D-14-00110.1

Thompson, R., Kaplan, C., & Gomberg, D. (2009). The Station Fire: An Example of a Large Wildfire in the Absence of Significant Winds. National Weather Service Forecast Office.

US EPA (2016). Guidance on the Preparation of Exceptional Events Demonstrations for Wildfire Events that May Influence Ozone Concentrations https://www.epa.gov/sites/default/files/2019-08/documents/ee_prescribed_fire_final_guidance_-_august_2019.pdf 




