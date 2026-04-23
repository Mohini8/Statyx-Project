import pandas as pd
import matplotlib.pyplot as plt

def categorical_bar_plot(df, col):

    fig, ax = plt.subplots()

    df[col].value_counts().plot.bar(ax=ax)

    ax.set_title(f"{col} Distribution")

    return fig


def categorical_pie_plot(df, col):

    fig, ax = plt.subplots()

    df[col].value_counts().plot.pie(
        ax=ax,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_ylabel("")

    return fig