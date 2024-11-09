import os
import time
import numpy as np
import matplotlib.pyplot as plt

HOME = os.path.expanduser("~")
DATA_ROOT = os.path.join(HOME, ".reed_reviewer_data")


def epoch_time_int():
    """
    epoch time is a float. This corrects this to the integer at the computer
    clock resolution
    """
    clock_precision = time.clock_getres(0)
    int_time = round(
        time.time() / clock_precision
    )  # epoch time at cpu clock resolution

    return int_time


def check_add_dir(dir_path):
    """
    check for path, add if doesn't exist
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def newest_recording_name(dir_path):
    """
        if files exist at path return newest, or return empty list 
    """
    if os.path.exists(dir_path):
        rec_list = os.listdir(dir_path)
        if not rec_list == []:
            return max(rec_list)
        else:
            return []
    else:
        return []


def load_rec(rec_path):
    """
    load saved recording.

    NOTE: allow_pickle=True - this allows the fingerprint dict to load
    """

    with np.load(rec_path, allow_pickle=True) as data:
        fingerp_array = data["fingerprint"]
        fingerp_dict = fingerp_array.tolist()
        return data["recording"], fingerp_dict
