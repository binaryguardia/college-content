#creating series from array
import pandas as pd
import numpy as np

info = np.array([21,33,69,96,12,17])
a = pd.Series(info)

print(a)
