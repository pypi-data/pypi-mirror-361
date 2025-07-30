import os
import numpy as np
import torch
import pandas as pd
import xarray as xr

from .models import ConventionalCNN, ViT, ResNet50
from .func_ml import conventional_dataset_inference, Normalize
from torch.utils.data import DataLoader

def buoy_data_extract(folder_path, polar_data, date):
    """ Extracts buoy data from a specified folder and returns arrays of latitude, longitude, time, wind speed, and buoy names.
    
    Args:
        folder_path (str): Path to the folder containing buoy data files.
        polar_data (xarray.Dataset): Polar data containing latitude and longitude information. Used to snap buoy data to the nearest polar grid points.
        date (str): Date for which to extract buoy data, in 'YYYY-MM-DD' format.

    Returns:
        buoy_lat (np.ndarray): Array of buoy latitudes snapped to the nearest polar grid points.
        buoy_lon (np.ndarray): Array of buoy longitudes snapped to the nearest polar grid points
        buoy_time (np.ndarray): Array of buoy observation times.
        buoy_wind_speed (np.ndarray): Array of buoy wind speeds.
        buoy_name (np.ndarray): Array of buoy names.
    """
    buoy_lat = []
    buoy_lon = []
    buoy_wind_speed = []
    buoy_time = []
    buoy_name = []

    for file in os.listdir(folder_path):
        if ".cdf" in file:
            file_path = os.path.join(folder_path, file)
            opened = xr.open_dataset(file_path)
            lat, lon, time, wind_speed, name = form_arrays_buoy(opened, date)
            if np.sum(wind_speed) > 0:
                buoy_lat.extend(lat)
                buoy_lon.extend(lon)
                buoy_wind_speed.extend(wind_speed)
                buoy_time.append(time)
                buoy_name.append(name)

    buoy_lat = np.array(buoy_lat)
    buoy_lat = snap_to_nearest(buoy_lat, polar_data.latitude.values, cutoff=0.8)
    buoy_lon = np.array(buoy_lon)
    buoy_wind_speed = np.array(buoy_wind_speed)
    buoy_time = np.array(buoy_time)

    buoy_lon = np.where(buoy_lon > 180, buoy_lon - 360, buoy_lon)
    buoy_lon = snap_to_nearest(buoy_lon, polar_data.longitude.values, cutoff=0.8)

    return buoy_lat, buoy_lon, buoy_time, buoy_wind_speed, buoy_name


def form_arrays_buoy(buoy, date_choice):

    """
    Form arrays from buoy data for a specific date.

    Args:
        buoy (xarray.Dataset): Buoy data containing time, latitude, longitude, and wind speed.
        date_choice (str): Date for which to extract buoy data, in 'YYYY-MM

    Returns:
        lat (np.ndarray): Array of buoy latitudes.
        lon (np.ndarray): Array of buoy longitudes.
        time (np.ndarray): Array of buoy observation times in nanoseconds since epoch.
        wind_speed (np.ndarray): Array of buoy wind speeds.
        buoy_name (np.ndarray): Array of buoy names.
    
    """
    try:
        start = np.datetime64(date_choice) - np.timedelta64(5, "m")
        end = np.datetime64(date_choice) + np.timedelta64(5, "m")

        wind_speed = buoy.sel(time=slice(start, end)).WS_401.values.flatten()
        time = (
            buoy.sel(time=slice(start, end))
            .time.values.astype("datetime64[ns]")
            .astype("int64")
        )
        lat = np.full(len(wind_speed), buoy.lat.values)
        lon = np.full(len(wind_speed), buoy.lon.values)
        buoy_name = np.full(len(wind_speed), buoy.platform_code, dtype=object)
    except:
        wind_speed = np.array([])
        time = np.array([])
        lat = np.array([])
        lon = np.array([])
        buoy_name = np.array([])

        print("date selection unavailable")
    return lat, lon, time, wind_speed, buoy_name


def snap_to_nearest(values, reference_array, cutoff=1.0):
    """
    Snap an array of values to the nearest values in a reference array.
    If the difference is greater than the cutoff, the original value is returned.

    Args:
        values (np.ndarray): Array of values to snap.
        reference_array (np.ndarray): Array of reference values.
        cutoff (float): Maximum allowable difference for snapping.

    Returns:
        np.ndarray: Snapped values.
    """
    # Convert inputs to NumPy arrays for compatibility
    values = np.asarray(values)
    reference_array = np.asarray(reference_array)

    # Find the nearest reference value for each input value
    # Reshape reference_array to allow broadcasting
    reference_array = reference_array.reshape(1, -1)
    differences = np.abs(values.reshape(-1, 1) - reference_array)
    nearest_indices = np.argmin(differences, axis=1)
    nearest_values = reference_array.ravel()[nearest_indices]

    # Apply the cutoff condition
    snap_mask = np.abs(values - nearest_values) <= cutoff
    snapped_values = np.where(snap_mask, nearest_values, values)

    return snapped_values


