from visualization.categorical_plots import (
    categorical_bar_plot,
    categorical_pie_plot
)

from visualization.numeric_plots import (
    histogram_plot,
    boxplot_plot,
    scatter_plot,
    line_plot
)

import pandas as pd

def build_chart(df, plot_type, cols):

    if plot_type == "histogram":
        return histogram_plot(df, cols[0])

    elif plot_type == "boxplot":
        return boxplot_plot(df, cols[0])

    elif plot_type == "scatter":
        return scatter_plot(df, cols[0], cols[1])

    elif plot_type == "line":
        return line_plot(df, cols[0], cols[1])

    elif plot_type == "bar":

        if not pd.api.types.is_numeric_dtype(df[cols[1]]):
            raise ValueError("Second column must be numeric")

        grouped = df.groupby(cols[0])[cols[1]].mean().reset_index()

        return categorical_bar_plot(grouped, cols[0])

    elif plot_type == "pie":

        if pd.api.types.is_numeric_dtype(df[cols[0]]):
            raise ValueError("Pie requires categorical column")

        return categorical_pie_plot(df, cols[0])

    else:
        raise ValueError("Invalid plot type")