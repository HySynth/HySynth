# HySynth

*HySynth* is a tool to automatically synthesize a mathematical model for a
dynamical system.
*HySynth* receives the following inputs:
1. data in the form of (a collection of) *time series*
2. a number epsilon
*HySynth* outputs a *hybrid automaton* model with the guarantee that the model
contains trajectories that are epsilon-close to the time-series data.

The theoretical background of the synthesis algorithms implemented in *HySynth*
is explained in [1] and [2], which we summarize next.


### Piecewise-constant dynamics

The algorithm in [1] constructs a model whose continuous dynamics are given by
piecewise-constant ordinary differential equations (ODEs).
The trajectories, which are the solutions of these ODEs, are piecewise-linear
functions.
In the code base this model class is called `pwl` (for PieceWise Linear).
There are two related algorithms in this setting.
The first algorithm is based on geometry and reachability analysis.
The first algorithm is based on satisfiability modulo theories (SMT).
The implementation is written in Python.


### Piecewise-linear dynamics

The algorithm in [2] constructs a model whose continuous dynamics are given by
piecewise-linear ODEs.
The trajectories, which are the solutions of these ODEs, are exponential
functions.
In the code base this model class is called `pwld` (for PieceWise Linear
Dynamics).
This algorithm is based on reachability analysis, ODE solving, and optimization.
The implementation of the high-level algorithm is written in Python while the
low-level functionality is written in Julia.



## Instructions to install HySynth

This section summarizes the installation instructions.


### Required software

* Python 3
* Further dependencies of the used Python packages (see below)


#### Optional dependencies

* Julia (we used v1.5.3)
  This is only needed for the `pwld` algorithm.
  Make sure `julia` is available in your PATH, e.g., by adding the following to
  `~/.profile` and logging off and on:

    PATH=$PATH:$HOME/PATH_TO_JULIA/bin"

  If the installer warns about a statically linked Python interpreter, Julia
  executions will become terribly slow.
  We strongly recommend using one of the workarounds suggested in the given
  troubleshooting link in this case, for example `python-jl`:

    PYTHONPATH=$PYTHONPATH:$PWD python-jl examples/SCRIPT.py

* Z3
  This is only needed for a `pwl` algorithm that use an SMT solver.
  Make sure `z3` is available in your PATH.


### Install the software and dependencies

#### Python 3

  Install the packages in `requirements.txt`.
  Below is a short manual for installing these things on a Debian Linux:

  * sudo apt install python3 python3-pip
  * pip3 install -r requirements.txt

  The installation of pplpy may fail due to missing dependencies.
  On a Debian Linux run:

  * sudo apt-get install libgmp-dev libmpfr-dev libmpc-dev libppl-dev cython swig
  * pip3 install cysignals --user
  * pip3 install gmpy2 --pre --user
  * pip3 install pplpy

  Do not forget to install the missing requirements from requirements.txt if
  there was an error.

#### Julia

  Install the following packages (via `pkg> add PACKAGE` from the Julia REPL):

  * PyCall
  * LazySets
  * MathematicalSystems
  * Optim
  * Distributions
  * Polyhedra
  * CDDLib
  * DifferentialEquations
  * ReachabilityAnalysis (or, if you use a Julia below v1.3, use `Reachability`
    via `pkg> add https://github.com/JuliaReach/Reachability.jl`)

  Note that the first time these packages are loaded after downloading them,
  they get precompiled (for Julia older than v1.6), which may take a long time.
  Precompilation can be triggered by `julia> using PACKAGE`.

  The package `PyCall` for the Python-Julia bridge needs to be installed
  separately, for which you can run the following in Python:

  import julia
  julia.install()



## Instructions to run HySynth

This section explains a quick start to *HySynth*.
As example we look at the benchmark script to reproduce the results for [2].

* Open a terminal in the *HySynth* folder.

* Run the benchmark script `run_benchmarks_HSCC2021.sh`.

    ./run_benchmarks_HSCC2021.sh

Unfortunately the Julia-Python bridge is not very stable and often results in
segmentation faults.
To skip benchmarks, one can edit the benchmark script
`examples/experiments_HSCC2021`.
The function `run_all` at the bottom runs the benchmarks sequentially.
Just comment out the benchmarks that have already run (adding a `#` in front).

*HySynth* stores the intermediate results (hybrid automata and approximated
functions) in the folder `data/saved_models` such that they can be reloaded (to
reduce the cost of rerunning the experiments in case of a crash).
These intermediate results are not used by default but can be reused with the
`load` flag in the benchmark script (`examples/experiments_HSCC2021`), by
replacing `load = False` or `load=False` with `load = True`.


## References

[1] Miriam García Soto, Thomas A. Henzinger, Christian Schilling, and Luka
Zeleznik:
*Membership-Based Synthesis of Linear Hybrid Automata*.
Proceedings of the 31st International Conference on Computer Aided Verification
(CAV) 2019.
[DOI](https://doi.org/10.1007/978-3-030-25540-4_16).
[PDF](https://research-explorer.app.ist.ac.at/record/6493).


[2] Miriam García Soto, Thomas A. Henzinger, and Christian Schilling:
*Synthesis of Hybrid Automata with Affine Dynamics from Time-Series Data*.
Proceedings of the 24th International Conference on Hybrid Systems: Computation
and Control (HSCC) 2021.
