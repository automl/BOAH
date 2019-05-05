#!/bin/bash

cave --folders opt_results/bnn/bostonhousing/bohb --file_format BOHB --output CAVE_reports/bnn_bostonhousing_bohb --verbose_level OFF
cave --folders opt_results/bnn/bostonhousing/hyperband --file_format BOHB --output CAVE_reports/bnn_bostonhousing_hyperband --verbose_level OFF
cave --folders opt_results/bnn/bostonhousing/randomsearch --file_format BOHB --output CAVE_reports/bnn_bostonhousing_randomsearch --verbose_level OFF
cave --folders opt_results/bnn/bostonhousing/smac/* --file_format SMAC3 --output CAVE_reports/bnn_bostonhousing_smac --verbose_level OFF

cave --folders opt_results/bnn/toyfunction/bohb --file_format BOHB --output CAVE_reports/bnn_toyfunction_bohb --verbose_level OFF
cave --folders opt_results/bnn/toyfunction/hyperband --file_format BOHB --output CAVE_reports/bnn_toyfunction_hyperband --verbose_level OFF
cave --folders opt_results/bnn/toyfunction/randomsearch --file_format BOHB --output CAVE_reports/bnn_toyfunction_randomsearch --verbose_level OFF
cave --folders opt_results/bnn/toyfunction/smac/* --file_format SMAC3 --output CAVE_reports/bnn_toyfunction_smac --verbose_level OFF

cave --folders opt_results/bnn/proteinstructure/bohb --file_format BOHB --output CAVE_reports/bnn_proteinstructure_bohb --verbose_level OFF
cave --folders opt_results/bnn/proteinstructure/hyperband --file_format BOHB --output CAVE_reports/bnn_proteinstructure_hyperband --verbose_level OFF
cave --folders opt_results/bnn/proteinstructure/randomsearch --file_format BOHB --output CAVE_reports/bnn_proteinstructure_randomsearch --verbose_level OFF
cave --folders opt_results/bnn/proteinstructure/smac/* --file_format SMAC3 --output CAVE_reports/bnn_proteinstructure_smac --verbose_level OFF

cave --folders opt_results/cartpole/bohb --file_format BOHB --output CAVE_reports/cartpole_bohb --verbose_level OFF
cave --folders opt_results/cartpole/hyperband --file_format BOHB --output CAVE_reports/cartpole_hyperband --verbose_level OFF
cave --folders opt_results/cartpole/randomsearch --file_format BOHB --output CAVE_reports/cartpole_randomsearch --verbose_level OFF
cave --folders opt_results/cartpole/smac/* --file_format SMAC3 --output CAVE_reports/cartpole_smac --verbose_level OFF

cave --folders opt_results/svm_surrogate/bohb --file_format BOHB --output CAVE_reports/svm_surrogate_bohb --verbose_level OFF
cave --folders opt_results/svm_surrogate/hyperband --file_format BOHB --output CAVE_reports/svm_surrogate_hyperband --verbose_level OFF
cave --folders opt_results/svm_surrogate/randomsearch --file_format BOHB --output CAVE_reports/svm_surrogate_randomsearch --verbose_level OFF
cave --folders opt_results/svm_surrogate/smac/* --file_format SMAC3 --output CAVE_reports/svm_surrogate_smac --verbose_level OFF

cave --folders opt_results/paramnet_surrogate/adult/bohb --file_format BOHB --output CAVE_reports/paramnet_surrogate_adult_bohb --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/adult/hyperband --file_format BOHB --output CAVE_reports/paramnet_surrogate_adult_hyperband --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/adult/randomsearch --file_format BOHB --output CAVE_reports/paramnet_surrogate_adult_randomsearch --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/adult/smac/* --file_format SMAC3 --output CAVE_reports/paramnet_surrogate_adult_smac --verbose_level OFF

cave --folders opt_results/paramnet_surrogate/higgs/bohb --file_format BOHB --output CAVE_reports/paramnet_surrogate_higgs_bohb --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/higgs/hyperband --file_format BOHB --output CAVE_reports/paramnet_surrogate_higgs_hyperband --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/higgs/randomsearch --file_format BOHB --output CAVE_reports/paramnet_surrogate_higgs_randomsearch --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/higgs/smac/* --file_format SMAC3 --output CAVE_reports/paramnet_surrogate_higgs_smac --verbose_level OFF

cave --folders opt_results/paramnet_surrogate/letter/bohb --file_format BOHB --output CAVE_reports/paramnet_surrogate_letter_bohb --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/letter/hyperband --file_format BOHB --output CAVE_reports/paramnet_surrogate_letter_hyperband --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/letter/randomsearch --file_format BOHB --output CAVE_reports/paramnet_surrogate_letter_randomsearch --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/letter/smac/* --file_format SMAC3 --output CAVE_reports/paramnet_surrogate_letter_smac --verbose_level OFF

cave --folders opt_results/paramnet_surrogate/mnist/bohb --file_format BOHB --output CAVE_reports/paramnet_surrogate_mnist_bohb --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/mnist/hyperband --file_format BOHB --output CAVE_reports/paramnet_surrogate_mnist_hyperband --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/mnist/randomsearch --file_format BOHB --output CAVE_reports/paramnet_surrogate_mnist_randomsearch --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/mnist/smac/* --file_format SMAC3 --output CAVE_reports/paramnet_surrogate_mnist_smac --verbose_level OFF

cave --folders opt_results/paramnet_surrogate/optdigits/bohb --file_format BOHB --output CAVE_reports/paramnet_surrogate_optdigits_bohb --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/optdigits/hyperband --file_format BOHB --output CAVE_reports/paramnet_surrogate_optdigits_hyperband --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/optdigits/randomsearch --file_format BOHB --output CAVE_reports/paramnet_surrogate_optdigits_randomsearch --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/optdigits/smac/* --file_format SMAC3 --output CAVE_reports/paramnet_surrogate_optdigits_smac --verbose_level OFF

cave --folders opt_results/paramnet_surrogate/poker/bohb --file_format BOHB --output CAVE_reports/paramnet_surrogate_poker_bohb --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/poker/hyperband --file_format BOHB --output CAVE_reports/paramnet_surrogate_poker_hyperband --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/poker/randomsearch --file_format BOHB --output CAVE_reports/paramnet_surrogate_poker_randomsearch --verbose_level OFF
cave --folders opt_results/paramnet_surrogate/poker/smac/* --file_format SMAC3 --output CAVE_reports/paramnet_surrogate_poker_smac --verbose_level OFF
