# Jessica Deng
# ENE 428 Final Project (SCAQMD)
# exceedance back trajectory modeling

library(splitr)
library(data.table)
library(htmlwidgets)
library(webshot)

exceedances <- data.frame(fread('ExceedancesWithHMSSmokeOverhead.csv', select = c("SiteNum", "ParameterCode", "Latitude", "Longitude", "DateLocal", "LocalSiteName")), stringsAsFactors = FALSE)
listofdfs <- list()
sitenums <- exceedances $SiteNum

# creating back trajectories for each exceedance
for (i in 1:nrow(exceedances)) {
  trajectory_model <-
      create_trajectory_model() %>%
      add_trajectory_params(
        lat = exceedances[i, "Latitude"],
        lon = exceedances[i, "Longitude"],
        height = 10,
        duration = 40,
        days = as.Date(exceedances[i, "DateLocal"], "%m/%d/%Y") +1,
        daily_hours = c(0,12),
        direction = "backward",
        met_type = "reanalysis",
        extended_met = FALSE
      ) %>%
      run_model()
    trajectory_tbl <- trajectory_model %>% get_output_tbl()
    trajectory_tbl <- as.data.frame(trajectory_tbl)
    listofdfs[[i]] <- trajectory_tbl
}

# finding max and min longitude/latitude
minlat <- min(listofdfs[[1]]["lat"])
maxlat <- max(listofdfs[[1]]["lat"])
minlon <- min(listofdfs[[1]]["lon"])
maxlon <- max(listofdfs[[1]]["lon"])
for (i in 1:1380) {
  if (min(listofdfs[[i]]["lat"]) < minlat) {
    minlat <- min(listofdfs[[i]]["lat"])
  } 
  if (max(listofdfs[[i]]["lat"]) > maxlat) {
    maxlat <- max(listofdfs[[i]]["lat"])
  }
  if (min(listofdfs[[i]]["lon"]) < minlon) {
    minlon <- min(listofdfs[[i]]["lon"])
  }
  if (max(listofdfs[[i]]["lon"]) > maxlon) {
    maxlon <- max(listofdfs[[i]]["lon"])
  }
  
}


# saving image files for trajectory plots
for (i in 1:length(listofdfs)){
  trajectory_tbl <- listofdfs[[i]]
  x<- trajectory_tbl %>% trajectory_plot()
  filename = paste0(listofdfs[[i]][1, "traj_dt"], ".html")
  imgname = paste0(listofdfs[[i]][1, "traj_dt"], "_", localsitenames[i], ".png")
  saveWidget(x, filename)
  webshot(filename, imgname)
  file.remove(filename)
}

# writing trajectories to csv files
for (i in 1:length(listofdfs)) {
  write.csv(listofdfs[[i]], file = paste0(as.Date(exceedances[i, "DateLocal"], "%m/%d/%Y"), "_", sitenums[i], ".csv"))
}



