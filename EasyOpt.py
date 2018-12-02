"""
Welcome to EasyOpt for HpBandSter optimization runs.

You can easily optimize a function with the optimization tools from HpBandSter,
like BOHB.

The function easy_opt is callable from the commandline, as well as in your code.

To call it from command line, you must:

- provide the path to a file containing a function with the name opt_func.
- provide the path to a configuration space definition in pcs or json file
    format
- make sure to satisfy the conditions described in the docstring of
    :method:: easy_opt

"""

# TODO:
# - Remove visualization at end of file (in main)
# - Think of better way to pass function arguments via commandline

import argparse
from pathlib import Path

import hpbandster.core.nameserver as hpns
import hpbandster.core.result as hpres
from hpbandster.optimizers import BOHB
from hpbandster.core.worker import Worker

from ConfigSpace.read_and_write import pcs_new, json

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


def easy_opt(func, config_space, func_args=(),
             eta=2, min_budget=2, max_budget=4, num_iterations=1,
             num_workers=1, output_dir='.'):
    """
    Starts a local BOHB optimization run for a function over a hyperparameter
    search space, which is referred to as configuration space.
    This function's purpose is to give a fast and easy way to run BOHB on a
    optimisation objective on your local machine.

    The optimized function must satisfy the following conditions:
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
        configuration space. The parameter name in the function call must be
        equal to the name of the hyperparameter. Otherwise a exception will
        be thrown.

    - Function arguments in right order:
        Function arguments, which are not hyperparameters and therefore not
        defined in the configuration space must be passed to the
        ``easy_opt`` call in the order of occurrence in the function signature.
        In the example below, for instance the training data, X and y, is a
        use case for this kind of function arguments.

    Example::
        import numpy as np
        from EasyOpt import easy_opt
        import ConfigSpace as CS

        # Create configuration space
        cs = CS.ConfigurationSpace()
        cs.add_hyperparameter(
            CS.UniformFloatHyperparameter('w', lower=-5, upper=5)
        )

        # Create data from function
        # f(x) = x + :math:`\mathcal{N}(0, 1)`
        X = np.random.uniform(-5, 5, 100)
        y = np.random.normal(X, 1)

        # The function calculates the mean squared error for the first
        # ``budget`` points compared to their responding true values.
        # The expected minimum is at w = 1.
        opt_func = lambda x, y, w, budget: np.mean((y[:int(budget)] - w*x[:int(budget)])**2)

        inc_best, inc_best_cfg, result = easy_opt(opt_func,
                                                  cs, func_args=(X, y),
                                                  min_budget=3,
                                                  max_budget=len(X),
                                                  num_iterations=3,
                                                  num_worker=1)

    Args:
        func (function): function to optimize. Must return a python scalar!
            See also section above
            **The optimized function must satisfy the following conditions**
        config_space (ConfigSpace.ConfigurationSpace):
            Definition of the search space containing all hyperparameters
            and their value ranges. You can find its definition in
            the `ConfiSpace repository <https://github.com/automl/ConfigSpace/>`_.
        func_args (tuple): arguments, passed to the function by the user,
            e.g. the data (X,y). These arguments don't include
            optimized parameters. Those are defined in the
            configuration space object and will be passed by the master directly
            to the function.
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
        num_workers (int, optional): number of parallel workers. By default, just
            one worker is used.
        output_dir (str, optional): HpBandSter stores the sampled
            configurations and the results on these configurations in two .json
            files. 'configs.json' and 'results.json'. Those files will be stored
            by default in the current directory (default='.').
            Also, we store the configuration space definition for later use to
            this directory. It may be used for further analysis via
            `CAVE <https://automl.github.io/CAVE/stable/>`_.

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
    output_dir = Path(output_dir)
    # Set up a local nameserver and start it
    ns = hpns.NameServer(run_id='easy_opt',
                         nic_name=None,
                         working_directory=output_dir)
    ns_host, ns_port = ns.start()

    # Create ``num_workers`` workers and pass the function as well as the
    # function arguments to each of them.
    workers = []
    for _ in range(num_workers):
        worker = EasyOptWorker(func=func, func_args=func_args,
                               nameserver=ns_host,
                               nameserver_port=ns_port,
                               run_id='easy_opt')
        worker.run(background=True)
        workers.append(worker)

    # The result logger will store the intermediate results and the sampled
    # configurations in the passed directory.
    result_logger = hpres.json_result_logger(directory=output_dir,
                                             overwrite=True)

    # For hyperparameter importance analysis via CAVE we store the configuration
    # space definition to file.
    with open(output_dir / 'configSpace.pcs', 'w') as f:
        f.write(pcs_new.write(config_space))

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
    # Force the master to wait until all workers are ready.
    result = opt.run(n_iterations=num_iterations, min_n_workers=num_workers)

    # After the run has finished, shut down the master and the workers
    opt.shutdown(shutdown_workers=True)
    ns.shutdown()

    # Return the optimal value and the responding configuration, as well as the
    # result object. The result object can be used in a second step for further
    # hyperparameter importance analysis with CAVE.
    id2config = result.get_id2config_mapping()
    incumbent = result.get_incumbent_id()
    inc_value = result.get_runs_by_id(incumbent)[-1]['loss']
    inc_cfg = id2config[incumbent]['config']

    return inc_value, inc_cfg, result


def load_func(path_to_function_file):
    """
    Parse optimization function

    Args:
        path_to_function_file (str): Path to the file, in which the function
            with the name 'opt_func' is

    Returns:
        optimize function
    """
    from importlib.machinery import SourceFileLoader
    loader = SourceFileLoader('opt_func', path_to_function_file)
    module = loader.load_module()
    function = getattr(module, 'opt_func')
    return function


def load_configspace(path_to_cs_file):
    """
    Load configuration space definition
    Args:
        path_to_cs_file: Path to the file, in which the configuration space is
            defined. Must be in format pcs or json

    Returns:
        ConfigSpace.configuration_space
    """
    if path_to_cs_file.endswith('.pcs'):
        with open(path_to_cs_file, 'r') as f:
            cfg = pcs_new.read(f)
    elif path_to_cs_file.endswith('.json'):
        with open(path_to_cs_file, 'r') as f:
            cfg = json.read(f.read())
    else:
        raise ImportError('Configuration space definition not understood. File'
                          ' must be in format pcs or json.')

    return cfg


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Easy Optimization for '
                                                 'HpBandSter')
    parser.add_argument('--func',
                        help='Path to a py-file, containing a function to '
                             'optimize and its arguments', type=str)
    parser.add_argument('--config_space',
                        help='Path to a ConfigSpace definition in pcs or json '
                             'format', type=str)
    parser.add_argument('--eta', help='ETA Parameter for HpBandSter',
                        type=float, default=2)
    parser.add_argument('--min_budget', help='Minimum budget for HpBandSter',
                        type=float, default=2)
    parser.add_argument('--max_budget', help='Maximum budget for HpBandSter',
                        type=float, default=4)
    parser.add_argument('--num_iterations',
                        help='Number iterations of HpBandSter',
                        type=int, default=1)
    parser.add_argument('--num_workers', help='Number of parallel workers',
                        type=int, default=1)
    parser.add_argument('--output_dir', help='Output directory',
                        type=str, default='.')
    args = parser.parse_args()

    func = load_func(args.func)
    config = load_configspace(args.config_space)

    inc_value, inc_cfg, result = easy_opt(func=func, config_space=config, eta=args.eta,
             min_budget=args.min_budget, max_budget=args.max_budget,
             num_iterations=args.num_iterations, num_workers=args.num_workers,
             output_dir=args.output_dir)

    print('Found best value {} with the configuration {}'.format(inc_value,
                                                                 inc_cfg))

    # TODO THIS IS FOR DEMONSTRATION PURPOSE:
    # Plot the results
    id2config = result.get_id2config_mapping()
    incumbent = result.get_incumbent_id()

    traj = result.get_incumbent_trajectory()
    budgets = [b for b in traj['budgets']]
    values = [id2config[id]['config'] for id in traj['config_ids']]

    import matplotlib.pyplot as plt
    import numpy as np
    np.random.seed(123)
    X = np.random.uniform(-5, 5, 100)
    y = np.random.normal(X, 1)
    plt.scatter(X, y)
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    for i in range(len(values)):
        plt.plot(X, values[i]['w'] * X,
                 label="{}. W: {:.2f}".format(i + 1, values[i]['w']))
    plt.legend(loc=1)
    plt.show()