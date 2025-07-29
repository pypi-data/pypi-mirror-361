import numpy as np
from scipy.optimize import curve_fit
from functools import partial
from .core import pool
from .image import fitfunc_dict


def update():
    percentiles = [1, 10, 25, 75, 90, 99]
    input_data = []
    output_data = []
    for i in range(10, 201, 5):
        average_array = []
        for _ in range(5000):
            average_array.append(sum(pool.gacha().rare for _ in range(i)) / i)
        input_data.append(i)
        output_data.append([np.percentile(average_array, percentile) for percentile in percentiles])

    def func(x, a, b, c, d):
        return a * np.log(b * x) + c * x + d

    fitfunc_dict.clear()

    for i, percentile_data in enumerate(zip(*output_data), start=1):
        popt, pcov = curve_fit(func, input_data, percentile_data)
        a, b, c, d = popt
        fitfunc_dict[i] = partial(func, a=a, b=b, c=c, d=d)
