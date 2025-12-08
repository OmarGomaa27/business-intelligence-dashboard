"""
Automated insight generation for the Business Intelligence Dashboard.
Provides functions for analyzing trends, anomalies, and summary patterns
in tabular datasets.
"""

import pandas as pd
import numpy as np


def identify_top_bottom_performers(df, group_col, value_col, n=10):
    """
    Identify the top and bottom performing groups based on aggregated values.

    Parameters
    ----------
    df : DataFrame
        Input dataset.
    group_col : str
        Column used for grouping.
    value_col : str
        Column used for aggregation.
    n : int, optional
        Number of top and bottom items to return.

    Returns
    -------
    tuple of DataFrame or (None, None)
        DataFrames for top performers and bottom performers.
    """
    if df is None or not group_col or not value_col:
        return None, None

    grouped = df.groupby(group_col)[value_col].sum().sort_values(ascending=False)

    top_n = grouped.head(n).reset_index()
    top_n.columns = [group_col, f"Total {value_col}"]

    bottom_n = grouped.tail(n).reset_index()
    bottom_n.columns = [group_col, f"Total {value_col}"]

    return top_n, bottom_n


def detect_missing_values(df):
    """
    Analyze missing values in the dataset and summarize findings.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    str
        Text summary describing missing value patterns.
    """
    if df is None:
        return ""

    insights = []
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)

    cols_with_missing = missing[missing > 0]

    if len(cols_with_missing) > 0:
        insights.append(f"**Missing Data:** {len(cols_with_missing)} columns contain missing values.")
        for col in cols_with_missing.index[:5]:
            insights.append(f"- {col}: {missing_pct[col]}% missing ({missing[col]:,} rows)")
    else:
        insights.append("**Data Quality:** No missing values detected.")

    return "\n".join(insights)


def detect_anomalies(df, n_std=3):
    """
    Detect potential anomalies in numeric columns using simple heuristic checks.

    Parameters
    ----------
    df : DataFrame
    n_std : int, optional
        Number of standard deviations used to flag outliers.

    Returns
    -------
    str
        Text summary of detected anomalies.
    """
    if df is None:
        return ""

    insights = []
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    for col in numeric_cols[:5]:
        col_lower = col.lower()

        # Detect unexpected negative values
        if any(word in col_lower for word in ["quantity", "amount", "price", "sales"]):
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                insights.append(
                    f"**Anomaly:** {col} contains {neg_count:,} negative values."
                )

        # Detect statistical outliers
        mean = df[col].mean()
        std = df[col].std()

        if std > 0:
            outliers = ((df[col] < mean - n_std * std) |
                        (df[col] > mean + n_std * std)).sum()
            if 0 < outliers < len(df) * 0.1:
                pct = (outliers / len(df) * 100).round(1)
                insights.append(
                    f"**Outliers:** {col} has {outliers:,} extreme values ({pct}% beyond {n_std} standard deviations)."
                )

    return "\n".join(insights) if insights else "**No significant anomalies detected.**"


def analyze_date_trends(df):
    """
    Analyze temporal patterns when a datetime column is available.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    str
        Summary of trends based on date-related columns.
    """
    if df is None:
        return ""

    insights = []
    date_cols = [c for c in df.columns if "datetime" in str(df[c].dtype)]

    if date_cols:
        date_col = date_cols[0]

        date_range = df[date_col].max() - df[date_col].min()
        min_date = df[date_col].min().strftime("%Y-%m-%d")
        max_date = df[date_col].max().strftime("%Y-%m-%d")

        insights.append(f"**Date Range:** {min_date} to {max_date} ({date_range.days} days).")

        daily_counts = df.groupby(df[date_col].dt.date).size()

        busiest_day = daily_counts.idxmax()
        slowest_day = daily_counts.idxmin()

        insights.append(f"**Busiest Day:** {busiest_day} with {daily_counts.max():,} records.")
        insights.append(f"**Slowest Day:** {slowest_day} with {daily_counts.min():,} records.")

    return "\n".join(insights) if insights else ""


def generate_dataset_summary(df):
    """
    Generate general dataset summary statistics.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    str
        Summary of dataset size, memory usage, and column type distribution.
    """
    if df is None:
        return ""

    insights = []
    insights.append(f"**Dataset Size:** {len(df):,} rows, {len(df.columns)} columns.")

    memory_mb = df.memory_usage(deep=True).sum() / 1024 ** 2
    insights.append(f"**Memory Usage:** {memory_mb:.2f} MB.")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = [c for c in df.columns if "datetime" in str(df[c].dtype)]

    insights.append(
        f"**Column Types:** {len(numeric_cols)} numeric, "
        f"{len(cat_cols)} categorical, {len(date_cols)} datetime."
    )

    return "\n".join(insights)


def generate_all_insights(df):
    """
    Produce a comprehensive insight summary including:
    - top and bottom performers
    - missing value patterns
    - anomaly detection
    - temporal trends
    - dataset-level summary

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    tuple
        (top_performers_df, bottom_performers_df, insights_text)
    """
    if df is None:
        return None, None, "Upload a dataset to begin."

    insights_sections = []

    # Determine candidate numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Treat low-cardinality numeric columns as categorical
    for col in numeric_cols[:]:
        if df[col].nunique() < 100 and col not in cat_cols:
            cat_cols.append(col)

    # Identify value column
    value_col = None
    numeric_only = numeric_cols

    for col in numeric_only:
        if any(keyword in col.lower() for keyword in [
            "quantity", "amount", "sales", "revenue",
            "price", "total", "weekly", "monthly",
            "cost", "profit", "value"
        ]):
            value_col = col
            break

    if value_col is None and numeric_only:
        value_col = numeric_only[0]

    # Identify grouping column
    group_col = None
    for col in cat_cols:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in [
            "country", "product", "category", "customer",
            "description", "name", "store", "region",
            "city", "state", "department"
        ]):
            group_col = col
            break

    if group_col is None and cat_cols:
        group_col = cat_cols[0]

    top_df = None
    bottom_df = None

    if value_col and group_col and value_col != group_col:
        try:
            top_df, bottom_df = identify_top_bottom_performers(df, group_col, value_col, n=10)
            grouped = df.groupby(group_col)[value_col].sum().sort_values(ascending=False)
            insights_sections.append(
                f"**Top Performer:** {grouped.index[0]} with {grouped.iloc[0]:,.0f} total {value_col}."
            )
            insights_sections.append(
                f"**Bottom Performer:** {grouped.index[-1]} with {grouped.iloc[-1]:,.0f} total {value_col}."
            )
        except Exception:
            pass

    # Missing values
    insights_sections.append(detect_missing_values(df))

    # Anomalies
    insights_sections.append(detect_anomalies(df))

    # Date trends
    date_info = analyze_date_trends(df)
    if date_info:
        insights_sections.append(date_info)

    # Dataset summary
    insights_sections.append(generate_dataset_summary(df))

    return top_df, bottom_df, "\n\n".join(insights_sections)
