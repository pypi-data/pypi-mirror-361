
import numpy as np
import pandas as pd
import os

def vectorized_solar_angles(lat, lon, time_utc):

    """
    This function calculates the solar zenith angle (SZA) and solar azimuth angle (SAA) for a given latitude, longitude, and time. This is an archived function. Current implementation does not use solar angles but only image input.

    Args:
        lat (numpy.ndarray): The latitude values of the scatterometer data.
        lon (numpy.ndarray): The longitude values of the scatterometer data.
        time_utc (numpy.ndarray): The observation times in UTC.

    Returns:
        sza (numpy.ndarray): The solar zenith angle in degrees.
        saa (numpy.ndarray): The solar azimuth angle in degrees.
    """

    # Convert time to Julian Day
    timestamp = pd.to_datetime(time_utc).tz_localize(None)
    jd = (
        timestamp.astype("datetime64[ns]").astype(np.int64) / 86400000000000 + 2440587.5
    )
    d = jd - 2451545.0  # Days since J2000

    # Mean longitude, mean anomaly, ecliptic longitude
    g = np.deg2rad((357.529 + 0.98560028 * d) % 360)  # Mean anomaly
    q = np.deg2rad((280.459 + 0.98564736 * d) % 360)  # Mean longitude
    L = (q + np.deg2rad(1.915) * np.sin(g) + np.deg2rad(0.020) * np.sin(2 * g)) % (
        2 * np.pi
    )  # Ecliptic long

    # Obliquity of the ecliptic
    e = np.deg2rad(23.439 - 0.00000036 * d)

    # Sun declination
    sin_delta = np.sin(e) * np.sin(L)
    delta = np.arcsin(sin_delta)

    # Equation of time (in minutes)
    E = 229.18 * (
        0.000075
        + 0.001868 * np.cos(g)
        - 0.032077 * np.sin(g)
        - 0.014615 * np.cos(2 * g)
        - 0.040849 * np.sin(2 * g)
    )

    # Convert time to fractional hours (UTC)
    fractional_hour = timestamp.hour + timestamp.minute / 60 + timestamp.second / 3600

    # Solar time correction
    time_offset = E + 4 * lon  # lon in degrees
    tst = fractional_hour * 60 + time_offset  # True Solar Time in minutes
    ha = np.deg2rad((tst / 4 - 180) % 360)  # Hour angle in radians

    # Convert lat/lon to radians
    lat_rad = np.deg2rad(lat)

    # Solar zenith angle
    cos_zenith = np.sin(lat_rad) * np.sin(delta) + np.cos(lat_rad) * np.cos(
        delta
    ) * np.cos(ha)
    zenith = np.rad2deg(np.arccos(np.clip(cos_zenith, -1, 1)))  # in degrees

    # Solar saa angle
    sin_saa = -np.sin(ha) * np.cos(delta)
    cos_saa = np.cos(lat_rad) * np.sin(delta) - np.sin(lat_rad) * np.cos(
        delta
    ) * np.cos(ha)
    saa = np.rad2deg(np.arctan2(sin_saa, cos_saa))
    saa = (saa + 360) % 360  # Normalize

    return zenith, saa


def create_folder(experiment_name):
    """
    Create a folder for saving results based on the experiment name.

    Args:
        experiment_name (str): Name of the experiment to create a folder for.
        If the folder already exists, it will not be created again.

    Returns:
        str: Path to the created folder.
    """

    path_folder = f"./results_folder/model_day_{experiment_name}"

    if not os.path.exists(path_folder):
        os.makedirs(path_folder)
        print(f"Folder created at {path_folder}")

    return path_folder


def create_folder_indice(folder_name):
    """
    Create a folder for saving satellite indices.

    Args:
        folder_name (str): Name of the folder to create.
        If the folder already exists, it will not be created again.

    Returns:
        str: Path to the created folder.
    """

    path_folder = f"./{folder_name}"

    if not os.path.exists(path_folder):
        os.makedirs(path_folder)
        print(f"Folder created at {path_folder}")

    return path_folder


def filter_invalid(
    images,
    numerical_data,
    min_nonzero_pixels=50,
):
    
    """
    This function filters out invalid images and corresponding numerical data based on two criteria:
    1) The sum of pixel values in the image is not zero (i.e., the image is not completely empty).
    2) The number of non-zero pixels in the image is greater than or equal to a specified minimum threshold (default is 50).

    Args:
        images (numpy.ndarray): A 4D numpy array of shape (num_images, num_channels, height, width) containing the GOES images.
        numerical_data (dict): A dictionary containing numerical data associated with the images. The keys should match the dimensions of the images.
        min_nonzero_pixels (int): The minimum number of non-zero pixels required for an image to be considered valid. Default is 50.

    Returns:
        filtered_images (numpy.ndarray): A 4D numpy array of shape (num_valid_images, num_channels, height, width) containing the filtered GOES images.
        filtered_numerical_data (dict): A dictionary containing the numerical data associated with the valid images.

    """
    # Sums of pixel values in each image
    sums_images = [np.nansum(x) for x in images]

    # Counts of non-zero pixels in each image
    nonzero_counts = [np.count_nonzero(x) for x in images]

    # Build a "mask_invalid" array of indices that fail any criterion:
    # 1) sum == 0 (completely empty)
    # 2) nonzero pixel count < min_nonzero_pixels (not enough data)

    mask_valid = np.where(
        (np.array(sums_images) != 0) & (np.array(nonzero_counts) >= min_nonzero_pixels)
    )[0]

    # Delete the invalid entries from each array
    filtered_numerical_data = {
        key: value[mask_valid] for key, value in numerical_data.items()
    }
    filtered_images = images[mask_valid]
    n_removed_images = len(images) - len(filtered_images)

    print(
        "INFO : Filtered invalid images. Removed {} entries.".format(
            n_removed_images
        )
    )
    return (
        filtered_images,
        filtered_numerical_data,
    )


