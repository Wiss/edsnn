"""
manage_files.py:
    Some general tools for different experiments
"""
import os
import pickle
import shutil
import yaml


def create_folder(folder_path, verbose=True):
    """
    Creates new folder w.r.t. the current path

    Parameters
    ----------
    folder_path : string
        create path for new folder
    verbose : bool
    """
    current_path = os.path.abspath(os.getcwd())
    directory = f"{current_path}/{folder_path}"
    if not os.path.exists(directory):
        os.makedirs(directory, 0o775)
        if verbose:
            print(f"Successfully created new directory {directory}")


def load_config(path):
    """
    load config file from path

    Parameters
    ----------
    path : string
        absolute path to configuration file
    """
    with open(path) as f:
        data = yaml.safe_load(f)
    return data['general'], data['neurons'], data['connections'], \
        data['network_layout'], data['external_sources']


def save_config(config_path, output_path):
    """
    save config file to output path

    Parameters
    ----------
    config_path : string
        configuration absolute path
    output_path : string
        where the configuration file is going to be saved

    Returns
    -------
    None
    """
    shutil.copy(config_path, os.path.join(output_path, 'config.yaml'))


def save_data(file_path, file_name, dict_data):
    """
    save data from experiments

    Parameters
    ----------
    file_path : string
        path to file
    file_name : string
        file name
    dict_data : dict
        dictionary with information
    """
    with open(f"{file_path}/{file_name}.pkl", "wb") as f:
        pickle.dump(dict_data, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_data(file_path, file_name):
    """
    load data from experiments

    Parameters
    ----------
    file_path : string
        path to file
    file_name : string
        file name
    """
    with open(f"{file_path}/{file_name}.pkl", "rb") as f:
        loaded = pickle.load(f)
    return(loaded)
