import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# 1. Generate a dummy signal
sampling_rate = 1000.0  # Hz
time_step = 1.0 / sampling_rate
t = np.arange(0, 1.0, time_step)
signal = np.sin(2 * np.pi * 133 * t)  # 50 Hz sine wave
signal2 = np.cos(2 * np.pi * 100 * t)
signal3 = signal * signal2

# 2. Compute the FFT
fft_output = fft(signal3)

# 3. Calculate true frequencies
frequencies = fftfreq(len(2*signal3), d=time_step)

# 4. Get the real magnitude (ignore negative mirror frequencies)
magnitude = np.abs(fft_output)[:len(signal3)//2]
positive_frequencies = frequencies[:len(signal3)//2]
plt.plot(positive_frequencies, magnitude)
plt.xlabel('Frequency')
plt.ylabel('Magnitude')
plt.title('title')

# 4. Display the chart
plt.show()
