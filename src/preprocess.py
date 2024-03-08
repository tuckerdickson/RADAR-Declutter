import os

import pandas as pd

from utilities import constants as c


def read_df(file_path):
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        raise FileNotFoundError(f"Error: {file_path} not found")


def clean_df(df):
    return df.drop(columns=c.DROP_COLUMNS)
