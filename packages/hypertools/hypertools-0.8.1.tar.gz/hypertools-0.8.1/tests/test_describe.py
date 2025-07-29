# -*- coding: utf-8 -*-

import numpy as np

from hypertools.tools.describe import describe
from hypertools.plot.plot import plot

data = np.random.multivariate_normal(np.zeros(10), np.eye(10), size=100)


def test_describe_data_is_dict():
    result = describe(data, reduce='PCA', show=False)
    assert type(result) is dict


def test_describe_geo():
    geo = plot(data, show=False)
    result = describe(geo, reduce='PCA', show=False)
    assert type(result) is dict
