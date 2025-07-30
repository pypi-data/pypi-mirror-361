import xarray as xr
import numpy as np
import os
from datetime import datetime, timedelta


def extract_scatter_multisat(
    scatterometer_data_path, date, lat_range, lon_range,verbose=True
):
    
    """
    Extracts scatterometer data from multiple files (`.nc`) in a specified directory.

    Args:
        scatterometer_data_path (str): Path to the directory containing scatterometer data files.
        date (datetime): Date for which to extract data.
        lat_range (tuple): Latitude range (min, max) for filtering data.
        lon_range (tuple): Longitude range (min, max) for filtering data.
        verbose (bool): If True, prints progress information.

    Returns:
        tuple: A tuple containing:
            - list of datetime: observation times
            - list of float: latitudes
            - list of float: longitudes
            - list of float: wind speeds
    """

    observation_times = []
    observation_lats = []
    observation_lons = []
    observation_wind_speeds = []

    if verbose:
        print("INFO : Extracting scatterometer data from folder : ", scatterometer_data_path)
        print("___")

    for file in os.listdir(scatterometer_data_path):
        if ".nc" in file:
            # Open the file
            file_path = scatterometer_data_path + file
            polar_data = xr.open_dataset(file_path)
            (
                observation_times_local,
                observation_lats_local,
                observation_lons_local,
                observation_wind_speeds_local,
            ) = extract_scatter(
                polar_data, date, lat_range, lon_range, verbose=verbose
            )
            observation_times.extend(observation_times_local)
            observation_lats.extend(observation_lats_local)
            observation_lons.extend(observation_lons_local)
            observation_wind_speeds.extend(observation_wind_speeds_local)

    if verbose : 
        print("___")
        print(f"INFO : Total number of scatterometer data points: {len(observation_times)}")
    return (
        observation_times,
        observation_lats,
        observation_lons,
        observation_wind_speeds,
    )



def sort_by_time(lat_list, lon_list, time_list, wind_speed_list):
    """
    This function sorts the output of savedataseperated() by time.
    This allows for more efficient data processing and allows file caching for times that are represented by the same GOES file.

    Args:
        lat_list (numpy.ndarray): The latitude values of the scatterometer data.
        lon_list (numpy.ndarray): The longitude values of the scatterometer data.
        time_list (numpy.ndarray): The measurement time values of the scatterometer data.
        wind_speed_list (numpy.ndarray): The wind speed values of the scatterometer data.

    Returns:
        lat_list_sorted (numpy.ndarray): The sorted latitude values of the scatterometer data.
        lon_list_sorted (numpy.ndarray): The sorted longitude values of the scatterometer data.
        time_list_sorted (numpy.ndarray): The sorted measurement time values of the scatterometer data.
        wind_speed_list_sorted (numpy.ndarray): The sorted wind speed values of the scatterometer data.

    """
    # Get the indices that would sort the measurement_time array
    sorted_indices = np.argsort(time_list)

    # Reorder the arrays using the sorted indices
    time_list_sorted = time_list[sorted_indices]
    lat_list_sorted = lat_list[sorted_indices]
    lon_list_sorted = lon_list[sorted_indices]
    speed_list_sorted = wind_speed_list[sorted_indices]

    return lat_list_sorted, lon_list_sorted, time_list_sorted, speed_list_sorted


