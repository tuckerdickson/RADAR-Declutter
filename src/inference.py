# standard library
import sys

# external

# local
import preprocess as pre
from utilities import constants as c


def main(input_path, output_path):
    # read the input csv into a dataframe
    df = pre.read_df(input_path)

    # drop unneeded columns
    df = pre.drop_columns(df, c.DROP_COLUMNS)



    # output the augmented dataframe as a csv
    # df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
