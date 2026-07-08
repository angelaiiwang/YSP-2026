import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

import PythonSerialPlotting

time_ms, signal3 = PythonSerialPlotting.main()
time_ms = np.asarray(time_ms)
signal3 = np.asarray(signal3, dtype=float)

# --- Check sampling uniformity -----------------------------------------
dt_ms = np.diff(time_ms)
mean_dt_ms = np.mean(dt_ms)
std_dt_ms = np.std(dt_ms)
print(f"Mean sample spacing: {mean_dt_ms:.3f} ms, std dev: {std_dt_ms:.3f} ms")
if std_dt_ms > 0.1 * mean_dt_ms:
    print("Warning: sample spacing is quite irregular. "
          "FFT assumes uniform sampling, so results may be smeared. "
          "Consider resampling onto a uniform time grid (see np.interp).")

time_step = mean_dt_ms / 1000.0  # seconds, from ACTUAL measured sample rate
N = len(signal3)

# Remove DC offset so 0 Hz doesn't dominate the plot
signal3_ac = signal3 - np.mean(signal3)

# --- FFT -----------------------------------------------------------------
fft_output = fft(signal3_ac)
frequencies = fftfreq(N, d=time_step)

magnitude = (2.0 / N) * np.abs(fft_output[:N // 2])
positive_frequencies = frequencies[:N // 2]

plt.plot(positive_frequencies, magnitude)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.title('FFT of Sensor Signal')
plt.grid(True, alpha=0.3)
plt.show()
