import numpy as np

f0 = np.arange(18., 40.1, 0.2)
f1 = np.arange(50., 55.1, 0.2)
f2 = np.arange(65., 70.1, 0.2)
f3 = np.arange(183.3 - 5, 183.3 + 5.1, 0.2)
frequencies = np.hstack((f0, f1, f2, f3)) # GHz