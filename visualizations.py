"""
Visualization functions for the Business Intelligence Dashboard.
Provides chart generation utilities using matplotlib and seaborn.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def create_time_series_plot(df, date_col, value_col, agg="sum"):
    """
    Create a time series line chart with an aggregation function.

    Parameters
    ----------
    df : DataFrame
        Dataset containing the time series data.
    date_col : str
        Column containing date values.
    value_col : str
        Column containing numeric values to aggregate.
    agg : str, optional
        Aggregation method: 'sum', 'mean', 'count', or 'median'.

    Returns
    -------
    matplotlib.figure.Figure or None
        Generated figure, or None if inputs are invalid.
    """
    if df is None or not date_col or not value_col:
        return None

    temp = df.copy()
    temp["_date"] = pd.to_datetime(
        temp[date_col], dayfirst=True, errors="coerce"
    ).dt.to_period("D").astype(str)

    if agg == "sum":
        grouped = temp.groupby("_date")[value_col].sum()
    elif agg == "mean":
        grouped = temp.groupby("_date")[value_col].mean()
    elif agg == "count":
        grouped = temp.groupby("_date")[value_col].count()
    else:
        grouped = temp.groupby("_date")[value_col].median()

    fig, ax = plt.subplots(figsize=(10, 5))
    grouped.plot(ax=ax, linewidth=2)
    ax.set_title(f"{value_col} ({agg}) Over Time", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel(f"{value_col} ({agg})", fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig


def create_distribution_plot(df, col, chart_type="histogram"):
    """
    Create a distribution plot for a numeric column.

    Parameters
    ----------
    df : DataFrame
        Dataset containing the column.
    col : str
        Column to visualize.
    chart_type : str, optional
        Either 'histogram' or 'box'.

    Returns
    -------
    matplotlib.figure.Figure or None
        Generated figure, or None if inputs are invalid.
    """
    if df is None or not col:
        return None

    fig, ax = plt.subplots(figsize=(10, 5))

    if chart_type == "histogram":
        df[col].hist(ax=ax, bins=50, edgecolor="black", color="steelblue")
        ax.set_xlabel(col, fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.set_title(f"Distribution of {col}", fontsize=14)
    else:
        df.boxplot(column=col, ax=ax, patch_artist=True)
        ax.set_title(f"Box Plot of {col}", fontsize=14)
        ax.set_ylabel(col, fontsize=12)

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return fig


def create_category_bar_chart(df, cat_col, value_col, agg="sum", top_n=20):
    """
    Create a bar chart showing aggregated values by category.

    Parameters
    ----------
    df : DataFrame
        Dataset containing the columns.
    cat_col : str
        Categorical column name.
    value_col : str
        Numeric column to aggregate.
    agg : str, optional
        Aggregation method: 'sum', 'mean', 'count', or 'median'.
    top_n : int, optional
        Number of top categories to display.

    Returns
    -------
    matplotlib.figure.Figure or None
        Generated figure, or None if inputs are invalid.
    """
    if df is None or not cat_col or not value_col:
        return None

    if agg == "sum":
        grouped = df.groupby(cat_col)[value_col].sum()
    elif agg == "mean":
        grouped = df.groupby(cat_col)[value_col].mean()
    elif agg == "count":
        grouped = df.groupby(cat_col)[value_col].count()
    else:
        grouped = df.groupby(cat_col)[value_col].median()

    grouped = grouped.sort_values(ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    grouped.plot(kind="bar", ax=ax, edgecolor="black", color="coral")
    ax.set_title(
        f"{value_col} ({agg}) by {cat_col} (Top {top_n})",
        fontsize=14
    )
    ax.set_xlabel(cat_col, fontsize=12)
    ax.set_ylabel(f"{value_col} ({agg})", fontsize=12)
    ax.grid(True, alpha=0.3, axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    return fig


def create_scatter_plot(df, x_col, y_col, sample_size=5000):
    """
    Create a scatter plot showing the relationship between two numeric variables.

    Parameters
    ----------
    df : DataFrame
        Input dataset.
    x_col : str
        Column for the x-axis.
    y_col : str
        Column for the y-axis.
    sample_size : int, optional
        Maximum number of points to display.

    Returns
    -------
    matplotlib.figure.Figure or None
        Generated figure, or None if inputs are invalid.
    """
    if df is None or not x_col or not y_col:
        return None

    sample = df if len(df) < sample_size else df.sample(sample_size)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(sample[x_col], sample[y_col], alpha=0.5, s=20, color="teal")
    ax.set_title(f"{y_col} vs {x_col}", fontsize=14)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    return fig


def create_correlation_heatmap(df, figsize=(10, 8)):
    """
    Create a heatmap showing correlation values between numeric columns.

    Parameters
    ----------
    df : DataFrame
        Dataset from which to compute correlations.
    figsize : tuple, optional
        Size of the output figure.

    Returns
    -------
    matplotlib.figure.Figure or None
        Generated heatmap, or None if no numeric columns exist.
    """
    if df is None:
        return None

    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return None

    corr = numeric_df.corr()

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        center=0,
        ax=ax,
        fmt=".2f",
        square=True,
        linewidths=0.5
    )
    ax.set_title("Correlation Heatmap", fontsize=14)
    plt.tight_layout()

    return fig


def save_plot_as_png(fig, filename):
    """
    Save a matplotlib figure to a PNG file.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    filename : str
        Destination file path.

    Returns
    -------
    str or None
        File path if successful, otherwise None.
    """
    if fig is None:
        return None

    fig.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return filename
