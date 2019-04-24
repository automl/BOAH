import os
from itertools import product

import hpbandster.core.nameserver as hpns
import hpbandster.core.result as hpres
from hpbandster.optimizers import BOHB, RandomSearch, HyperBand

from workers.bnn_worker import BNNWorker

# Run the experiment

datasets =  ['toyfunction', 'bostonhousing', 'proteinstructure']  # , 'yearprediction']
opt_methods = ["bohb", "randomsearch", "hyperband"] # smac?
num_iterations = 4
max_budget = 10000

eta = 3

for dataset, opt_method in product(datasets, opt_methods):

    print(dataset, opt_method)
    
    output_dir = "opt_results/bnn/{}/{}".format(dataset, opt_method)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    run_id = '0'  # Every run has to have a unique (at runtime) id.

    # setup a nameserver
    NS = hpns.NameServer(run_id=run_id, host='localhost', port=0, working_directory=output_dir)
    ns_host, ns_port = NS.start()

    # create a worker
    worker = BNNWorker(dataset=dataset, measure_test_loss=False, run_id=run_id, max_budget=max_budget)
    configspace = worker.configspace

    worker.load_nameserver_credentials(output_dir)
    worker.run(background=True)

    # instantiate optimizer
    opt = None
    if opt_method == 'randomsearch':
        opt = RandomSearch      
    elif opt_method == 'bohb':
        opt = BOHB              
    elif opt_method == 'hyperband':
        opt = HyperBand
    else:
        raise ValueError("Unknown method %s" % opt_method)

    result_logger = hpres.json_result_logger(directory=output_dir, overwrite=True)

    opt = opt(configspace, eta=3,
              working_directory=output_dir,
              run_id=run_id,
              min_budget=300, max_budget=max_budget,
              host=ns_host,
              nameserver=ns_host,
              nameserver_port = ns_port,
              ping_interval=3600,
              result_logger=result_logger)

    result = opt.run(n_iterations=num_iterations)

    # **NOTE:** Unfortunately, the configuration space is *not saved automatically* to file
    # but this step is mandatory for the analysis with CAVE.  
    # We recommend to save the configuration space every time you use BOHB.
    # We do this by using the ConfigSpace-to-json-writer.

    from ConfigSpace.read_and_write import pcs_new
    with open(os.path.join(output_dir, 'configspace.pcs'), 'w') as fh:
        fh.write(pcs_new.write(opt.config_generator.configspace))
