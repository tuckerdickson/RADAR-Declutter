import argparse
import glob
import datetime
import os

import pandas as pd
from model import Model

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
    files |= set(glob.glob(dir + '/*' + '.csv'))

for file in args.trainingFiles:
    files.add(file)

print(files)

mod = Model()

data = []
for file in files:
    data.append(pd.read_csv(file))

if(len(data) > 0):
    training = pd.concat(data)

mod.train_model(training)
mod.save_model(args.saveFile)

print("Saved model to " + args.saveFile)