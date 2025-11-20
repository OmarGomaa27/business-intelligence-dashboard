import pandas as pd

def load_data(file):
    """Load CSV or Excel file and return pandas DataFrame."""
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file.name)
        elif file.name.endswith(".xlsx") or file.name.endswith(".xls"):
            df = pd.read_excel(file.name)
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
