import numpy as np
import saftig as sg

n_filter = 10
n_channel = 2

filt = sg._lms_c.LMS_C(n_filter, 0, n_channel, 0.1)

W = np.array([np.arange(n_filter) for i in range(n_channel)], dtype=np.float64)
T = 2

for i in range(10):
    pred = filt.step(W, T)
    print(pred)
