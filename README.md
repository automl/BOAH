# BOHB's CAVE

Hyperparameter optimization and architecture search can easily become prohibitively expensive for regular black-box Bayesian optimization because training and validation of a single model can already take several hours. To overcome this, we introduce a tool suite for multi-fidelity Bayesian optimization that allows the specification of design spaces in Python, the efficient optimization of black-box functions by using cheap approximations and an automatic analysis of of the optimization process and results to gain better understanding.

## Repository

This repository provides an example how to use BOHB with minimal efforts and how to run CAVE to generate a comprehensive analysis of BOHB's outcomes.

## Requirements

This is a Python3 package (developed under Python 3.6). 
For convenience, we recommend to install Anaconda with a recent Python 3 (see also `setup.sh`).

## Content

 * `setup.sh` provides a simple BASH script to create an anaconda environment and installs all requirements from `requirements.txt`
 * `examples/EasyOpt.py` provides an easy command line interface to run BOHB
 * `examples/notebook_mlp_on_digits.ipynb` is a Jyputer notebook showing and explaining how to use BOHB for optimizing the hyperparameters of a simple MLP network on the DIGITS dataset
 * `examples/example_mlp_on_digits.py` implements the network and the hyperparameter optimization space

## License

This program is free software: you can redistribute it and/or modify it under the terms of the Apache license 2.0 (please see the LICENSE file).

## Contact

This repository is developed by the [AutoML Group Freiburg](https://www.automl.org)
