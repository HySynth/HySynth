import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint


def plot_time_series(time_series):
    # TODO generalize to more than one dimension
    if len(time_series[0]) > 2:
        raise(ValueError("only 1D time-series plotting is supported at the moment"))
    plt.scatter(*zip(*time_series), c="r")


def plot_pwld_function(pwld_function, color="b", style=None, phase_portrait=False):
    if style is None:
        style = ["{}-".format(color), "{}:".format(color), "{}--".format(color), "{}-.".format(color)]

    dyn_t, x0, epsilon = pwld_function
    odes = []
    times = []
    t0 = 0.0
    for dyn, T in dyn_t:
        time_span = np.linspace(t0, T)
        t0 = T
        A = dyn.A()
        b = dyn.b()
        f = lambda x, t: A.dot(x) + b
        s = odeint(f, x0, time_span)
        x0 = s[-1]
        odes.append(s)
        times.append(time_span)
        n = dyn.dim()
        if phase_portrait is not None and phase_portrait is not False:
            if phase_portrait is True:
                phase_portrait = [0, 1]
            for s, time_span in zip(odes, times):
                plt.plot(s[:, phase_portrait[0]], s[:, phase_portrait[1]], style[0], linewidth=2.0)
        else:
            for i in range(n):
                style_i = style[i % n]
                for s, time_span in zip(odes, times):
                    plt.plot(time_span, s[:, i], style_i, linewidth=2.0)


def plot_pwld_function_and_time_series(pwld_function, time_series, file_name, color_pwld="b", style_pwld=None,
                                       clean=True, xlim=None):
    plot_time_series(time_series)
    plot_pwld_function(pwld_function, color=color_pwld, style=style_pwld)
    if xlim is not None:
        plt.xlim(right=xlim)
    if file_name is not None:
        plt.savefig(file_name)
    if clean:
        plt.clf()


def plot_pwld_functions(pwld_functions, file_name=None, color="b", style=None, clean=True, xlim=None,
                        phase_portrait=False):
    for f in pwld_functions:
        plot_pwld_function(f, color=color, style=style, phase_portrait=phase_portrait)
    if xlim is not None:
        plt.xlim(right=xlim)
    if file_name is not None:
        plt.savefig(file_name)
    if clean:
        plt.clf()


def plot_pwld_functions_and_time_series(pwld_functions, time_series, file_names=None, clean=True, xlim=None):
    if file_names is None:
        file_names = ["plot_{:d}.pdf".format(i) for i in range(1, len(pwld_functions) + 1)]
    for (f, ts, fn) in zip(pwld_functions, time_series, file_names):
        plot_pwld_function_and_time_series(f, ts, fn, clean=clean, xlim=xlim)
