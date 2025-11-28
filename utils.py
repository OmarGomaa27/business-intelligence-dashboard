import pandas as pd


def get_filter_options(df):
    """
    Determine which columns are numeric, categorical, or datetime.
    Returns three lists:
    - numeric columns
    - categorical columns
    - date columns
    """
    if df is None or df.empty:
        return [], [], []

    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date = df.select_dtypes(include=["datetime64[ns]", "datetime64", "datetime"]).columns.tolist()

    # Detect string-typed datetime columns
    for col in df.columns:
        if "datetime" in str(df[col].dtype) and col not in date:
            date.append(col)

    return numeric, categorical, date


def apply_filters(df, num_filters, cat_filters, date_filters):
    """
    Apply numeric, categorical, and date filters to the DataFrame.
    Accepts three dictionaries:

    num_filters = { column_name: (min, max), ... }
    cat_filters = { column_name: [values], ... }
    date_filters = { column_name: (start_date, end_date), ... }

    Dates are converted safely using pandas.to_datetime.
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

import pandas as pd


def get_filter_options(df):
    """
    Determine which columns are numeric, categorical, or datetime.
    Returns three lists:
    - numeric columns
    - categorical columns
    - date columns
    """
    if df is None or df.empty:
        return [], [], []

    numeric = df.select_dtypes(include=["number"]).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date = df.select_dtypes(include=["datetime64[ns]", "datetime64", "datetime"]).columns.tolist()

    # Detect string-typed datetime columns
    for col in df.columns:
        if "datetime" in str(df[col].dtype) and col not in date:
            date.append(col)

    return numeric, categorical, date


def apply_filters(df, num_filters, cat_filters, date_filters):
    """
    Apply numeric, categorical, and date filters to the DataFrame.
    Accepts three dictionaries:

    num_filters = { column_name: (min, max), ... }
    cat_filters = { column_name: [values], ... }
    date_filters = { column_name: (start_date, end_date), ... }

    Dates are converted safely using pandas.to_datetime.
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
