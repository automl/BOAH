# BOAH Tool Suite

(see also [automl.org](https://www.automl.org/automl/boah/))

## Bayesian Optimization & Analysis of Hyperparameters

Hyperparameter optimization and architecture search can easily become prohibitively expensive for regular black-box
Bayesian optimization as training and validation of a single model can already take several hours. To overcome
this, we introduce a tool suite for multi-fidelity Bayesian optimization that allows the specification of design spaces
(via [ConfigSpace](https://github.com/automl/ConfigSpace))
in Python, the efficient optimization of black-box functions using cheap approximations
(via [BOHB](https://github.com/automl/HpBandSter))
and an automatic analysis of the optimization process and results (via [CAVE](https://github.com/automl/CAVE)) to gain better understanding.

## Content

This repository provides simple examples of how to construct a configuration space using the ConfigSpace package,
how to use BOHB with minimal efforts and how to run CAVE to generate a comprehensive
analysis of BOHB's optimization.

### Example 1: fmin interface

To improve the first-time usage experience, with BOAH we provide an easy-to-use interface for using BOHB with subsequent analyzing, called [fmin](https://github.com/automl/BOAH/blob/master/examples/mlp_on_digits/FMin.py), inspired by the well-known _fmin_ interface of scipy. Check out this [notebook](https://github.com/automl/BOAH/tree/master/examples/mlp_on_digits/notebook.ipynb) to see how it all comes together.

### Example 2: Proximal Policy Optimization on Cartpole

[PPO on Cartpole](https://github.com/automl/BOAH/tree/master/examples/PPO_on_cartpole) optimizes the Proximal Policy Optimization on the well-known reinforcement problem Cartpole. We provide results from a HPC cluster for the optimization data and a notebook to easily reproduce analysis.

### ICML 2018 Experiments

In this [series of notebooks](https://github.com/automl/BOAH/tree/master/examples/icml_2018_experiments) you can reproduce the
experiments described in [BOHB's introduction in 2018 (Falkner et al.)](http://proceedings.mlr.press/v80/falkner18a.html).
The results are available precomputed and ready for analysis, however you can re-run the experiments - just keep in mind,
that the notebooks might run for a long time (several days) for some of the experiments.

## Requirements

This is a Python3 package (developed under Python 3.6).  For convenience, we recommend to install Anaconda with a recent
Python 3 (see also `setup.sh`). If you want to set up the package manually, you find requirements in the `requirements.txt` (or, for the ICML 2018 Experiments, in `examples/icml_2018_experiments/icml2018requirements.txt`).

## About the tools

### ConfigSpace

<a href="https://github.com/automl/ConfigSpace" target="_blank">ConfigSpace</a> is a python module to manage configuration spaces for algorithm configuration and hyperparameter optimization tasks. Supports all common types, like numericals, ordinals, categoricals and also log-scale sampling or conditions. Includes various scripts to translate between different text formats for configuration space description. 

### HpBandSter

<a href="https://github.com/automl/HpBandSter" target="_blank">HpBandSter</a> (HyperBand on Steroids) implements recently published methods for optimizing hyperparameters of machine learning algorithms. One of the implemented algorithms is <a href="https://automl.github.io/HpBandSter/build/html/optimizers/bohb.html" target="_blank">BOHB</a>, combining Bayesian Optimization and HyperBand to efficiently search for well-performing configurations. Learn more about this method by reading our paper, published at <a href="http://proceedings.mlr.press/v80/falkner18a.html" target="_blank">ICML 2018</a>.

### CAVE

<a href="https://github.com/automl/CAVE" target="_blank">CAVE</a> (Configuration Assessment, Visualization, and Evaluation) is designed to create comprehensive reports about an optimization process. The resulting figures and interactive plots can be used to gain insights into the parameter importance, feature importance, search behavior, and quality. Learn more about CAVE from <a href="https://www.ml4aad.org/algorithm-analysis/cave/" target="_blank">our paper</a>.

## License

This package is free software: you can redistribute it and/or modify it under the terms of the Apache license 2.0
(please see the LICENSE file).

## Contact

This repository is developed by the [AutoML Group Freiburg](https://www.automl.org)

## Citing BOAH

```bibtex
@journal{
    title   = {BOAH: A Tool Suite for Multi-Fidelity Bayesian Optimization & Analysis of Hyperparameters},
    author  = {M. Lindauer and K. Eggensperger and M. Feurer and A. Biedenkapp and J. Marben and P. Müller and F. Hutter},
    journal = {arXiv:1908.06756 {[cs.LG]}},
    date    = {2019},
}
```