def savedataseperated(ScatterData, main_parameter,verbose=True):
    """
    This function extracts the valid lon / lat / measurement time and the main parameter from ever pixel
    of the scatterometer data and saves it to a numpy file.

    Args:
        ScatterData (xarray.Dataset): The ASCAT dataset containing the scatterometer data.
        main_parameter (xarray.DataArray): The main parameter to be saved. This can be a classification / wind speed / wind direction etc.

    Returns:

        lat_list (numpy.ndarray): The latitude values of the scatterometer data.
        lon_list (numpy.ndarray): The longitude values of the scatterometer data.
        time_list (numpy.ndarray): The measurement time values of the scatterometer data.
        main_parameter_list (numpy.ndarray): The main parameter values of the scatterometer data.

    this function saves the data locally to a folder called data_processed_scat
    """
    lat_full, lon_full, time_full = ScatterData.indexes.values()
    measurement_time_full = ScatterData.measurement_time

    lat_full = np.array(lat_full)
    lon_full = np.array(lon_full)
    measurement_time_full = np.array(measurement_time_full)
    main_parameter = np.array(main_parameter)

    index = np.argwhere(~np.isnan(main_parameter))

    index_list = []
    lat_list = []
    lon_list = []
    time_list = []
    wind_speed_list = []

    name_scatter = ScatterData.source

    for t, i, j in index:

        # print(t,'= time', i,'=row', j, '=column')
        index_list.append((t, i, j))

        # print(measurement_time_full[t, i, j].astype('datetime64[ns]'))
        time_list.append(measurement_time_full[t, i, j])

        # print(lat_full[i])
        lat_list.append(lat_full[i])

        # print(lon_full[j])
        lon_list.append(lon_full[j])

        # print(AllWindSpeeds[t, i, j])
        wind_speed_list.append(main_parameter[t, i, j])

    lat_list = np.array(lat_list)
    lon_list = np.array(lon_list)
    time_list = np.array(time_list)
    wind_speed_list = np.array(wind_speed_list)

    lat_list, lon_list, time_list, wind_speed_list = sort_by_time(
        lat_list, lon_list, time_list, wind_speed_list
    )
    if verbose:
        save_overpass_time(time_list,name_scatter)    

    return lat_list, lon_list, time_list, wind_speed_list

def save_overpass_time(time_list,name_scatter):
    """
    This function prints the overpass time of the scatterometer.

    Args:
        time_list (numpy.ndarray): The measurement time values of the scatterometer data.
        name_scatter (str): The name of the scatterometer data source (e.g. ASCAT, HYSCAT etc).

    Returns:
        None 

    """
    formated_time = time_list.astype('datetime64[ns]')
    hour_minute = formated_time.astype('datetime64[m]')
    unique_hour_minute = np.unique(hour_minute)

    filtered = [unique_hour_minute[0]]

    delta = np.timedelta64(1, 'h')

    for time in unique_hour_minute[1:]:
        if time - filtered[-1] >= delta:
            filtered.append(time)

    time_only = []
    for time in filtered:
        time = str(time).split('T')[1]
        time_only.append(time)
    print(f"ORBIT : {name_scatter} overpass time : {time_only}")


def extract_scatter(
    polar_data,
    date,
    lat_range,
    lon_range,
    verbose=True,
    main_variable="wind_speed",
):
    """
    This function extracts the scatterometer data from the polar_data dataset for the given time range, latitude range and longitude range.
    The function then saves the data into 4 numpy files : time of observation, latitude, longitude and main variable.

    Args:
        polar_data (xarray.Dataset): The scatterometer dataset (ASCAT, HYSCAT etc).
        date (numpy.datetime64): The time of the scatterometer data.
        lat_range (tuple): The latitude range of the scatterometer data.
        lon_range (tuple): The longitude range of the scatterometer data.
        verbose (bool): If True, the function will print the progress of the extraction.
        main_variable (str): The main variable to be extracted from the scatterometer data. This can be wind speed, wind direction, classification etc.

    Returns:
        observation_times (numpy.ndarray): The time of observation of the scatterometer data.
        observation_lats (numpy.ndarray): The latitude of the scatterometer data.
        observation_lons (numpy.ndarray): The longitude of the scatterometer data.
        observation_main_parameter (numpy.ndarray): main parameter extracted (wind_speed).

    """

    polar = polar_data.sel(
        time=slice(date, date),
        latitude=slice(lat_range[0], lat_range[1]),
        longitude=slice(lon_range[0], lon_range[1]),
    )

    seperated_scatter = savedataseperated(polar, polar[main_variable],verbose=verbose)

    observation_times = seperated_scatter[2]
    observation_lats = seperated_scatter[0]
    observation_lons = seperated_scatter[1]
    observation_wind_speeds = seperated_scatter[3]

    

    return (
        observation_times,
        observation_lats,
        observation_lons,
        observation_wind_speeds,
    )

