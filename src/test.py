import argparse
import glob
import datetime;
import os
import uuid

import pandas as pd
from model import Model

from utilities import constants as c

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Test Model',
        description='Tests a model on the provided data')

    parser.add_argument('-m', '--modelFile', type=str, default='../models/feb25_fv.sav', help="Model filename")
    parser.add_argument('-s', '--resultsFile', type=str, default='test.csv', help="Results filename")
    parser.add_argument('-t', '--testingFiles', type=str, default=[], nargs='+', help="Tests on all files listed")
    parser.add_argument('-d', '--testingDirectories', type=str, default=['../data/test'], nargs='+', help="Tests on all files in these directories")
    parser.add_argument('-l', '--trackLength', type=int, default=20, help="Maximum length before track splitting")
    parser.add_argument('-n', '--numRows', type=int, default=None, help="Limits the number of rows taken from the input during the test")

    args = parser.parse_args()

    # Parse paths
    files = set()

    for dir in args.testingDirectories:
        files |= set(glob.glob(dir + '/*' + '.csv', recursive=True))

    for file in args.testingFiles:
        files.add(file)

    print("Loading Files:")
    print("----------------------------------------")
    print(files)
    print("----------------------------------------\n")

    mod = Model()

    data = []
    for file in files:
        data.append(pd.read_csv(file, low_memory=False))

    if(len(data) > 0):
        testing = pd.concat(data)

    if(args.numRows):
        testing = testing[:args.numRows]

    num_unique_uuids = testing['UUID'].nunique()
    print("Number of unique UUIDs:", num_unique_uuids)


    print("Splitting tracks into length " + str(args.trackLength))
    grouped = testing.groupby("UUID")

    dataframes = []
    for group_name, group_df in grouped:
        if len(group_df) > args.trackLength:
            count = 0
            
            l = len(group_df)
            for idx, row in group_df.iterrows():
                if count % args.trackLength == 0 and l-count>=args.trackLength:
                    new_id = str(uuid.uuid4())

                group_df.at[idx, "UUID"] = new_id
                count += 1
        dataframes.append(group_df)

    testing = pd.concat(dataframes)

    grouped = testing.groupby("Combat ID")

    dataframes = {}
    for name, group in grouped:
        dataframes[name] = group.reset_index(drop=True)

    labeled_data = pd.DataFrame()

    if("HOSTILE" in grouped.groups):
        dataframes["HOSTILE"]["Label"] = 1
        labeled_data = pd.concat([labeled_data, dataframes["HOSTILE"]], ignore_index=True)
        print("HOSTILE updates: ", len(dataframes["HOSTILE"]))
    if("UNKNOWN_THREAT" in grouped.groups):
        dataframes["UNKNOWN_THREAT"]["Label"] = 0
        labeled_data = pd.concat([labeled_data, dataframes["UNKNOWN_THREAT"]], ignore_index=True)
        print("UNKNOWN_THREAT updates: ", len(dataframes["UNKNOWN_THREAT"]))

    print("")

    if(mod.load_model(args.modelFile)):
        mod.test_model(labeled_data, args.resultsFile)
        print("\nSaved results to " + args.resultsFile)