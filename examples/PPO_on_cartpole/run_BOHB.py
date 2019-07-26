import logging
logging.basicConfig(level=logging.INFO)

import argparse
import pickle
import os
import shutil
import time

import hpbandster.core.nameserver as hpns
import hpbandster.core.result as hpres
from hpbandster.optimizers import BOHB as BOHB
from hpbandster.core.worker import Worker

import hpolib.benchmarks.rl.cartpole as cartpole

import tensorflow as tf
import ConfigSpace.configuration_space as cs
import ConfigSpace.read_and_write.json as pcs_out

session_conf = tf.ConfigProto(
      intra_op_parallelism_threads=1,
      inter_op_parallelism_threads=1)
sess = tf.Session(config=session_conf)
MOAB_JOBID=4598620


class MyWorker(Worker):

    def compute(self, config, budget, **kwargs):
        b = cartpole.CartpoleReduced(rng=1)
        config = cs.Configuration(b.get_configuration_space(), config)
        res_val = b.objective_function(configuration=config, budget=int(budget))

        return({
            'loss': res_val['function_value'],
            'info': res_val
        })

    @staticmethod
    def get_configspace():
        return cartpole.CartpoleReduced.get_configuration_space()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--n_iterations', type=int,   help='Number of iterations performed by the optimizer', default=4)
    parser.add_argument('--worker', help='Flag to turn this into a worker process', action='store_true')
    parser.add_argument('--run_id', type=str, help='A unique run id for this optimization run. An easy option is to use'
                                                   ' the job id of the clusters scheduler.')
    parser.add_argument('--shared_directory', type=str, help='A directory that is accessible for all processes, e.g. a NFS share.')
    parser.add_argument('--interface', type=str, help='Which network interface to use', default="eth1")

    args = parser.parse_args()

    try:
        os.mkdir(args.shared_directory)
    except FileExistsError:
        pass

    # Every process has to lookup the hostname
    host = hpns.nic_name_to_host(args.interface)

    if args.worker:
        time.sleep(60)   # short artificial delay to make sure the nameserver is already running
        w = MyWorker(run_id=args.run_id, host=host)
        w.load_nameserver_credentials(working_directory=args.shared_directory)
        w.run(background=False)
        exit(0)

    # Write the configspace
    cs = MyWorker.get_configspace()
    with open(os.path.join(args.shared_directory, 'configspace.json'), "w") as fh:
        fh.write(
            pcs_out.write(cs)
        )

    result_logger = hpres.json_result_logger(directory=args.shared_directory, overwrite=True)
    NS = hpns.NameServer(run_id=args.run_id, host=host, port=0, working_directory=args.shared_directory)
    ns_host, ns_port = NS.start()

    w = MyWorker(run_id=args.run_id, host=host, nameserver=ns_host, nameserver_port=ns_port)
    w.run(background=True)

    # Run an optimizer
    # We now have to specify the host, and the nameserver information
    bohb = BOHB(configspace=cs,
                run_id=args.run_id,
                host=host,
                nameserver=ns_host,
                nameserver_port=ns_port,
                eta=3,
                result_logger=result_logger,
                min_budget=1, max_budget=9
                )
    res = bohb.run(n_iterations=args.n_iterations, min_n_workers=1)

    # In a cluster environment, you usually want to store the results for later analysis.
    # One option is to simply pickle the Result object
    with open(os.path.join(args.shared_directory, 'results.pkl'), 'wb') as fh:
        pickle.dump(res, fh)

    # Step 4: Shutdown
    # After the optimizer run, we must shutdown the master and the nameserver.
    bohb.shutdown(shutdown_workers=True)
    NS.shutdown()


if __name__ == "__main__":
    main()

