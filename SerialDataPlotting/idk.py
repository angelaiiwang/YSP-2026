import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

import PythonSerialPlotting
signal3 = PythonSerialPlotting.main()

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