def inference_run(
    images, model_parameters, model_path, normalization_factors
):
    
    """
    Runs inference on the provided images using the specified model parameters and normalization factors.

    Args:
        images (np.ndarray): Array of images to be used for inference.
        model_parameters (dict): Dictionary containing model parameters such as batch size, image size, channels
        model_path (str): Path to the pre-trained model file.
        normalization_factors (dict): Dictionary containing normalization factors such as mean and standard deviation.

    Returns:
        inference_output (np.ndarray): Array of inference outputs (wind speeds).
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    batch_size = model_parameters["batch_size"]
    image_height = model_parameters["image_size"]
    image_width = model_parameters["image_size"]
    in_channels = model_parameters["image_channels"]
    dropout_rate = model_parameters["dropout_rate"]
    model_choice = model_parameters["model_choice"]

    mean = normalization_factors["mean"]
    std = normalization_factors["std"]
    if model_choice == 'CNN':

        features_cnn = model_parameters["features_cnn"]
        kernel_size = model_parameters["kernel_size"]
        activation_cnn = model_parameters["activation_cnn"]
        activation_final = model_parameters["activation_final"]
        stride = model_parameters["stride"]

        print("model choice is CNN")
        model = ConventionalCNN(
            image_height,
            image_width,
            features_cnn,
            kernel_size,
            in_channels,
            activation_cnn,
            activation_final,
            stride,
            dropout_rate
        ).to(device)

    if model_choice == 'ViT':
        print('model choice is ViT')
        # Load the model
        model = ViT(
            img_size = (128, 128),
            patch_size = (8,8),
            n_channels = 1,
            d_model = 1024,
            nhead = 4,
            dim_feedforward = 2048,
            blocks = 8,
            mlp_head_units = [1024, 512],
            n_classes = 1,
        ).to(device)

    if model_choice == 'ResNet':
        model = ResNet50(num_classes=1, channels=1).to(device)



    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    inference_dataset = conventional_dataset_inference(
        images,
        transform=Normalize(mean,std),
    )
    inference_loader = DataLoader(inference_dataset, batch_size, shuffle=False)

    inference_output = inference_model(model, inference_loader, device)

    return inference_output

def inference_whole_image(
        path_folder,
        images,
        valid_lats,
        valid_lons,
        model_parameters,
        normalization_factors,
    ):
    for model in os.listdir(path_folder):
        if ".pth" in model:
            model_path = os.path.join(path_folder, model)
    print(model_path)

    print('INFO : starting inference')
    wind_speeds = inference_run(
        images, model_parameters, model_path, normalization_factors
    )

    lat_inference = np.reshape(valid_lats, (160, 340))
    lon_inference = np.reshape(valid_lons, (160, 340))
    wind_speeds = np.reshape(wind_speeds, (160, 340))


    return lat_inference, lon_inference, wind_speeds 
    

def update_buoy_comparison_csv(
    path_folder, time_choice, buoy_name, i,
    wind_speeds_inference_buoy, buoy_wind_speed, difference, percentage_cloud
):
    row = {
        'time': time_choice,
        'buoy': buoy_name[i],
        'model_output': wind_speeds_inference_buoy,
        'buoy_measurement': buoy_wind_speed[i],
        'difference': difference,
        'percentage_cloud': percentage_cloud,
    }

    file_path = os.path.join(path_folder, 'buoy_comparison.csv')

    # Check if file exists to control writing headers
    file_exists = os.path.exists(file_path)

    # Append a single-row DataFrame
    pd.DataFrame([row]).to_csv(
        file_path, mode='a', header=not file_exists, index=False
    )


def inference_model(model, inference_loader, device):
    """
    Perform inference on the model using the provided DataLoader and return the outputs. Same as train_model but for a fixed given model.

    Args:
        model (torch.nn.Module): The trained model to be used for inference.
        inference_loader (torch.utils.data.DataLoader): DataLoader for the inference dataset.
        device (torch.device): Device to run the model on (CPU or GPU).
        
    Returns:
        inference_outputs (numpy.ndarray): Outputs from the model on the inference dataset.
    """

    with torch.no_grad():  # Disable gradient calculation for inference

        inference_outputs = []

        for images in inference_loader:
            images = images.to(device)

            outputs = model(images).squeeze(-1)

            # Append outputs to the list
            inference_outputs.append(outputs)

        inference_outputs = torch.cat(inference_outputs, dim=0)
        inference_outputs = inference_outputs.cpu()
        inference_outputs = inference_outputs.numpy()

    return inference_outputs

