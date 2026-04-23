import matplotlib.pyplot as plt

def histogram_plot(df, col):

    fig, ax = plt.subplots()

    df[col].dropna().plot.hist(ax=ax)

    ax.set_title(f"{col} Histogram")

    return fig


def boxplot_plot(df, col):

    fig, ax = plt.subplots()

    df.boxplot(column=col, ax=ax)

    ax.set_title(f"{col} Boxplot")

    return fig


def scatter_plot(df, col1, col2):

    fig, ax = plt.subplots()

    df.plot.scatter(col1, col2, ax=ax)

    return fig


def line_plot(df, col1, col2):

    fig, ax = plt.subplots()

    df.plot(x=col1, y=col2, ax=ax)

    return fig