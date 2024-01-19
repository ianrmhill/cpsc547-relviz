

import numpy as np
import scipy
from matplotlib import pyplot as plt


def kde_fit_plot(data):
    kde = scipy.stats.gaussian_kde(data)
    x = np.linspace(np.min(data), np.max(data), 100)

    f, p = plt.subplots(figsize=(8, 2))
    p.hist(data, bins=100, density=True, color='grey')
    p.plot(x, kde(x), color='blue')
    plt.show()
