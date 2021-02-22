import matplotlib.pyplot as plt


def pointsplot(tuplelist):
    plt.scatter(*zip(*tuplelist))
    plt.show()


def lineplot(tuplelist):
    plt.plot(*zip(*tuplelist))
    plt.show()


def multilineplot(listoftuplelist):
    for list in listoftuplelist:
        plt.plot(*zip(*list))
    plt.show()
