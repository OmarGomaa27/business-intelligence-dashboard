import pandas as pd

def load_data(file):
    """Load CSV or Excel file and return pandas DataFrame."""
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
            df = pd.read_excel(file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel.")
        return df
    except Exception as e:
        raise ValueError(f"Error loading file: {str(e)}")


def get_basic_info(df):
    """Return shape, columns, and data types."""
    return {
        "Shape": df.shape,
        "Columns": list(df.columns),
        "Data Types": df.dtypes.astype(str).to_dict()
    }


def preview_data(df, n=5):
    """Return first n rows."""
    return df.head(n)


def numeric_summary(df):
    """Return summary statistics for numeric columns."""
    numeric_df = df.select_dtypes(include=['int64', 'float64'])
    return numeric_df.describe().T


def categorical_summary(df):
    """Return categorical columns with unique counts and top values."""
    cat_df = df.select_dtypes(include=['object'])
    summary = {}
    for col in cat_df.columns:
        summary[col] = {
            "Unique Values": cat_df[col].nunique(),
            "Most Frequent": cat_df[col].mode()[0] if not cat_df[col].mode().empty else None
        }
    return summary


def missing_values_report(df):
    """Return missing values per column."""
    return df.isnull().sum().to_dict()


def correlation_matrix(df):
    """Return correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include=['int64', 'float64'])
    return numeric_df.corr()
