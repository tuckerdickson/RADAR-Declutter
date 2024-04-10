import argparse
import glob
import datetime
import os
import uuid

import pandas as pd
from model import Model

from utilities import constants as c

parser = argparse.ArgumentParser(
    prog='Train Model',
    description='Trains a model on the provided data, then saves it to a given filename.')

parser.add_argument('-s', '--saveFile', type=str, default='../models/' + datetime.datetime.now().strftime("%B %d, %Y, %H-%m-%S"), help="Savefile name")
parser.add_argument('-t', '--trainingFiles', type=str, default=[], nargs='+', help="Trains on all files listed")
parser.add_argument('-d', '--trainingDirectories', type=str, default=['../data/train'], nargs='+', help="Trains on all files in these directories")
parser.add_argument('-l', '--trackLength', type=int, default=20, help="Maximum length before track splitting")
parser.add_argument('-n', '--numRows', type=int, default=None, help="Limits the number of rows taken from the input during the test")

args = parser.parse_args()

# Parse paths
files = set()

for dir in args.trainingDirectories:
    files |= set(glob.glob(dir + '/*' + '.csv', recursive=True))

for file in args.trainingFiles:
    files.add(file)

print("Loading Files:")
print("----------------------------------------")
print(files)
print("----------------------------------------\n")

mod = Model()

data = []
for file in files:
    data.append(pd.read_csv(file))

if(len(data) > 0):
    training = pd.concat(data)

if(args.numRows):
    training = training[:args.numRows]

num_unique_uuids = training['UUID'].nunique()
print("Number of unique UUIDs:", num_unique_uuids)


print("Splitting tracks into length " + str(args.trackLength))
grouped = training.groupby("UUID")

dataframes = []
for group_name, group_df in grouped:
    if len(group_df) > args.trackLength:
        count = 0
        
        for idx, row in group_df.iterrows():
            if count % args.trackLength == 0:
                new_id = str(uuid.uuid4())

            group_df.at[idx, "UUID"] = new_id
            count += 1
    dataframes.append(group_df)

training = pd.concat(dataframes)

num_unique_uuids = training['UUID'].nunique()
print("Number of unique UUIDs after track-splitting:", num_unique_uuids)

grouped = training.groupby("Combat ID")

dataframes = {}
for name, group in grouped:
    dataframes[name] = group.reset_index(drop=True)

labeled_data = pd.DataFrame()

if("HOSTILE" in grouped.groups):
    dataframes["HOSTILE"]["Label"] = 1
    labeled_data = pd.concat([labeled_data, dataframes["HOSTILE"]], ignore_index=True)
    print("HOSTILE updates: ", len(grouped.groups["HOSTILE"]))
if("UNKNOWN_THREAT" in grouped.groups):
    dataframes["UNKNOWN_THREAT"]["Label"] = 0
    labeled_data = pd.concat([labeled_data, dataframes["UNKNOWN_THREAT"]], ignore_index=True)
    print("UNKNOWN_THREAT updates: ", len(grouped.groups["UNKNOWN_THREAT"]))

print("")

mod.train_model(labeled_data)
mod.save_model(args.saveFile)

print("\nSaved model to " + args.saveFile)