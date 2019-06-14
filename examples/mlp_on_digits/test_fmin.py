import numpy as np
import unittest
import logging
from FMin import fmin, load_func, load_configspace
import ConfigSpace as CS


class TestFMin(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.ERROR)
        np.random.seed(123)

        self.X = np.random.uniform(-5, 5, 100)
        self.y = np.random.normal(self.X, 1)

        self.opt_func = lambda x, y, w, budget: np.mean(
            (y[:int(budget)] - w * x[:int(budget)]) ** 2)

        self.cs = CS.ConfigurationSpace()
        self.cs.add_hyperparameter(
            CS.CategoricalHyperparameter('w', [0, 1])
        )

    def test_predict(self):

        min_budget = 3
        max_budget = 100
        inc_best, inc_best_cfg, result = fmin(self.opt_func, self.cs,
                                                  func_args=(self.X, self.y),
                                                  min_budget=min_budget,
                                                  max_budget=max_budget,
                                                  num_iterations=1)
        id2config = result.get_id2config_mapping()
        incumbent = result.get_incumbent_id()

        self.assertTrue(inc_best, result.get_runs_by_id(incumbent)[-1]['loss'])
        self.assertTrue(inc_best_cfg, id2config[incumbent]['config'])

        # The best solution shoud be w = 1, since the data is generated from
        # f(x) = x
        self.assertTrue(inc_best_cfg, 1)

        traj = result.get_incumbent_trajectory()
        budgets = [b for b in traj['budgets']]
        for i in range(len(budgets)):
            self.assertTrue(min_budget <= budgets[i] <= max_budget)

    def test_parse_cmd_args(self):
        import argparse
        from pathlib import Path

        args = argparse.ArgumentParser()
        args.config_space = str(Path.cwd() / 'configSpace.pcs')
        args.func = str(Path.cwd() / 'OptFunc.py')

        func = load_func(args.func)
        config = load_configspace(args.config_space)
        result_loaded = func(w=1, budget=100)

        func_to_load = lambda X, y, w, budget: \
            np.mean((y[:int(budget)] - w*X[:int(budget)])**2)
        result_to_load = func_to_load(self.X, self.y, w=1, budget=100)

        self.assertTrue(result_loaded, result_to_load)
        self.assertTrue(self.cs.__repr__() == config.__repr__())


if __name__ == '__main__':
    unittest.main()

    # TODO: REMOVE THIS AFTER MONDAY -> Just for demonstration purpose
    cs = CS.ConfigurationSpace()
    cs.add_hyperparameter(
        CS.UniformFloatHyperparameter('w', lower=-5, upper=5)
    )

    X = np.random.uniform(-5, 5, 100)
    y = np.random.normal(X, 1)

    opt_func = lambda x, y, w, budget: np.mean((y[:int(budget)] - w*x[:int(budget)])**2)

    for w in cs.sample_configuration(size=3):
        print("W: {} --> {}".format(w['w'], opt_func(X, y, **w, budget=3)))

    inc_value, inc_cfg, result = fmin(opt_func, cs, func_args=(X, y),
                                              min_budget=3, max_budget=len(X),
                                              num_iterations=3, num_workers=1)
    # Plot the results
    id2config = result.get_id2config_mapping()
    incumbent = result.get_incumbent_id()

    traj = result.get_incumbent_trajectory()
    budgets = [b for b in traj['budgets']]
    values = [id2config[id]['config'] for id in traj['config_ids']]

    import matplotlib.pyplot as plt

    plt.scatter(X, y)
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    for i in range(len(values)):
        plt.plot(X, values[i]['w']*X, label="{}. W: {:.2f}".format(i+1, values[i]['w']))
    plt.legend(loc=1)
    plt.show()
