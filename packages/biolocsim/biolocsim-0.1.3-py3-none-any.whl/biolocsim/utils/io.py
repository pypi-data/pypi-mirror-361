import os
from collections import OrderedDict

import h5py
import numpy as np
import tifffile
import yaml

# Setup to dump OrderedDict to YAML like a regular dict
yaml.SafeDumper.add_representer(
    OrderedDict, lambda dumper, data: dumper.represent_mapping("tag:yaml.org,2002:map", data.items())
)

# Setup to load YAML into OrderedDict
yaml.SafeLoader.add_constructor("tag:yaml.org,2002:map", lambda loader, node: OrderedDict(loader.construct_pairs(node)))


def save_point_cloud_to_csv(file_path: str, point_cloud: np.ndarray, include_id: bool = True, precision: str = "%.3f"):
    """
    Saves a point cloud to a CSV file.

    Args:
        file_path (str): The path to the output CSV file.
        point_cloud (np.ndarray): The point cloud data, expected to be shape (N, 3) or (N, 4).
        include_id (bool): If True and the point cloud has 4 columns, saves all columns.
                           If False, saves only the first 3 (x, y, z) columns.
                           Defaults to True.
        precision (str): The format string for floating point numbers.
    """
    if point_cloud.ndim != 2 or point_cloud.shape[1] < 3:
        raise ValueError("point_cloud must be a 2D array with at least 3 columns (x, y, z).")

    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    num_columns = point_cloud.shape[1]

    if include_id and num_columns >= 4:
        # Save x, y, z, and id
        data_to_save = point_cloud[:, :4]
        header = "x [nm],y [nm],z [nm],id"
        # Ensure format specifier matches number of columns
        fmt = [precision] * 3 + ["%d"]
    else:
        # Save only x, y, z
        data_to_save = point_cloud[:, :3]
        header = "x [nm],y [nm],z [nm]"
        fmt = [precision] * 3

    np.savetxt(
        file_path,
        data_to_save,
        delimiter=",",
        fmt=fmt,
        header=header,
        comments="",
    )
    print(f"Point cloud saved to {file_path}")


def save_volume_as_tiff(volume: np.ndarray, file_path: str):
    """
    Saves a 3D numpy array as a multi-page TIFF file.

    Args:
        volume (np.ndarray): The 3D volume data (e.g., voxel grid).
        file_path (str): The path to the output TIFF file.
    """
    if volume.ndim != 3:
        raise ValueError("Input volume must be a 3D numpy array.")

    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Tifffile expects (planes, height, width), which matches numpy's (z, y, x)
    tifffile.imwrite(file_path, volume.astype(np.uint8) * 255)
    print(f"Volume saved as TIFF to {file_path}")


def save_2d_mask_as_tiff(mask: np.ndarray, file_path: str):
    """
    Saves a 2D boolean or integer mask as a TIFF file.

    Args:
        mask (np.ndarray): The 2D mask data (e.g., XY projection).
        file_path (str): The path to the output TIFF file.
    """
    if mask.ndim != 2:
        raise ValueError("Input mask must be a 2D numpy array.")

    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Convert boolean or integer mask to uint8 for saving
    image_to_save = mask.astype(np.uint8) * 255

    tifffile.imwrite(file_path, image_to_save)
    print(f"2D mask saved as TIFF to {file_path}")


def save_aggregated_mask(
    mask: np.ndarray,
    base_path: str,
    formats: list,
    dataset_name: str = "mask",
    dtype: str = "uint8",
    compression: str = "gzip",
):
    """
    Saves a 2D or 3D mask in specified formats (TIFF and/or HDF5).

    Args:
        mask (np.ndarray): The mask data to save.
        base_path (str): The base file path without extension.
        formats (list): A list of strings, e.g., ['tiff', 'hdf5'].
        dataset_name (str): The name of the dataset inside the HDF5 file.
    """
    output_dir = os.path.dirname(base_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    image_to_save = mask.astype(dtype) * 255 if mask.dtype == bool else mask.astype(dtype)

    if "tiff" in formats:
        tiff_path = f"{base_path}.tiff"
        tifffile.imwrite(tiff_path, image_to_save)
        print(f"Mask saved as TIFF to {tiff_path}")

    if "hdf5" in formats:
        hdf5_path = f"{base_path}.hdf5"
        with h5py.File(hdf5_path, "w") as f:
            f.create_dataset(dataset_name, data=image_to_save, compression=compression)
        print(f"Mask saved as HDF5 to {hdf5_path}")


def save_instance_masks_to_hdf5(masks_list: list, file_path: str, dataset_name: str = "instance_masks"):
    """
    Saves a list of individual boolean masks as a stack in an HDF5 file.

    Args:
        masks_list (list): A list of 3D numpy arrays (boolean masks).
        file_path (str): The full path to the output HDF5 file.
        dataset_name (str): The name for the dataset in the HDF5 file.
    """
    if not masks_list:
        print("Warning: Instance masks list is empty. Nothing to save.")
        return

    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Stack the boolean masks into a single (N, Z, Y, X) array
    stacked_masks = np.stack(masks_list, axis=0).astype(np.uint8)

    with h5py.File(file_path, "w") as f:
        f.create_dataset(
            dataset_name, data=stacked_masks, compression="gzip", chunks=True  # Good practice for large, stackable data
        )
    print(f"Instance masks saved to {file_path}")


def save_config_to_yaml(config: dict, file_path: str):
    """
    Saves a configuration dictionary to a YAML file, preserving order.

    Args:
        config (dict): The configuration dictionary. If not an OrderedDict, it will be converted.
        file_path (str): The path to the output YAML file.
    """
    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Convert to OrderedDict to ensure order is preserved if it's a regular dict
    config_ordered = OrderedDict(config)

    with open(file_path, "w") as f:
        yaml.dump(config_ordered, f, Dumper=yaml.SafeDumper, default_flow_style=False, sort_keys=False)
    print(f"Configuration saved to {file_path}")


def load_config_from_yaml(file_path: str) -> OrderedDict:
    """
    Loads a configuration from a YAML file into an OrderedDict.

    Args:
        file_path (str): The path to the input YAML file.

    Returns:
        OrderedDict: The configuration loaded as an ordered dictionary.
    """
    with open(file_path, "r") as f:
        # The loader is already configured to return OrderedDict
        config = yaml.load(f, Loader=yaml.SafeLoader)
    print(f"Configuration loaded from {file_path}")
    return config
