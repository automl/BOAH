import numpy as np
import hpbandster.core.nameserver as hpns
import hpbandster.core.result as hpres

from hpbandster.optimizers import BOHB
from hpbandster.core.worker import Worker


class EasyOptWorker(Worker):
    """
    The worker is responsible for evaluating a single configuration on a
    single budget at a time.
    Its 'compute' method  is repeatedly called during the optimization and
    evaluates a given configuration yielding the associated loss.
    The configuration is sampled from the configuration space by the master
    and is automatically passed to the 'compute' function.

    Note:
        The function to optimize must return a python scalar value

    Args:
        func (function): function to optimize. Must return a python scalar!
        func_args (tuple): arguments, passed to the function by the user,
            e.g. the data (X,y). These arguments don't include optimized
             parameters. Those are defined in the configuration space object.
    """

    def __init__(self, func, func_args,  *args, **kwargs):
        super(EasyOptWorker, self).__init__(*args, **kwargs)
        self.func = func
        self.func_args = func_args

    def compute(self, config, budget, **kwargs):
        return {'loss': self.func(budget=budget, *self.func_args, **config),
                'info': {'budget': budget}}


def easy_opt(func, func_args, config_space,
             eta=2, min_budget=2, max_budget=4, num_iterations=1,
             store_path='.'):
    """
    Starts a local BOHB optimization run for a function over a hyperparameter
    search space, which is referred to as configuration space.
    This function's purpose is to give a fast and easy way to run BOHB on a
    optimisation objective on your local machine.

    The signature of the optimized function must satisfy the following
    conditions:
    - Contain a parameter ``budget``:
        This parameter is passed by the optimizer.
        Its meaning is defined by your interpretation of budget used by your
        model. For example it may be the number of epochs for a neural network
        to train or the number of datapoints, the model receives.

        The idea is to run many configurations on a small budget and only
        take the best 1/``eta`` of them to the next round. In the next iteration
        the configurations run on the doubled budget. This is repeated, until
        only 2 configurations are left to run on the ``max_budget``.
        Therefore, bad configuration are rejected fast, and the good
        ones are explored more.
        The number of configurations with a minimum budget is calculated similar
        to the optimization run, just reversed. Having 2 configurations with
        ``max_budget``, in the iteration before ``eta``-times many
        configurations with half the budget are sampled, and so on.

    - Hyperparameter from the configuration space object:
        The function must implement all hyperparameters defined in the
        configuration space. The parameter name of the function must be
        equal to the name of the hyperparameter. Otherwise a exception will
        be thrown.

    - Function arguments in right order:
        Function arguments, which are not hyperparameters and therefore not
        defined in the configuration space must be passed to the
        ``easy_opt`` call in the order of occurence in the function signature.
        In the example below, for instance the training data, X and y, is a
        use case for this kind of function arguments.

    Example::

        import ConfigSpace as CS
        cs = CS.ConfigurationSpace()
        cs.add_hyperparameter(
            CS.UniformIntegerHyperparameter('w', lower=-3, upper=3)
        )

        X = np.arange(-5, 5)
        y = np.arange(-5, 5)

        # This simple example doesn't take the budget into account
        opt_func = lambda x, y, w, budget: np.mean(y - w*x)**2 + 0*budget

        # But the budget is still used to determine the number of
        # configurations to be sampled.(See the description of ``budget`` above)
        inc_best, inc_best_cfg, result = \
            easy_opt(opt_func, (X, y), cs, min_budget=1, max_budget=10)


    Args:
        func (function): function to optimize. Must return a python scalar!
        func_args (tuple): arguments, passed to the function by the user,
            e.g. the data (X,y). These arguments don't include
            optimized parameters. Those are defined in the
            configuration space object and will be passed by the master directly
            to the function.
        config_space (ConfigSpace.ConfigurationSpace):
            Definition of the search space containing all hyperparameter
            and their value ranges. You can find its definition in
            the `ConfiSpace repository <https://github.com/automl/ConfigSpace/>`_.
        eta (float): In each iteration, a complete run of sequential halving
            is executed. In it, after evaluating each configuration on the
            same subset size, only a fraction of 1/eta of them ‘advances’ to
            the next round. Must be greater or equal to 2
        min_budget (int, float, optional): Defines the minimum budget to
            evaluate configurations on it.
            In combination with the parameter `max_budget` and `eta`,
            the number of configuartions to evaluate is determined.
            Read more about it in the
            `Quickstart <https://automl.github.io/HpBandSter/build/html/quickstart.html#id6>`_.
            By default `min_budget` and `max_budget` is set, so that only a few
            configurations with budgets from 1 to 4 are evaluated.
        max_budget (int, float, optional): Defines the maximum budget to
            evaluate configurations on it.
        num_iterations (int, optional):   number of iterations to be performed
            in this run. By default, this value is set to 1.
        store_path (str, pathlib.Path, optional): HpBandSter stores the sampled
            configurations and the results on these configurations in two .json
            files. 'configs.json' and 'results.json'. Those files will be stored
            by default in the current directory (default='.').

    Returns:
        hpbandster.core.result.Run - Best run.
            Run result with the best loss values of all budgets.
            It stores information about the
            - budget
            - the unique configuration id (tuple)
            - loss
            - time stamps: start time and end time for this run.

        Dict - Best found configuration.
            Containing the configuration (from the configuration space), which
            achieved the best results in optimization run

        hpbandster.core.result.Result - Result object stores all results from
            all results, which were evaluated. The best run and the best found
            configuration are extracted from this results-object.

    """
    # Set up a local nameserver and start it
    ns = hpns.NameServer(run_id='easy_opt',
                         nic_name=None,
                         working_directory=store_path)
    ns_host, ns_port = ns.start()

    # Create a worker and pass the function as well as the function arguments
    # to it.
    worker = EasyOptWorker(func=func, func_args=func_args,
                           nameserver=ns_host,
                           nameserver_port=ns_port,
                           run_id='easy_opt')
    worker.run(background=True)

    # The result logger will store the intermediate results and the sampled
    # configurations in the passed directory.
    result_logger = hpres.json_result_logger(directory=store_path,
                                             overwrite=True)

    # Set up a master, which is book keeping and decides what to run next.
    opt = BOHB(configspace=config_space,
               run_id='easy_opt',
               min_budget=min_budget,
               max_budget=max_budget,
               eta=eta,
               host=ns_host,
               nameserver=ns_host,
               nameserver_port=ns_port,
               result_logger=result_logger)

    # The result object stores run information, e.g. the incumbent trajectory.
    result = opt.run(n_iterations=num_iterations)

    # After the run has finished, shut down the master and the worker
    opt.shutdown(shutdown_workers=True)
    ns.shutdown()

    # Extract the best configuration for each budget.
    inc_per_budget = result.get_runs_by_id(result.get_incumbent_id())

    # Find best incumbent over budgets. It is possible, that in some cases
    # results from intermediate budgets are better.
    from operator import itemgetter
    inc_best = sorted(inc_per_budget, key=itemgetter('loss'))[0]
    inc_best_cfg = result.data.get(inc_best.config_id).config

    return inc_best, inc_best_cfg, result


if __name__ == "__main__":

    # Create configuration space
    import ConfigSpace as CS
    cs = CS.ConfigurationSpace()
    cs.add_hyperparameter(
        CS.UniformIntegerHyperparameter('w', lower=-3, upper=3)
    )

    X = np.arange(-5, 5)
    y = np.arange(-5, 5)

    opt_func = lambda x, y, w, budget: np.mean(y - w*x)**2 + 0*budget

    for w in cs.sample_configuration(size=3):
        print("W: {} --> {}".format(w['w'], opt_func(X, y, **w, budget=0)))

    inc_best, inc_best_cfg, result = \
        easy_opt(opt_func, (X, y), cs, min_budget=1, max_budget=10)
