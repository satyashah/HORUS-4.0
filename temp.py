from SetUp import *
from scipy.optimize import minimize

print(np.nan-np.nan)

rangesArr = [[1,2],[1.5,2.5], [np.nan,np.nan], [2,3], [2.5,3.5]]
#https://matplotlib.org/stable/gallery/lines_bars_and_markers/fill_between_demo.html

x = np.arange(len(rangesArr))
y1 = np.array([ran[0] for ran in rangesArr])
y2 = np.array([ran[1] for ran in rangesArr])


plt.plot(x, y1, 'o--')
plt.plot(x, y2, 'o--')
plt.fill_between(x, y1, y2, where=(y1 > y2), color='C0', alpha=0.3)
plt.fill_between(x, y1, y2, where=(y1 < y2), color='C1', alpha=0.3)


plt.show()