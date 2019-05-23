# This script will run any of the experiments described in HpBandSter's icml_2018_experiments
# Use the script with the --help flag to receive info on usage.

import os
import pickle
import argparse
import copy

import numpy as np

import hpbandster.core.nameserver as hpns
from hpbandster.optimizers import RandomSearch, BOHB, HyperBand
import hpbandster.core.result as hpres

from workers.bnn_worker import BNNWorker
from workers.cartpole_worker import CartpoleReducedWorker as CartpoleWorker
from workers.paramnet_surrogates import ParamNetSurrogateWorker
from workers.svm_surrogate import SVMSurrogateWorker

def standard_parser_args(parser):
    parser.add_argument('--exp_name', type=str, required=True, help='Possible choices: bnn, cartpole, svm_surrogate, paramnet_surrogates')
    parser.add_argument('--opt_method', type=str, default='bohb', help='Possible choices: randomsearch, bohb, hyperband, smac')

    parser.add_argument('--dest_dir', type=str, help='the destination directory. A new subfolder is created for each benchmark/dataset.',
                        default='../opt_results')
    parser.add_argument('--num_iterations', type=int, help='number of Hyperband iterations performed.', default=4)
    parser.add_argument('--min_budget', type=float, help='Minimum budget for Hyperband and BOHB.')
    parser.add_argument('--max_budget', type=float, help='Maximum budget for all methods.')
    parser.add_argument('--eta', type=float, help='Eta value for Hyperband/BOHB.', default=3)
    # Network / cluster args for HpBandSter-methods
    parser.add_argument('--n_workers', type=int, help='Number of workers to run in parallel.', default=1)
    parser.add_argument('--worker', help='Flag to turn this into a worker process', action='store_true')
    parser.add_argument('--no_worker', help='Flag to turn this into a worker process',
                        dest='worker', action='store_false')
    parser.add_argument('--nic_name', type=str, default='lo', help='name of the network interface used for communication. Note: default is only for local execution on *nix!')
    parser.add_argument('--run_id', type=str, default=0)
    parser.add_argument('--working_directory', type=str, help='Directory holding live rundata. Should be shared across all nodes for parallel optimization.',
                        default='./tmp/')
    # Only relevant for some experiments
    parser.add_argument('--dataset_bnn', choices=['toyfunction', 'bostonhousing', 'proteinstructure'], help='Only for bnn. ', default=None)
    parser.add_argument('--dataset_paramnet_surrogates', choices=['adult', 'higgs', 'letter', 'mnist', 'optdigits', 'poker'],
                        help="Only for paramnet_surrogates. ", default=None)
    parser.add_argument('--surrogate_path', type=str, help="Path to the pickled surrogate models. If None, HPOlib2 "
                                                           "will automatically download the surrogates to the .hpolib "
                                                           "directory in your home directory.", default=None)
    return parser

def get_optimizer(parsed_args, config_space, **kwargs):
    """ Get the right hpbandster-optimizer """
    eta = parsed_args.eta
    opt = None
    if parsed_args.opt_method == 'randomsearch':
        opt = RandomSearch
    if parsed_args.opt_method == 'bohb':
        opt = BOHB
    if parsed_args.opt_method == 'hyperband':
        opt = HyperBand
    if opt is None:
        raise ValueError("Unknown method %s" % parsed_args.method)
    return opt(config_space, eta=eta, **kwargs)

def get_worker(args, host=None):
    exp_name = args.exp_name
    if exp_name == 'bnn':
        if not args.dataset_bnn:
            raise ValueError("Specify a dataset for bnn experiment!")
        worker = BNNWorker(dataset=args.dataset_bnn, measure_test_loss=False, run_id=args.run_id,
                           max_budget=args.max_budget, host=host)
    elif exp_name == 'cartpole':
        worker = CartpoleWorker(measure_test_loss=False, run_id=args.run_id, host=host)
    elif exp_name == 'svm_surrogate':
        # this is a synthetic benchmark, so we will use the run_id to separate the independent runs (JM: what's that supposed to mean?)
        worker = SVMSurrogateWorker(surrogate_path=args.surrogate_path, measure_test_loss=True, run_id=args.run_id, host=host)
    elif exp_name == 'paramnet_surrogates':
        if not args.dataset_paramnet_surrogates:
            raise ValueError("Specify a dataset for paramnet surrogates experiment!")
        worker = ParamNetSurrogateWorker(dataset=args.dataset_paramnet_surrogates, surrogate_path=args.surrogate_path,
                                         measure_test_loss=False, run_id=args.run_id, host=host)
    else:
        raise ValueError("{} not a valid experiment name".format(exp_name))
    return worker

