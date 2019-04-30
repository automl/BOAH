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
