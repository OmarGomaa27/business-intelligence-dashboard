"""
Utility functions for the Business Intelligence Dashboard.
Provides helper functions for filtering, data inspection,
and basic column validation.
"""

import pandas as pd


def get_filter_options(df):
    """
    Identify numeric, categorical, and datetime columns in a DataFrame.

    Parameters
    ----------
    df : DataFrame
        Input dataset.

    Returns
    -------
    tuple
        A tuple of three lists:
        - numeric_cols: columns with numeric data types
        - categorical_cols: columns with object or category data types
        - date_cols: columns with datetime data types
    """
    if df is None or df.empty:
        return [], [], []

    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date = df.select_dtypes(include=["datetime64[ns]", "datetime64", "datetime"]).columns.tolist()

    # Additional detection for datetime-like columns
    for col in df.columns:
        if "datetime" in str(df[col].dtype).lower() and col not in date:
            date.append(col)

    return numeric, categorical, date


def apply_filters(df, num_filters, cat_filters, date_filters):
    """
    Apply numeric, categorical, and date-based filters to a dataset.

    Parameters
    ----------
    df : DataFrame
        Dataset to filter.
    num_filters : dict
        Numeric filters of the form:
        { column_name: (min_value, max_value) }
    cat_filters : dict
        Categorical filters of the form:
        { column_name: [allowed_values] }
    date_filters : dict
        Date filters of the form:
        { column_name: (start_date, end_date) }

    Returns
    -------
    DataFrame
        Filtered dataset. Returns an empty DataFrame if input is invalid.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    filtered_df = df.copy()

    # Numeric filters
    for col, bounds in num_filters.items():
        if col in filtered_df.columns:
            min_val, max_val = bounds
            if min_val is not None:
                filtered_df = filtered_df[filtered_df[col] >= min_val]
            if max_val is not None:
                filtered_df = filtered_df[filtered_df[col] <= max_val]

    # Categorical filters
    for col, selected_values in cat_filters.items():
        if col in filtered_df.columns and selected_values:
            filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

    # Date filters
    for col, drange in date_filters.items():
        if col in filtered_df.columns:
            start, end = drange

            if start:
                try:
                    start_dt = pd.to_datetime(start)
                    filtered_df = filtered_df[filtered_df[col] >= start_dt]
                except Exception:
                    pass

            if end:
                try:
                    end_dt = pd.to_datetime(end)
                    filtered_df = filtered_df[filtered_df[col] <= end_dt]
                except Exception:
                    pass

    return filtered_df


def validate_column_exists(df, column_name):
    """
    Check whether a column exists in the dataset.

    Parameters
    ----------
    df : DataFrame
    column_name : str
        Column name to validate.

    Returns
    -------
    bool
        True if the column exists; otherwise False.
    """
    if df is None or column_name is None:
        return False
    return column_name in df.columns


def get_column_info(df, column_name):
    """
    Retrieve metadata for a specific column.

    Parameters
    ----------
    df : DataFrame
    column_name : str
        Column to inspect.

    Returns
    -------
    dict or None
        Metadata including:
        - dtype: data type
        - null_count: number of missing values
        - unique_count: number of unique values
        - sample_values: up to five example values
        Returns None if the column does not exist.
    """
    if not validate_column_exists(df, column_name):
        return None

    col = df[column_name]

    return {
        "dtype": str(col.dtype),
        "null_count": int(col.isnull().sum()),
        "unique_count": int(col.nunique()),
        "sample_values": col.dropna().unique()[:5].tolist(),
    }


def safe_numeric_conversion(series, default=0):
    """
    Convert a pandas Series to numeric type, replacing invalid values.

    Parameters
    ----------
    series : Series
        Input series.
    default : int or float
        Replacement value for non-convertible entries.

    Returns
    -------
    Series
        Numeric series with fallback values applied.
    """
    try:
        return pd.to_numeric(series, errors="coerce").fillna(default)
    except Exception:
        return series


def format_number(value, decimals=2):
    """
    Format a number with thousand separators and a fixed number of decimals.

    Parameters
    ----------
    value : int or float
        Value to format.
    decimals : int
        Number of decimal places.

    Returns
    -------
    str
        Formatted number as a string.
    """
    try:
        if decimals == 0:
            return f"{int(value):,}"
        return f"{value:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)


def get_date_range(df, date_column):
    """
    Return the minimum and maximum values of a datetime column.

    Parameters
    ----------
    df : DataFrame
    date_column : str

    Returns
    -------
    tuple
        (min_date, max_date), or (None, None) if invalid.
    """
    if not validate_column_exists(df, date_column):
        return None, None

    try:
        col = pd.to_datetime(df[date_column])
        return col.min(), col.max()
    except Exception:
        return None, None
