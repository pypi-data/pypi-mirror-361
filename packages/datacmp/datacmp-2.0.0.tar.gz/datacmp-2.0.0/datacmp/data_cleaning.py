import pandas as pd

def _handle_outliers_iqr(series, config):
    """
    Internal function to detect and handle outliers using the IQR method.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    multiplier = config.get('iqr_multiplier', 1.5)
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    action = config.get('action', 'cap')
    
    if action == 'cap':
        series = series.clip(lower=lower_bound, upper=upper_bound)
        return series, series[~series.between(lower_bound, upper_bound)].count()
    
    elif action == 'remove':
        initial_count = series.shape[0]
        cleaned_series = series[series.between(lower_bound, upper_bound)]
        removed_count = initial_count - cleaned_series.shape[0]
        return cleaned_series, removed_count
    
    return series, 0 # Return original series and 0 count if no action

def clean_missing_data(df, config=None):
    """
    Cleans missing values and handles outliers based on a config dictionary.
    
    Parameters:
    - df: pandas DataFrame
    - config: dict, configuration loaded from YAML.
    
    Returns:
    - cleaned_df: pandas DataFrame
    - report: dict, summary of actions taken
    """
    df = df.copy()
    report = {'actions': []}
    
    cleaning_config = config.get('cleaning', {}) if config else {}
    
    if config and config.get('drop_duplicates', False):
        initial_rows = len(df)
        df.drop_duplicates(inplace=True)
        dropped_rows = initial_rows - len(df)
        report['actions'].append(f"Dropped {dropped_rows} duplicate rows.")
    
    # Type conversion logic could go here, for now it's in the loop
    
    missing_info = df.isnull().mean()
    
    # Process each column based on config
    for col in df.columns:
        missing_ratio = missing_info[col]
        
        if missing_ratio > cleaning_config.get('threshold_drop', 0.4):
            df.drop(columns=[col], inplace=True)
            report['actions'].append(f"Dropped column '{col}' due to {missing_ratio:.2%} missing values.")
            continue
        
        if missing_ratio > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                strategy = cleaning_config.get('fill_strategy', {}).get('numeric', 'mean')
                if strategy == 'mean':
                    fill_value = df[col].mean()
                elif strategy == 'median':
                    fill_value = df[col].median()
                elif strategy == 'mode':
                    fill_value = df[col].mode()[0] if not df[col].mode().empty else 0
                else: # Default to mean
                    fill_value = df[col].mean()
                df[col] = df[col].fillna(fill_value)
                report['actions'].append(f"Filled numeric column '{col}' with {strategy}.")
            else:
                strategy = cleaning_config.get('fill_strategy', {}).get('categorical', 'mode')
                if strategy == 'mode':
                    mode_value = df[col].mode()
                    if not mode_value.empty:
                        df[col] = df[col].fillna(mode_value[0])
                    else:
                        df[col] = df[col].fillna('Unknown')
                else: # Default to 'Unknown'
                    df[col] = df[col].fillna('Unknown')
                report['actions'].append(f"Filled categorical column '{col}' with '{strategy}'.")

    # Handle outliers based on config
    outlier_config = cleaning_config.get('outlier_handling', {})
    if outlier_config.get('enabled', False) and outlier_config.get('method') == 'iqr':
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                initial_series = df[col].copy()
                df[col], handled_count = _handle_outliers_iqr(initial_series, outlier_config)
                if handled_count > 0:
                    report['actions'].append(f"Handled {handled_count} outliers in '{col}' by '{outlier_config['action']}'.")

    return df, report