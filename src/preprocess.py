import pandas as pd


def read_df(file_path):
    df = pd.read_csv(file_path)
    return df


def drop_columns(df, columns):
    return df.drop(columns=columns)