def fill_nans(images):
    """
    This function fills NaN values in the images with zeros. (This is simply np.nan_to_num)

    Args:
        images (numpy.ndarray): A 4D numpy array of shape (num_images, num_channels, height, width) containing the GOES images.
    
    Returns:
        images (numpy.ndarray): A 4D numpy array with NaN values replaced by zeros.
    """
    images = np.nan_to_num(images, nan=0.0)
    print("INFO : Filled nans")
    return images


def filter_nighttime(
    observation_times,
    observation_lats,
    observation_lons,
    observation_wind_speeds,
    min_hour=10,
    max_hour=19,
    verbose=True,
):
    """
    This function filters the scatterometer data to only include observations that were made during daylight hours.
    The function checks the hour of each observation time and only keeps those that fall within the specified
    range (default is 10 to 19, which corresponds to 10 AM to 7 PM UTC).

    Args:
        observation_times (numpy.ndarray): The times of observation of the scatterometer data.
        observation_lats (numpy.ndarray): The latitudes of the scatterometer data.
        observation_lons (numpy.ndarray): The longitudes of the scatterometer data.
        observation_wind_speeds (numpy.ndarray): The wind speeds of the scatterometer data.
        min_hour (int): The minimum hour of the day to include (default is 10).
        max_hour (int): The maximum hour of the day to include (default is 19).
        verbose (bool): If True, prints the number of valid scatterometer data points at daylight.
    
    Returns:
        valid_times (list): A list of valid observation times that fall within the specified hour range.
        valid_lats (list): A list of valid latitudes corresponding to the valid observation times
        valid_lons (list): A list of valid longitudes corresponding to the valid observation times.
        valid_wind_speeds (list): A list of valid wind speeds corresponding to the valid observation times.

    """

    valid_times = []
    valid_lats = []
    valid_lons = []
    valid_wind_speeds = []

    for idx in range(len(observation_times)):
        only_hour = int(
            observation_times[idx].astype("datetime64[ns]").astype("str")[11:13]
        )
        if min_hour <= only_hour <= max_hour:
            valid_times.append(observation_times[idx])
            valid_lats.append(observation_lats[idx])
            valid_lons.append(observation_lons[idx])
            valid_wind_speeds.append(observation_wind_speeds[idx])

    if verbose:
        print(f"INFO : Total number of scatterometer data points at daylight : {len(valid_times)}")
    return valid_times, valid_lats, valid_lons, valid_wind_speeds




def package_data(
    images,
    numerical_data,
    filter=True,
    solar_conversion=False,
    verbose=True
):
    """
    This function packages the images and numerical data into a format that can be used for training a machine learning model.
    The function will filter out invalid images and fill in any NaN values. (Invalid images = empty images from GOES data)
    The function will also convert the observation times, latitudes and longitudes to solar angles (sza, saa) if solar_conversion is set to True.
    The function will return the images and numerical data in a numpy array format.

    Args:
        images (numpy.ndarray): The GOES images corresponding to the observation data.
        numerical_data (dict): A dictionary containing the numerical data corresponding to the observation data. The keys should include "observation_lats", "observation_lons", "observation_times" and optionally "wind_speeds".
        filter (bool): If True, the function will filter out invalid images and fill in Nan values. Default is True.
        solar_conversion (bool): If True, the function will convert the observation times, latitudes and longitudes to solar angles (sza, saa). Default is False. (Not used in current implementation, but kept in case of future use)
        verbose (bool): If True, the function will print progress information. Default is True.

    Returns:
        images (numpy.ndarray): The GOES images corresponding to the observation data.
        numerical_data (numpy.ndarray): The numerical data corresponding to the observation data. (sza, saa, main_parameter if solar_conversion is set to True or lat, lon, time, wind_speeds if solar_conversion is set to False)

    """
    if filter:
        (images, numerical_data) = filter_invalid(images, numerical_data)
        images = fill_nans(images)

    if solar_conversion:
        observation_lats = numerical_data["observation_lats"]
        observation_lons = numerical_data["observation_lons"]
        observation_times = numerical_data["observation_times"]

        sza, saa = vectorized_solar_angles(
            observation_lats, observation_lons, observation_times
        )

        sza_rad = np.deg2rad(sza)
        sza_sin = np.sin(sza_rad)
        sza_cos = np.cos(sza_rad)

        saa_rad = np.deg2rad(saa)
        saa_sin = np.sin(saa_rad)
        saa_cos = np.cos(saa_rad)

        # Add the solar angles to the numerical data dictionary
        
        numerical_data["sza_sin"] = sza_sin
        numerical_data["sza_cos"] = sza_cos
        numerical_data["saa_sin"] = saa_sin
        numerical_data["saa_cos"] = saa_cos

        print("Data Preparation : converted to solar angles (sza, saa)")
        print("Data Preparation : returning images, numerical_data")
        return images, numerical_data

    else:

        return images, numerical_data
