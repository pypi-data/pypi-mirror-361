import yaml
import os
import pandas as pd
from .detailed_info import get_detailed
from .column_cleaning import clean_column_names
from .data_cleaning import clean_missing_data

def run_pipeline(df, config_path='config.yaml', export_csv_path=None, export_report_path=None):
    """
    Executes a complete data analysis and cleaning pipeline based on a YAML configuration file.
    
    Parameters:
    - df: pandas DataFrame
    - config_path: str, path to the YAML configuration file.
    - export_csv_path: str or None, path to save cleaned dataframe as CSV.
    - export_report_path: str or None, path to save the report text file.
    
    Returns:
    - cleaned_df: The fully processed pandas DataFrame.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    print("--- Datacmp Pipeline Started ---")
    print("\n[STEP 1] Generating Initial Data Report...")
    initial_report = get_detailed(df, config)
    print(initial_report)
    
    # ------------------ Cleaning Phase ------------------
    print("\n[STEP 2] Cleaning Column Names...")
    df = clean_column_names(df)
    print("Column names cleaned.")
    
    print("\n[STEP 3] Handling Missing Data & Outliers...")
    df_cleaned, cleaning_report = clean_missing_data(df, config)
    for action in cleaning_report.get('actions', []):
        print(f"   • {action}")
    
    # ------------------ Final Report Phase ------------------
    print("\n[STEP 4] Generating Final Data Report...")
    final_report = get_detailed(df_cleaned, config)
    print(final_report)
    
    print("\n--- Datacmp Pipeline Finished ---")
    
    # Export CSV if path provided
    if export_csv_path:
        df_cleaned.to_csv(export_csv_path, index=False)
        print(f"Cleaned data saved to: {export_csv_path}")
    
    # Export full report if path provided
    if export_report_path:
        with open(export_report_path, 'w') as report_file:
            report_file.write("--- Initial Data Report ---\n\n")
            report_file.write(initial_report + "\n\n")
            
            report_file.write("--- Cleaning Actions ---\n")
            for action in cleaning_report.get('actions', []):
                report_file.write(f"• {action}\n")
            report_file.write("\n")
            
            report_file.write("--- Final Data Report ---\n\n")
            report_file.write(final_report + "\n")
        
        print(f"Report saved to: {export_report_path}")
    
    return df_cleaned


if __name__ == "__main__":
    pass  # For real usage, user will import and call run_pipeline with their df and paths
