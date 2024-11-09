import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import reed_reviewer.reed_utils as rutils
import time
from scipy.integrate import simps

CLOCK_PRECISION = time.clock_getres(0)


class ReedReviewer:
    def __init__(self, reed_id):
        self.id = reed_id

    def fingerprint_from_file(self, file_path):
        raw_data, fingerp = rutils.load_rec(file_path)
        # parse fingerprint
        reed_id = fingerp["id"]
        save_time = fingerp["save_time"]
        Fs = fingerp["Fs"]
        thresh = fingerp["rms_thresh"]

        print(reed_id, save_time, Fs, thresh)
        print(f"data shape = {raw_data.shape}")
