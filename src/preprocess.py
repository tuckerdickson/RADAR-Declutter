import os
import pandas as pd


def read_df(file_path):
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        raise FileNotFoundError(f"Error: {file_path} not found")


def drop_columns(df, columns):
    return df.drop(columns=columns)
