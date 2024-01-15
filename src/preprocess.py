# built-in

# external
import pandas as pd

# local


def read_df(file_path):
    df = pd.read_csv(file_path)
    return df


def drop_columns(df, columns):
    return df.drop(columns=columns)
