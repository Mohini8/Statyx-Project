import matplotlib.pyplot as plt
import pandas as pd

def generate_plot(df, plot_type, cols):

    plot_type = plot_type.lower()
    if not cols or len(cols) == 0:
        raise ValueError("At least one column is required for visualization.")

    if plot_type in ["histogram", "boxplot", "pie"] and len(cols) != 1:
        raise ValueError(f"{plot_type.title()} plots require exactly one column.")

    if plot_type in ["scatter", "line"] and len(cols) != 2:
        raise ValueError(f"{plot_type.title()} plots require exactly two columns.")

    if plot_type == "bar" and len(cols) != 2:
        raise ValueError("Bar plots require one categorical column and one numeric column.")

    for col in cols:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' is not present in the dataset.")

    fig, ax = plt.subplots()

    if plot_type == "histogram":
        if not pd.api.types.is_numeric_dtype(df[cols[0]]):
            raise ValueError(f"'{cols[0]}' is not numeric. Histograms require numeric data.")
        df[cols[0]].dropna().plot.hist(ax=ax)

    elif plot_type == "boxplot":
        if not pd.api.types.is_numeric_dtype(df[cols[0]]):
            raise ValueError(f"'{cols[0]}' is not numeric. Box plots require numeric data.")
        df.boxplot(column=cols[0], ax=ax)

    elif plot_type == "scatter":
        if not all(pd.api.types.is_numeric_dtype(df[c]) for c in cols):
            raise ValueError("Both selected columns must be numeric for scatter plots.")
        df.plot.scatter(cols[0], cols[1], ax=ax)

    elif plot_type == "line":
        if not all(pd.api.types.is_numeric_dtype(df[c]) for c in cols):
            raise ValueError("Both selected columns must be numeric for line plots.")
        df.plot(x=cols[0], y=cols[1], ax=ax)

    elif plot_type == "bar":
        if not pd.api.types.is_numeric_dtype(df[cols[1]]):
            raise ValueError(f"'{cols[1]}' must be numeric for bar plot aggregation.")
        df.groupby(cols[0])[cols[1]].mean().plot.bar(ax=ax)

    elif plot_type == "pie":
        if pd.api.types.is_numeric_dtype(df[cols[0]]):
            raise ValueError(f"'{cols[0]}' is numeric. Pie charts require categorical data.")
        df[cols[0]].value_counts().plot.pie(ax=ax, autopct="%1.1f%%", startangle=90)
        ax.set_ylabel("")
        ax.axis("equal")

    else:
        raise ValueError(f"Unsupported plot type: {plot_type}")

    return fig