# BOHB's CAVE

Hyperparameter optimization and architecture search can easily become prohibitively expensive for regular black-box
Bayesian optimization because training and validation of a single model can already take several hours. To overcome
this, we introduce a tool suite for multi-fidelity Bayesian optimization that allows the specification of design spaces
in Python, the efficient optimization of black-box functions by using cheap approximations and an automatic analysis of
of the optimization process and results to gain better understanding.

## Content

This repository provides an example how to use BOHB with minimal efforts and how to run CAVE to generate a comprehensive
analysis of BOHB's outcomes.

### Toy Example

An easily adaptable [step-for-step tutorial](http://github.com/automl/BOHBsCAVE/examples/mlp_on_digits) on how to use BOHB with CAVE. In this notebook, there is an
exemplary optimization of a simple multi-layer perceptron on the digits dataset with a subsequent analysis through CAVE.

### ICML 2018 Experiments

In this [series of notebooks](http://github.com/automl/BOHBsCAVE/examples/icml_2018_experiments) you can reproduce the experiments described in
[BOHB's introduction in 2018 (Falkner et al.)](http://proceedings.mlr.press/v80/falkner18a.html).
The results are available precomputed and ready for analysis, however you can rerun the experiments - just keep in mind,
that the notebooks might run for a long time (several days) for some of the experiments.

### Plug-and-Play your own example

(coming soon)

## Requirements

This is a Python3 package (developed under Python 3.6).  For convenience, we recommend to install Anaconda with a recent
Python 3 (see also `setup.sh`).

## Content

 * `setup.sh` provides a simple BASH script to create an anaconda environment and installs all requirements from
   `requirements.txt`
 * `examples/EasyOpt.py` provides an easy command line interface to run BOHB
 * `examples/notebook_mlp_on_digits.ipynb` is a Jyputer notebook showing and explaining how to use BOHB for optimizing
   the hyperparameters of a simple MLP network on the DIGITS dataset
 * `examples/example_mlp_on_digits.py` implements the network and the hyperparameter optimization space

## License

This program is free software: you can redistribute it and/or modify it under the terms of the Apache license 2.0
(please see the LICENSE file).

## Contact

This repository is developed by the [AutoML Group Freiburg](https://www.automl.org)
