import pandas as pd
from matplotlib import pyplot as plt

df = pd.read_csv('full_match_stats_premier.csv')
corrMatrix = df.corr()
print(corrMatrix)
# plt.matshow(corrMatrix)
# plt.show()