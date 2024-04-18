import pickle
import dictionary
import output
import pickle
import preprocess as pre
from radar_track import RADARTrack

import numpy as np
import pandas as pd
from pandas import DataFrame

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics, tree
from sklearn.base import clone
from sklearn.metrics import classification_report

import multiprocessing as mp
import tqdm


def calculate_feature(group):
    name, group = group
    vals = {
        "Speed": [group.iloc[0]["Speed"]],
        "AZ": [group.iloc[0]["AZ"]],
        "EL": [group.iloc[0]["EL"]],
        "Range": [group.iloc[0]["Range"]],
        "Position (lat)": [group.iloc[0]["Position (lat)"]],
        "Position (lon)": [group.iloc[0]["Position (lon)"]],
        "Position (alt MSL)": [group.iloc[0]["Position (alt MSL)"]]
    }
    l = len(group)

    track = RADARTrack(uuid=name, init_vals=vals)
    track.calculate_new_values(group.iloc[1:l])

    features = track.get_feature_vector()
    features["Label"] = group.iloc[0]["Label"]
    features = {k: [v] for k, v in features.items()}  # pandas needs everything to have an index
    features = DataFrame.from_dict(features, orient='columns')

    return features


class Model:

    def __init__(self, path=None):
        self.model = RandomForestClassifier(class_weight='balanced') if path is None else self.load_model(
            path)  # the actual model
        self.records = dictionary.Dictionary()  # dictionary that stores historic radar data

    def save_model(self, filename):
        pickle.dump(self.model, open(filename, 'wb'))

    def load_model(self, filename):
        # try to load the model from its file
        try:
            self.model = pickle.load(open(filename, 'rb'))
            return self.model

        # if the file can't be found, print a message and return
        # TODO: figure out a better way to handle this error
        except FileNotFoundError:
            print(f"no model found at {filename}")
            return None

    def clear_model(self):
        self.model = RandomForestClassifier(class_weight='balanced')

    def train_model(self, data):

        data = pre.clean_df(data)

        print("Generating feature vectors...")
        grouped = data.groupby("UUID")
        dataframes = []
        i = 0

        pool = mp.Pool(mp.cpu_count())

        results = []
        for result in tqdm.tqdm(pool.imap_unordered(calculate_feature, [[name, group] for name, group in grouped]),
                                total=len(grouped)):
            results.append(result)
        features = pd.concat(results)

        data = features.reset_index()
        data.dropna(how='any', inplace=True)

        print("\n\nTraining Model...")
        X = data.drop("Label", axis=1)
        y = data["Label"]
        X.drop("UUID", axis=1, inplace=True)

        # Perform 70-30 split test on given data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        rf = clone(self.model)
        rf.fit(X_train, y_train)

        rf_pred = rf.predict(X_test)
        rf_confidence_pair = rf.predict_proba(X_test)

        accuracy = metrics.accuracy_score(y_test, rf_pred)
        print(f'accuracy = {100 * accuracy}')

        accuracy = metrics.f1_score(y_test, rf_pred)
        print(f'f1 score = {100 * accuracy}')

        rf_confidence = [max(pair) for pair in rf_confidence_pair]
        avg_rf_confidence = np.mean(rf_confidence)
        med_rf_confidence = np.median(rf_confidence)
        print(f'average confidence level: {avg_rf_confidence}')
        print(f'median confidence level: {med_rf_confidence}')

        print("\nClassification Report")
        print(classification_report(y_test, rf_pred, target_names=["Bird", "Drone"], digits=4))

        # Train self with full dataset
        self.model.fit(X, y)

    def test_model(self, data, output_path):

        data = pre.clean_df(data)

        print("Generating feature vectors...")
        grouped = data.groupby("UUID")
        dataframes = []
        i = 0

        pool = mp.Pool(mp.cpu_count())

        results = []
        for result in tqdm.tqdm(pool.imap_unordered(calculate_feature, [[name, group] for name, group in grouped]),
                                total=len(grouped)):
            results.append(result)
        features = pd.concat(results)

        data = features.reset_index()
        data.dropna(how='any', inplace=True)

        print("\n\nTraining Model...")
        X = data.drop("Label", axis=1)
        y = data["Label"]
        X.drop("UUID", axis=1, inplace=True)

        rf_pred = self.model.predict(X)
        rf_confidence_pair = self.model.predict_proba(X)

        accuracy = metrics.accuracy_score(y, rf_pred)
        print(f'accuracy = {100 * accuracy}')

        accuracy = metrics.f1_score(y, rf_pred)
        print(f'f1 score = {100 * accuracy}')

        rf_confidence = [max(pair) for pair in rf_confidence_pair]
        avg_rf_confidence = np.mean(rf_confidence)
        med_rf_confidence = np.median(rf_confidence)
        print(f'\naverage confidence level: {avg_rf_confidence}')
        print(f'median confidence level: {med_rf_confidence}')

        print("\nClassification Report")
        print(classification_report(y, rf_pred, target_names=["Bird", "Drone"], digits=4))

        X["Label"] = rf_pred
        X.to_csv(output_path, index=False)

    def make_inference(self, input_df, output_path=None, demo=False):

        # "clean" the data by dropping unnecessary columns, etc...
        df = input_df.copy()
        df = pre.clean_df(df)

        # add plots to dictionary
        curr_uuids = []
        for idx, row in df.iterrows():
            uuid = row["UUID"]
            self.records.add_plot(uuid, row)
            curr_uuids.append(uuid)

        # calculate feature vectors for the objects present
        feature_df = self.records.get_features(curr_uuids)

        # set the column names for the returned feature df
        feature_df.set_index('UUID', inplace=True)

        # make predictions with classifier
        predictions = self.model.predict(feature_df)
        conf_levels = self.model.predict_proba(feature_df)
        max_conf_levels = conf_levels.max(axis=1)

        # add the prediction to input data
        input_df["Prediction"] = predictions
        input_df["Confidence"] = max_conf_levels

        # if running demonstration, return the data so that results can be displayed
        if demo:
            return input_df

        # otherwise, output the augmented dataframe as a csv
        print(f"{input_df}\n")
        # input_df.to_csv(output_path, index=False)

        # otherwise, output the augmented dataframe as a protobuff file
        # currently disabled to avoid errors in working branches
        # output.dataframe_to_protomessage(input_df, output_path)
