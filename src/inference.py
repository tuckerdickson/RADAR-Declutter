import sys
import pandas as pd


def main(input_path, output_path):
    df = read_df(input_path)
    df.to_csv(output_path, index=False)


def read_df(file_path):
    df = pd.read_csv(file_path)
    return df


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
