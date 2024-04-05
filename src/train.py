import argparse
import glob
import datetime;
import os

import pandas as pd
from model import Model

from utilities import constants as c

parser = argparse.ArgumentParser(
    prog='Train Model',
    description='Trains a model on the provided data, then saves it to a given filename.')

parser.add_argument('-s', '--saveFile', type=str, default='../models/' + datetime.datetime.now().strftime("%B %d, %Y, %H-%m-%S"), help="Savefile name")
parser.add_argument('-t', '--trainingFiles', type=str, default=[], nargs='+', help="Trains on all files listed")
parser.add_argument('-d', '--trainingDirectories', type=str, default=['../data/train'], nargs='+', help="Trains on all files in these directories")

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

#training.dropna(axis="index", inplace=True)

grouped = training.groupby("Combat ID")

dataframes = {}
for name, group in grouped:
    dataframes[name] = group.reset_index(drop=True)

dataframes["HOSTILE"]["Label"] = 1
dataframes["UNKNOWN_THREAT"]["Label"] = 0

print("HOSTILE tracks: ", len(dataframes["HOSTILE"]))
print("UNKNOWN_THREAT tracks: ", len(dataframes["UNKNOWN_THREAT"]))

labeled_data = pd.concat([dataframes["HOSTILE"], dataframes["UNKNOWN_THREAT"]], ignore_index=True)

mod.train_model(labeled_data)
mod.save_model(args.saveFile)

print("Saved model to " + args.saveFile)