#!/bin/bash
PYTHONPATH=$PYTHONPATH:$PWD julia -e 'include("run_no_venv.jl")'
