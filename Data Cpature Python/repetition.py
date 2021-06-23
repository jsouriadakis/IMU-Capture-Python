import pandas as pd
import numpy as np
from scipy.signal import butter, lfilter, freqz, savgol_filter, filtfilt, detrend, find_peaks, medfilt
from scipy.integrate import cumtrapz
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class RepetitionClass:

    def countReps(self, z, fs):
        # # we assume that the motion is mainly on the z axis
        # # need to trasnform data from arduino to world space
        # # filting acceleration signal and integrating twice to get distance travelled by the equipment's weight
        order = 1
        # # fs = 20  # sample rate, Hz
        fc = 1.5
        b, a = butter(N = order, Wn = fc / (0.5 * fs), btype='low', analog=False)
        # d, c = butter(N = order, Wn = fc / (0.5 * fs), btype='high', analog=False)
        #
        y = lfilter(b, a, z)
        print(y)
        # #z_filtered = y = lfilter(b, a, z)
        # #z_filtered = y = medfilt(z)
        # #z_filtered = y = lfilter(b, a, y)
        # z_filtered = savgol_filter(z, 13, 3)
        # vel = cumtrapz(z_filtered)
        # vel_detrended = detrend(vel)
        # vel_filtered = lfilter(d, c, vel)
        #
        # dist = cumtrapz(vel_detrended)
        # dist_filtered = lfilter(d, c, dist)
        # dist_filtered = dist_filtered - dist_filtered.mean()
        #
        # dist_detrended = detrend(dist, type='linear')
        # Savitzky–Golay filter

        # plt.plot(z_filtered2)
        peak_min_width = 0.2 * fs
        peak_min_height = 15  # 30 cm
        # peaks, peaks_props = find_peaks(dist, height=peak_min_height, width=peak_min_width)
        # #peaks2, peaks_props2 = find_peaks(-dist_filtered, height=-peak_min_height, width=peak_min_width)
        # # find mean of peaks and accept only those within ?x-std?
        # peak_prominance = peaks_props['prominences']
        # peak_vals = peaks_props['peak_heights']
        # peak_mean = np.mean(peak_vals)
        # peak_std = np.std(peak_vals)

        #print("Peak Heights:", peak_vals)
        #print("Peak Heights - Mean:", peak_mean)
        #print("Peak Heights - Std:", peak_std)
        #print("Peak prominence:", peak_prominance)
        #print("# Reps: ", peaks)
        #nonzero_count = (np.where(np.abs(peak_mean - peak_vals) < 2 * peak_std))
        #print("\n")
        #print(peaks)
        #return peaks, peak_vals.size

