import os
import pickle

import numpy as np

import hpbandster.core.nameserver as hpns
from hpbandster.optimizers import RandomSearch, BOHB, HyperBand
import hpbandster.core.result as hpres

from workers.bnn_worker import BNNWorker
from workers.cartpole_worker import CartpoleReducedWorker as CartpoleWorker

def standard_parser_args(parser):
    parser.add_argument('--dest_dir', type=str, help='the destination directory. A new subfolder is created for each benchmark/dataset.', default='../results/')
    parser.add_argument('--num_iterations', type=int, help='number of Hyperband iterations performed.', default=4)
    parser.add_argument('--exp_name', type=str, default='bnn', help='Possible choices: bnn, cartpole, svm_surrogate, paramnet_surrogate')
    parser.add_argument('--method', type=str, default='randomsearch', help='Possible choices: randomsearch, bohb, hyperband, tpe, smac')
    parser.add_argument('--min_budget', type=float, help='Minimum budget for Hyperband and BOHB.')
    parser.add_argument('--max_budget', type=float, help='Maximum budget for all methods.')
    parser.add_argument('--eta', type=float, help='Eta value for Hyperband/BOHB.', default=3)
    # Network / cluster args for HpBandSter-methods
    parser.add_argument('--n_workers', type=int, help='Number of workers to run in parallel.', default=4)
    parser.add_argument('--worker', help='Flag to turn this into a worker process', action='store_true')
    parser.add_argument('--nic_name', type=str, default='lo', help='name of the network interface used for communication. Note: default is only for local execution on *nix!')
    parser.add_argument('--run_id', type=str, default=0)
    parser.add_argument('--working_directory', type=str, help='Directory holding live rundata. Should be shared across all nodes for parallel optimization.', default='/tmp/')
    # Only relevant for some experiments
    parser.add_argument('--dataset', type=str, help='Only for bnn. Choose from toyfunction, bostonhousing, proteinstructure.', default=None)
    return parser

def get_optimizer(parsed_args, config_space, **kwargs):
    eta = parsed_args.eta
    opt = None
    if parsed_args.method == 'randomsearch':
        opt = RandomSearch
    if parsed_args.method == 'bohb':
        opt = BOHB
    if parsed_args.method == 'hyperband':
        opt = HyperBand
    if opt is None:
        raise ValueError("Unknown method %s"%parsed_args.method)
    return opt(config_space, eta=eta, **kwargs)

def get_worker(args):
    exp_name = args.exp_name
    if exp_name == 'bnn':
        if not args.dataset:
            raise ValueError("Specify a dataset for bnn experiment!")
        worker = BNNWorker(dataset=args.dataset, measure_test_loss=False, run_id=args.run_id, max_budget=args.max_budget)
    elif exp_name == 'cartpole':
        worker = CartpoleWorker(measure_test_loss=False, run_id=args.run_id)

    else:
        raise ValueError("{} not a valid experiment name".format(exp_name))
    return worker

def run_experiment(args, worker, dest_dir, smac_deterministic, store_all_runs=False):
    # make sure the working and dest directory exist
    os.makedirs(args.working_directory, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)

    if args.method in ['randomsearch', 'bohb', 'hyperband']:
        # Every process has to lookup the hostname
        host = hpns.nic_name_to_host(args.nic_name)

        # setup a nameserver
        NS = hpns.NameServer(run_id=args.run_id, nic_name=args.nic_name, host=host, working_directory=args.working_directory)
        ns_host, ns_port = NS.start()

        if args.worker:
            time.sleep(5)    # short artificial delay to make sure the nameserver is already running
            worker = get_worker(args, host=host)
            worker.load_nameserver_credentials(working_directory=args.working_directory)
            worker.run(background=False)
            exit(0)

        # start worker in the background
        worker.load_nameserver_credentials(args.working_directory)
        worker.run(background=True)

        configspace = worker.configspace

        result_logger = hpres.json_result_logger(directory=dest_dir, overwrite=True)

        opt = get_optimizer(args, configspace, working_directory=args.dest_dir,
                            run_id = args.run_id,
                            min_budget=args.min_budget, max_budget=args.max_budget,
                            host=ns_host,
                            nameserver=ns_host,
                            nameserver_port = ns_port,
                            ping_interval=3600,
                            result_logger=result_logger,
                           )

        result = opt.run(n_iterations=args.num_iterations, min_n_workers=args.n_workers)

        # shutdown the worker and the dispatcher
        opt.shutdown(shutdown_workers=True)
        NS.shutdown()


        from ConfigSpace.read_and_write import pcs_new
        with open(os.path.join(dest_dir, 'configspace.pcs'), 'w') as fh:
            fh.write(pcs_new.write(opt.config_generator.configspace))

    # the number of iterations for the blackbox optimizers must be increased so they have comparable total budgets
    bb_iterations = int(args.num_iterations * (1+(np.log(args.max_budget) - np.log(args.min_budget))/np.log(args.eta)))

    if args.method == 'tpe':
        result = worker.run_tpe(bb_iterations)

    if args.method == 'smac':
        result = worker.run_smac(bb_iterations, deterministic=smac_deterministic)

    if result is None:
        raise ValueError("Unknown method %s!"%args.method)

    return result
