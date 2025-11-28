import pandas as pd
import numpy as np


def load_data(file):
    """
    Load a CSV or Excel file and return a cleaned pandas DataFrame.
    Performs type inference and sanitization after loading.
    """
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel.")
        
        df = clean_and_infer_types(df)
        return df

    except Exception as e:
        raise ValueError(f"Error loading file: {str(e)}")


def clean_and_infer_types(df):
    """
    Attempts to infer appropriate data types for columns.
    - Converts date-like columns to datetime if appropriate.
    - Converts numeric-like object columns to numeric.
    - Only applies conversions when at least 50% of values are valid.
    """
    df = df.copy()

    for col in df.columns:
        col_lower = col.lower()

        # Detect columns likely to contain dates
        date_indicators = ['date', 'time', 'created', 'updated', 'timestamp']
        likely_date = any(ind in col_lower for ind in date_indicators)

        # Keep existing datetime columns
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

        # Attempt datetime conversion if column is likely a date
        if likely_date and df[col].dtype == "object":
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().mean() > 0.5:
                    df[col] = converted
                    continue
            except Exception:
                pass

        # Attempt numeric conversion for object columns
        if df[col].dtype == "object":
            try:
                converted = pd.to_numeric(df[col], errors="coerce")
                if converted.notna().mean() > 0.5:
                    df[col] = converted
            except Exception:
                pass

    return df


def get_basic_info(df):
    """Return dataset shape, column names, and data types."""
    return {
        "Shape": list(df.shape),
        "Columns": list(df.columns),
        "Data Types": df.dtypes.astype(str).to_dict(),
    }


def preview_data(df, n=5):
    """Return the first n rows of the dataset."""
    return df.head(n)


def numeric_summary(df):
    """
    Produce descriptive statistics for all numeric columns.
    Returns an empty DataFrame if no numeric columns exist.
    """
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.describe().T


def categorical_summary(df):
    """
    Produce a summary for all categorical columns, including:
    - number of unique values
    - most frequent value
    """
    cat_df = df.select_dtypes(include=["object", "category"])
    summary = {}

    for col in cat_df.columns:
        mode_vals = cat_df[col].mode()
        summary[col] = {
            "Unique Values": int(cat_df[col].nunique()),
            "Most Frequent": mode_vals.iloc[0] if len(mode_vals) > 0 else None,
        }

    return summary


def missing_values_report(df):
    """Return the number of missing values per column."""
    return {col: int(count) for col, count in df.isnull().sum().items()}


def correlation_matrix(df):
    """
    Return the correlation matrix for numeric columns.
    Returns an empty DataFrame if no numeric columns exist.
    """
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.corr()
