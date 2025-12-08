import pandas as pd
import numpy as np


def load_data(file):
    """
    Load a CSV or Excel file and return a cleaned pandas DataFrame.
    Performs basic type inference and sanitization after loading.
    
    Parameters
    ----------
    file : file-like object
        The uploaded file. Must be CSV or Excel format.

    Returns
    -------
    DataFrame
        A cleaned pandas DataFrame with inferred data types.

    Raises
    ------
    ValueError
        If the file format is unsupported or cannot be loaded.
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
    Infer appropriate data types for DataFrame columns.
    
    This function:
    - Converts object columns containing date-like values to datetime.
    - Converts object columns containing numeric-like values to numeric.
    - Applies conversions only when at least half of the column values are valid.

    Parameters
    ----------
    df : DataFrame
        Input dataset.

    Returns
    -------
    DataFrame
        Dataset with improved data types.
    """
    df = df.copy()

    for col in df.columns:
        col_lower = col.lower()

        date_indicators = ["date", "time", "created", "updated", "timestamp"]
        likely_date = any(ind in col_lower for ind in date_indicators)

        # Preserve existing datetime columns
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

        # Attempt datetime conversion for likely date columns
        if likely_date and df[col].dtype == "object":
            try:
                converted = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
                if converted.notna().mean() > 0.5:
                    df[col] = converted
                    continue
            except Exception:
                pass

        # Attempt numeric conversion
        if df[col].dtype == "object" and not likely_date:
            try:
                converted = pd.to_numeric(df[col], errors="coerce")
                if converted.notna().mean() > 0.5:
                    df[col] = converted
            except Exception:
                pass

    return df


def get_basic_info(df):
    """
    Return basic dataset information including shape, columns, and data types.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    dict
        Dictionary containing dataset shape, column names, and data types.
    """
    return {
        "Shape": list(df.shape),
        "Columns": list(df.columns),
        "Data Types": df.dtypes.astype(str).to_dict(),
    }


def preview_data(df, n=5):
    """
    Return the first n rows of the dataset.

    Parameters
    ----------
    df : DataFrame
    n : int
        Number of rows to preview.

    Returns
    -------
    DataFrame
        First n rows of the dataset.
    """
    return df.head(n)


def numeric_summary(df):
    """
    Generate descriptive statistics for numeric columns.
    
    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
        Summary statistics, or an empty DataFrame if no numeric columns are present.
    """
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.describe().T


def categorical_summary(df):
    """
    Generate a summary for categorical columns.

    For each column, reports:
    - Number of unique values
    - Most frequent value

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    dict
        Summary statistics for categorical columns.
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
    """
    Return the number of missing values for each column.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    dict
        Missing value counts per column.
    """
    return {col: int(count) for col, count in df.isnull().sum().items()}


def correlation_matrix(df):
    """
    Compute the correlation matrix for numeric columns.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
        Correlation matrix, or an empty DataFrame if no numeric columns exist.
    """
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.corr()
