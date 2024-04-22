import os
import pandas as pd

from utilities import constants as c


def read_df(file_path):
    """
    Reads a csv file into a Pandas DataFrame.
    :param file_path: The path to the csv file to be read.
    :return: A Pandas DataFrame if file_path exists, otherwise None.
    """
    # check if there is a file at file_path
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        return df

    # if there is no file, raise an error
    else:
        raise FileNotFoundError(f"Error: {file_path} not found")


def clean_df(df):
    """
    Drops unnecessary columns (specified in constants.py) from the DataFrame passed in.
    :param df: The Pandas DataFrame to be cleaned.
    :return: The cleaned Pandas DataFrame.
    """
    return df.drop(columns=c.DROP_COLUMNS, errors='ignore')
