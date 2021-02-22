import pandas as pd
import matplotlib.pyplot as plt


def show_example(original_dataset, resulting_dataset, title1="Data generated from original automaton",
                 title2="Data generated from resulting automaton"):

    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True)

    plot_dset(dataset=original_dataset,
              title=title1,
              axes=ax1)

    plot_dset(dataset=resulting_dataset,
              title=title2,
              axes=ax2)

    plt.show()

    return fig


def plot_dset(dataset, title, axes):

    if isinstance(dataset, list):
        for pwl_line in dataset:
            x, y = zip(*pwl_line)
            axes.plot(x, y, linewidth=2.0)
            axes.spines['top'].set_visible(False)
            axes.spines['right'].set_visible(False)
            axes.set(ylim=[0, 10])
            axes.tick_params(axis='both', which='major', labelsize=15)
            # axes.set_title(title)

    elif isinstance(dataset, pd.DataFrame):
        for _, series in dataset.iterrows():
            axes.plot(series)
            axes.set_title(title)

    else:
        raise NotImplementedError("This datatype is not supported!")
