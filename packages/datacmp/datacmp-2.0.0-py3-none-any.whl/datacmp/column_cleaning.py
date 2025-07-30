# datacmp/column_cleaning.py
import logging
import pandas as pd

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def clean_column_names(df):

    """
    Cleans and standardizes the column names of a Pandas DataFrame by:
        - Stripping leading and trailing whitespace
        - Converting all names to lowercase
        - Replacing spaces with underscores

    Returns:
        pd.DataFrame: A new DataFrame with cleaned and standardized column names.
    """

    df = df.copy()
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    cleaned_columns = df.columns.tolist()

    for orig, cleaned in zip(original_columns, cleaned_columns):
        if orig != cleaned:
            logger.info(f"Renamed column: '{orig}' → '{cleaned}'")

    return df
