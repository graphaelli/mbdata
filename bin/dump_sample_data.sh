#!/usr/bin/env bash

python -m mbdata.tools.dump_sample_data -d "$1" >mbdata/api/tests/sample_data.py

