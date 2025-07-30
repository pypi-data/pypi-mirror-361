import pandas as pd
from tabulate import tabulate
def get_detailed(df, config=None):
    """
    Generates a detailed summary of the DataFrame based on configuration.
    
    Parameters:
    - df: pandas DataFrame
    - config: dict, configuration loaded from YAML.
    
    Returns:
    - str: A formatted table with dataset information.
    """
    
    num_rows, num_cols = df.shape
    
    profiling_config = config.get('profiling', {}) if config else {}
    include_more_stats = profiling_config.get('include_more_stats', False)
    
    numeric, categorical, datetime, other = count_column_types(df)

    # Add a column types summary section
    col_types_info = [
        ["Number of Columns", num_cols],
        ["Numeric Columns", numeric],
        ["Categorical Columns", categorical],
        ["Datetime Columns", datetime],
        ["Other Column Types", other],
        ["Number of Rows", num_rows]
    ]
    
    from tabulate import tabulate
    summary_table = tabulate(col_types_info, headers=["Info", "Count"], tablefmt="rounded_outline")
    
    headers = ["Column Name", "Dtype", "Null", "Not Null", "Null %", "Unique Val"]
    if include_more_stats:
        headers.extend(["Mean", "Median", "Std Dev", "Skewness", "Kurtosis"])

    data = []
    null_counts = df.isnull().sum()
    total_counts = df.count()
    
    for col in df.columns:
        dtype = df[col].dtype
        null = null_counts.get(col, 0)
        not_null = total_counts.get(col, 0)
        null_percent = f"{null / num_rows:.2%}" if num_rows > 0 else "0.00%"
        unique_values = df[col].nunique()
        
        row_data = [col, dtype, null, not_null, null_percent, unique_values]
        
        if include_more_stats:
            if pd.api.types.is_numeric_dtype(dtype):
                mean_val = round(df[col].mean(), 2)
                median_val = round(df[col].median(), 2)
                std_dev = round(df[col].std(), 2)
                skew_val = round(df[col].skew(), 2)
                kurt_val = round(df[col].kurtosis(), 2)
                row_data.extend([mean_val, median_val, std_dev, skew_val, kurt_val])
            else:
                row_data.extend(["-", "-", "-", "-", "-"])

        data.append(row_data)
    
    details_table = tabulate(data, headers=headers, tablefmt="rounded_outline")
    
    return f"{summary_table}\n\n{details_table}"



def count_column_types(df):
    numeric = sum(pd.api.types.is_numeric_dtype(dtype) for dtype in df.dtypes)
    categorical = sum(pd.api.types.is_object_dtype(dtype) for dtype in df.dtypes)
    datetime = sum(pd.api.types.is_datetime64_any_dtype(dtype) for dtype in df.dtypes)
    other = df.shape[1] - (numeric + categorical + datetime)
    return numeric, categorical, datetime, other
