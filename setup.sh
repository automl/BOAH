#!/bin/bash

rm virtual_environment_bohb_cave -r
virtualenv -p python3 virtual_environment_bohb_cave
source virtual_environment_bohb_cave/bin/activate
cat requirements.txt | xargs -n 1 -L 1 pip install
