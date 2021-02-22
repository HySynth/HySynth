using PyCall
py"""
from julia import Julia
Julia(init_julia=False)
from examples.experiments_HSCC2021 import run_all
run_all()
"""
