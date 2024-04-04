import argparse
import glob
import datetime;
import os

import pandas as pd
from model import Model

from utilities import constants as c

parser = argparse.ArgumentParser(
    prog='Test Model',
    description='Tests a model on the provided data')

parser.add_argument('-m', '--modelFile', type=str, default='../models/feb25_fv.sav', help="Model filename")
parser.add_argument('-s', '--resultsFile', type=str, default='test.csv', help="Results filename")
parser.add_argument('-t', '--testingFiles', type=str, default=[], nargs='+', help="Tests on all files listed")
parser.add_argument('-d', '--testingDirectories', type=str, default=['../data/test'], nargs='+', help="Tests on all files in these directories")

args = parser.parse_args()

# Parse paths
files = set()

for dir in args.testingDirectories:
    files |= set(glob.glob(dir + '/*' + '.csv', recursive=True))

for file in args.testingFiles:
    files.add(file)

print(files)

mod = Model()

data = []
for file in files:
    data.append(pd.read_csv(file))

if(len(data) > 0):
    testing = pd.concat(data)

testing = testing.rename(columns=c.INPUT_MAP, errors='raise')

mod.load_model(args.modelFile)
mod.make_inference(testing, args.resultsFile)

print("Saved results to " + args.resultsFile)