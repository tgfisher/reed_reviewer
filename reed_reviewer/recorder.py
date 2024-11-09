import os
import time
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import reed_reviewer.reed_utils as rutils
from scipy.integrate import simps

CLOCK_PRECISION = time.clock_getres(0)
HOME = os.path.expanduser("~")
DATA_ROOT = os.path.join(HOME, ".reed_reviewer_data")


class ReedRecorder:
    """
    Each reed has a reed recorder. The reed id tells reed reviewer where to save
    out files.

    Inputs
    ------
        reed_id (int/str) - reed number, an identification name for a particular reed.

        rec_duration_sec (float/int) - This specifies the length of recording and 
            the length of baseline period.

        sensitivity_rms = amplitude scale for save threshold. Look into _thresh_save
            for more details.

        rec_wait (float) - miliseconds - _record method sleeps for this ammount of
            time. This prevents button/key clicks from registering in recordings
    """

    def __init__(self, reed_id, rec_duration_sec=1, sensitivity_rms=10, rec_wait=0.1):
        """
        Instance Variables
        ------------------
            id (converts to str) - reed id number or name
            duration (float) - length of listening in seconds. TODO: this should
                be listening in chunks for a passing threshold so user doesn't need
                need to click buttons on the app.
            sensitivity_rms (float) - specifies how many "rms" away from average
                the sound envelope must be before it triggers a save.
            Fs (int) - 44100 - this is the frequency samples per second. This is
                the "CD quality" sampling rate. It is twice the frequency that is
                perceptible to the human ear.
            raw_data (ndarray) - this holds a numpy array of the last recording.
            save_time (int) - epoch time at the resolution of the system clock.
            rms_thresh (float) - amplitude threshold for save trigger.
            ref_power (float) - power of the baseline, or reference, recording.
                db is a log ratio of powers. In order to implement db level triggering
                later this is necessary.
            freq_mag (ndarray) - magnitude at each frequency. Frequencies specified
                in freq_axis. The magnitudes in Fourier domain.
            freq_axis (ndarray) - array of frequencies in the fft. The frequency
                axis in f domain.
        """
        # initialize static values
        self.id = str(reed_id)
        self.duration = rec_duration_sec  # length of listening TODO: this should be listening in chunks for passing threshold
        self.sensitivity_rms = sensitivity_rms
        self.rec_wait = rec_wait

        self.Fs = 44100  # this is a CD quality sampling rate (twice the sampling
        # rate of the max human frequency)

        # empty arrays
        self.raw_data = np.array([])  # current recording
        self.save_time = []
        self.freq_mag = []  # frequency spectrum magnitudes, normalized for rec time
        self.freq_axis = []  # frequency axis of fft

        # sets ref_power, and rms_thresh
        self._set_initial_thresh()  # sets to empty if no baseline rec is saved

    # ____________________________Bread  n'  Butter____________________________#
    # def stream_listen(self):
    #    with sd.InputStream(samplerate=self.Fs, latency=10, channels=2, dtype=np.ndarray, callback=stream_parse):
    #        time.sleep(10)
    # def stream_parse(data, frames, time, status):
    #    print(data.shape)

    def listen(self, save_bool=True):
        """
        records, checks if recording passes save threshold and if so, saves
        """
        raw_data = self._record(self.duration)
        print(f"recording... please wait {self.duration} seconds")
        sd.wait()
        print("done")

        # data and time
        self.save_time = rutils.epoch_time_int()
        self.raw_data = raw_data
        self._thresh_save()

    def set_thresh(self):
        """
        takes baseline recording, sets threshold, saves it to baseline dir
        """
        self.listen(
            save_bool=False
        )  # save_bool prevents saving baseline rec as reed rec

        # rms val
        rms = self.get_rms()
        self.rms_thresh = rms[0] * self.sensitivity_rms

        # power
        self.ref_power = self.get_power()

        # save
        self._save_baseline_rec()

    def speak(self):
        """
        plays back last recording on system speakers
        """
        sd.play(self.raw_data, self.Fs)

    # ____________________________Plotting  Methods____________________________#
    def plot(self, fig=None):
        """
        Nice plotting method. Specifically designed for use with kivy.

        Top panel: It will plot the last sound recording, and the current threshold 
            if there is one.
        Middle panel: It will plot the power spectrum of the last sound recording
            across the specified (by Fs) spectrum.
        Bottom panel: Designed to highlight relevant frequencies. Just a blown
            up version of the middle panel.

        Inputs
        ------
        fig (matplotlib.figure.Figure) - None - this is an instance of the figure class.
           by default it is set to none and one is created. However, for use with kivy
           app development environment a figure input makes the kivy code much cleaner.
        """

        # This block is because I need to preserve figure canvas for the app
        if fig == None:
            fig, ax = plt.subplots(3, 1, figsize=(10, 10))
        else:
            # strip out figure
            for ax in fig.axes:
                ax.remove()
            # repopulate for ReedReviewer plot method
            fig.add_subplot(311)
            fig.add_subplot(312)
            fig.add_subplot(313)
            ax = fig.get_axes()

        # constants
        plot_alpha = 0.97
        grid_alpha = 0.1
        title_size = 15
        text_size = 13

        # Plotting block
        if self.raw_data.size > 0:  # data has been taken
            self._fft(self.raw_data)
            print("plotting")

            time_samples = self.raw_data.shape[0]
            t = [idx / self.Fs for idx in range(time_samples)]

            ax[0].plot(t, self.raw_data, alpha=plot_alpha)

            # plot rms thresh as labeled line
            if self.rms_thresh:  # runs if isnt empty
                thresh_plot_max_idx = int(time_samples * 0.96)  # make room for label
                rms_thresh = [self.rms_thresh for idx in range(thresh_plot_max_idx)]
                ax[0].plot(t[:thresh_plot_max_idx], rms_thresh, color="g")
                label_x_idx = int(thresh_plot_max_idx * 1)
                ax[0].text(
                    t[label_x_idx],
                    rms_thresh[0],
                    " Threshold",
                    verticalalignment="center",
                    fontsize=text_size,
                    color="g",
                )

            # define x-axes for power spectrum
            startfreq_idx = int(self.freq_axis.shape[0] / 2)
            endfreq_idx = (
                int(20000 * startfreq_idx / max(self.freq_axis)) + startfreq_idx
            )
            trunc_startfreq_idx = int(self.freq_axis.shape[0] / 2)
            trunc_endfreq_idx = (
                int(4000 * trunc_startfreq_idx / max(self.freq_axis))
                + trunc_startfreq_idx
            )

            # plot
            draw_style = ["-", "--"]  # plots both left and right mic channel
            for idx in range(self.raw_data.shape[1]):  # plot for each channel
                ax[1].plot(
                    self.freq_axis[startfreq_idx:endfreq_idx],
                    self.freq_mag[startfreq_idx:endfreq_idx, idx],
                    linestyle=draw_style[idx],
                    alpha=plot_alpha,
                )
                ax[2].plot(
                    self.freq_axis[trunc_startfreq_idx:trunc_endfreq_idx],
                    self.freq_mag[trunc_startfreq_idx:trunc_endfreq_idx, idx],
                    linestyle=draw_style[idx],
                    alpha=plot_alpha,
                )
        else:  # no data yet plot
            ax[0].text(
                0.5,
                0.5,
                "waiting",
                verticalalignment="center",
                horizontalalignment="center",
                fontsize=50,
            )
            ax[1].text(
                0.5,
                0.5,
                "on",
                verticalalignment="center",
                horizontalalignment="center",
                fontsize=50,
            )
            ax[2].text(
                0.5,
                0.5,
                "data",
                verticalalignment="center",
                horizontalalignment="center",
                fontsize=50,
            )
            print("waiting on data")

        # Prettyfy
        ax[0].set_title("Sound Envelope", fontsize=title_size)
        ax[0].set_xlabel("Time")
        ax[0].set_ylabel("Amplitude")
        ax[0].grid(color="k", alpha=grid_alpha)
        ax[1].set_title("Full Frequency Spectrum", fontsize=title_size)
        ax[1].set_xlabel("Frequency")
        ax[1].set_ylabel("Power\n")
        ax[1].grid(color="k", alpha=grid_alpha)
        ax[2].set_title(
            "Truncated Frequency Spectrum (Zoomed In View)", fontsize=title_size
        )
        ax[2].set_xlabel("Frequency (smaller range)")
        ax[2].set_ylabel("Power\n")
        ax[2].grid(color="k", alpha=grid_alpha)

        for an_ax in fig.axes:
            an_ax.spines["top"].set_visible(False)
            an_ax.spines["right"].set_visible(False)
            an_ax.spines["left"].set_visible(False)

        plt.tight_layout()

        return fig

    # ____________________________ Return Methods  ____________________________#
    def get_id(self):
        return self.id

    def get_signal(self):
        return self.raw_data

    def get_thresh_amp(self):
        return self.rms_thresh

    def get_rms(self):
        return self._compute_rms(self.raw_data)

    def get_power(self):
        signal = self.raw_data[:, 0]
        Ns = signal.shape[0]
        signal_duration = Ns / self.Fs
        power = self._compute_power(signal, signal_duration)
        return power

    def get_db(self):
        self.raw_db = 10 * np.log10(self.get_power() / self.ref_power)
        return self.raw_db

    # ____________________________ Support  Methods ____________________________#
    def _record(self, duration):
        """
        waits a moment and records
        """
        time.sleep(self.rec_wait)  # prevent keyclicks from registering
        raw_data = sd.rec(int(duration * self.Fs), samplerate=self.Fs, channels=2)
        return raw_data
        # save_squeak(self.reed_id, self.Fs, self.save_time, self.raw_data)

    def _compute_rms(self, raw_data):
        squared_error = raw_data ** 2  # mean is approx 0 so no subtraction needed
        mean_squared_error = squared_error.mean(0)  # mean of the squared error
        root_mse = np.sqrt(mean_squared_error)
        return root_mse

    def _compute_power(self, signal, signal_duration):
        # TODO compute in frequency domain
        """
            Inputs
            ------
            signal (ndarray, signal by)
            P_avg
           -------
            Average power can be computed in the frequency or the time domain.
                In the time domain average power is the integral of its squared 
                signal (aka. total energy) divided by duration over which you
                take the integral.

                In the frequency domain...to come later, maybe

        """
        Ns = signal.shape[0]
        abs_signal_squared = np.abs(signal) ** 2
        signal_integral = simps(abs_signal_squared, dx=1 / self.Fs)
        signal_duration = Ns / self.Fs

        return signal_integral / signal_duration

    def _fft(self, signal):
        """
        implements a fast Fourier transform. Boiler plate from python docs.
        """

        print("computing fft")
        Ns = signal.shape[0]  # sample number
        fft_raw_data = np.empty([Ns, 2], dtype=complex)  # holds fft later
        self.freq_mag = np.zeros([Ns, 2])
        for idx in range(2):  # fft on each channel
            fft_raw_data[:, idx] = np.fft.fft(self.raw_data[:, idx])
            self.freq_mag[:, idx] = np.fft.fftshift(np.abs(fft_raw_data[:, idx])) / (
                Ns / self.Fs
            )  # Ns * Fs corrects for time so this is a density
        self.freq_axis = np.fft.fftshift(
            np.fft.fftfreq(Ns, 1 / self.Fs)
        )  # freq axis shared

    def _set_initial_thresh(self):
        """
        run by __init__ method. Checks for existing threshold files. Will use the
        most recent threshold recording if availible. If none exist it will
        set threshold variables to empty lists.
        """

        # form path in os agnostic way
        baseline_dir = os.path.join(DATA_ROOT, "baseline")

        # make dir if doesnt exist
        rutils.check_add_dir(baseline_dir)

        # get newest file or empty list if none exist (dir is empty)
        newest_file_name = rutils.newest_recording_name(baseline_dir)

        if not newest_file_name == []:  # if dir isnt empty
            print("setting initial threshold")

            newest_baseline_path = os.path.join(baseline_dir, newest_file_name)
            # load recording
            baseline_rec, fingerprint = rutils.load_rec(newest_baseline_path)

            # set rms_threshold
            rms = self._compute_rms(baseline_rec)
            self.rms_thresh = rms[0] * self.sensitivity_rms

            # set ref_power
            signal = baseline_rec[:, 0]
            Ns = signal.shape[0]
            Fs = fingerprint["Fs"]
            signal_duration = Ns / int(Fs)
            self.ref_power = self._compute_power(signal, signal_duration)
            print("done")

        else:  # else empty dir
            print("no baseline file, please set threshold")
            self.rms_thresh = []
            self.ref_power = []

    def _thresh_save(self):
        """
        Save if current recording passes threshold.
        """
        thresh_vals = [val for val in self.raw_data[:, 0] if val > self.rms_thresh]
        if thresh_vals:  # check if empty
            self._save_rec()

    def _save_baseline_rec(self):
        """
        Save into the baseline directory. Baseline recordings are saved into their
        own directory. There is no reed associated with them.
        """
        self._save("baseline")

    def _save_rec(self):
        """
        save into current reed dir
        """
        reed_dir = f"reed_{self.id}"
        self._save(reed_dir)

    def _save(self, sub_dir, tag=None):
        """
        handles save filename creation. Preps data for saving. saves raw_data.

        Inputs
        ------
        tag - (string) - a string that can be appended to filename.
        """
        print("saving")

        # add fingerprint for futureproofing
        fingerp = self._fingerprint()  # fingerprint

        # check for / add reed directory
        dir_path = os.path.join(DATA_ROOT, sub_dir)
        rutils.check_add_dir(dir_path)

        # add tags to save name
        if tag == None:
            sv_filename = f"{self.save_time}"
        else:
            sv_filename = f"baseline_{self.save_time}_{tag}"

        # save
        sv_path = os.path.join(dir_path, sv_filename)

        # take advantage of savez multiple array save
        # allowing fingerp to be array of strings
        np.savez_compressed(f"{sv_path}", recording=self.raw_data, fingerprint=fingerp)

    def _fingerprint(self):
        """
        Makes a "fingerprint". It's the little things. Will help me out if
            files get shuffled.

        fingerprint (dict)
        ----------
            id - in case a file gets moved from its proper directory
            save_time - in case data gets shuffled.
            Fs - verify the sampling rate of the recording
            rms_threshold - what value the recording passed to be saved
        """
        return dict(
            id=self.id, save_time=self.save_time, Fs=self.Fs, rms_thresh=self.rms_thresh
        )
