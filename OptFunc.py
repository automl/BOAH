import numpy as np


def opt_func(w, budget):
    np.random.seed(123)
    X = np.random.uniform(-5, 5, 100)
    y = np.random.normal(X, 1)
    return np.mean((y[:int(budget)] - w*X[:int(budget)])**2)