def run_experiment(args, worker, dest_dir, smac_deterministic, store_all_runs=False):
    print("Running experiment (args: %s)" % str(args))
    # make sure the working and dest directory exist
    os.makedirs(args.working_directory, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)

    if args.opt_method in ['randomsearch', 'bohb', 'hyperband']:
        print("Using hpbandster-optimizer (%s)" % args.opt_method)
        # Every process has to lookup the hostname
        host = hpns.nic_name_to_host(args.nic_name)
        print("Host: %s" % str(host))

        # setup a nameserver
        NS = hpns.NameServer(run_id=args.run_id,
                             nic_name=args.nic_name,
                             port=0,
                             host=host,
                             working_directory=args.working_directory)
        ns_host, ns_port = NS.start()
        print("Initialized nameserver (ns_host: %s; ns_port: %s)" % (str(ns_host), str(ns_port)))

        if args.worker:
            print("This is a pure worker-thread.")
            worker = get_worker(args, host=host)
            worker.load_nameserver_credentials(working_directory=args.working_directory)
            worker.run(background=False)
            print("Exiting...")
            exit(0)

        print("This is the name-server thread, however there will be a worker running in the background.")
        worker = get_worker(args, host=host)

        # start worker in the background
        worker.load_nameserver_credentials(working_directory=args.working_directory)
        worker.run(background=True)

        if args.exp_name == 'paramnet_surrogates':
            print("This is the paramnet_surrogates experiment, so any custom budgets will be replaced by the "
                  "dataset-specific budgets.")
            args.min_budget, args.max_budget = worker.budgets[args.dataset_paramnet_surrogates]

        print("Background-worker is running, grabbing configspace from worker and initializing result_logger "
              "(with dest_dir %s)" % dest_dir)
        configspace = worker.configspace

        result_logger = hpres.json_result_logger(directory=dest_dir, overwrite=True)

        print("Getting optimizer.")

        opt = get_optimizer(args, configspace, working_directory=args.working_directory,
                            run_id=args.run_id,
                            min_budget=args.min_budget, max_budget=args.max_budget,
                            host=host,
                            nameserver=ns_host,
                            nameserver_port = ns_port,
                            ping_interval=30,
                            result_logger=result_logger,
                           )

        print("Initialization successful, starting optimization.")

        from ConfigSpace.read_and_write import pcs_new
        with open(os.path.join(dest_dir, 'configspace.pcs'), 'w') as fh:
            fh.write(pcs_new.write(opt.config_generator.configspace))

        result = opt.run(n_iterations=args.num_iterations, min_n_workers=args.n_workers)

        print("Finished optimization")
        # shutdown the worker and the dispatcher
        opt.shutdown(shutdown_workers=True)
        NS.shutdown()

    if args.exp_name == 'paramnet_surrogates':
        # This if block is necessary to set budgets for paramnet_surrogates - for nothing else
        args_tmp = copy.deepcopy(args)
        args_tmp.opt_method = 'bohb'
        worker = get_worker(args_tmp)
        args.min_budget, args.max_budget = worker.budgets[args.dataset_paramnet_surrogates]

    # the number of iterations for the blackbox optimizers must be increased so they have comparable total budgets
    bb_iterations = int(args.num_iterations * (1+(np.log(args.max_budget) - np.log(args.min_budget))/np.log(args.eta)))

    #if args.opt_method == 'tpe':
    #    result = worker.run_tpe(bb_iterations)

    if args.opt_method == 'smac':
        result = worker.run_smac(bb_iterations, deterministic=smac_deterministic, working_directory=args.dest_dir)

    if result is None:
        raise ValueError("Unknown method %s!"%args.method)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Running one of the icml 2018 experiments.', conflict_handler='resolve')
    parser = standard_parser_args(parser)

    # Parsing args and creating sub-folders for experiments
    args = parser.parse_args()
    args.dest_dir = os.path.join(args.dest_dir, args.exp_name)
    if args.exp_name == 'bnn':
        args.dest_dir = os.path.join(args.dest_dir, args.dataset_bnn)
    if args.exp_name == 'paramnet_surrogates':
        args.dest_dir = os.path.join(args.dest_dir, args.dataset_paramnet_surrogates)
    args.dest_dir = os.path.join(args.dest_dir, args.opt_method)

    run_experiment(args, args.worker, args.dest_dir, smac_deterministic=True, store_all_runs=False)
