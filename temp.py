from SetUp import *
from scipy.optimize import minimize

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('mathtext', default='regular')
 
# Creating dataset
x = np.arange(10)
dataset_1 = np.random.random(10)*30
dataset_2 = np.random.random(10)*60
dataset_3 = np.random.random(10)*100
 
# Creating figure
fig = plt.figure()
 
# Plotting dataset_2
ax = fig.add_subplot(111)
ax.plot(x, dataset_2, '-', label='dataset_2')
ax.plot(x, dataset_3, '-', label='dataset_3')
 
# Creating Twin axes for dataset_1
ax2 = ax.twinx()
ax2.plot(x, dataset_1, '-r', label='dataset_1')
 
# Adding title
plt.title('Use different y-axes on the left and right of a Matplotlib plot',
          fontweight="bold")
 
# Adding legend
ax.legend(loc=0)
ax2.legend(loc=0)
 
# adding grid
ax.grid()
 
# Adding labels
ax.set_xlabel("X-axis")
ax.set_ylabel(r"Y1-axis")
ax2.set_ylabel(r"Y2-axis")
 
# Setting Y limits
ax2.set_ylim(0, 35)
ax.set_ylim(-20, 100)
 
# Show plot
plt.show()