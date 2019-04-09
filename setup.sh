#!/bin/bash

conda create -n bohb_cave pip
conda activate bohb_cave
cat requirements.txt | xargs -n 1 -L 1 pip install
