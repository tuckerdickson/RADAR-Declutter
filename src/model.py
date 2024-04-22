import dictionary
import multiprocessing as mp
import numpy as np
import output
import pandas as pd
import pickle
import preprocess as pre
import tqdm

from pandas import DataFrame
from radar_track import RADARTrack
from sklearn import metrics, tree
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


def calculate_feature(group):
    """
    Calculates the features vectors for a given radar track.
    :param group: The radar track to calculate feature vectors for.
    :return: The feature vectors of the given radar track.
    """
    # separate the input DataFrame into name (the track's UUID) and group (the actual data).
    name, group = group

    # extract the important values from group
    vals = {
        "Speed": [group.iloc[0]["Speed"]],
        "AZ": [group.iloc[0]["AZ"]],
        "EL": [group.iloc[0]["EL"]],
        "Range": [group.iloc[0]["Range"]],
        "Position (lat)": [group.iloc[0]["Position (lat)"]],
        "Position (lon)": [group.iloc[0]["Position (lon)"]],
        "Position (alt MSL)": [group.iloc[0]["Position (alt MSL)"]]
    }
    length = len(group)

    # initialize a RADARTrack instance using the important values from above
    track = RADARTrack(uuid=name, init_vals=vals)

    # use the RADARTrack instance to calculate the object's feature vectors
    track.calculate_new_values(group.iloc[1:length])

    # get the feature vectors from the RADARTrack instance
    features = track.get_feature_vector()

    # append the ground-truth label
    features["Label"] = group.iloc[0]["Label"]

    # convert the returned feature vectors to a DataFrame
    features = {k: [v] for k, v in features.items()}  # pandas needs everything to have an index
    features = DataFrame.from_dict(features, orient='columns')

    return features


class Model:
    """
    This class represents the machine learning model used to make predictions about the type of object based on radar
    track information. It can be used to make predictions about the type of object, retrain the classification model,
    and evaluate the classification model.

    Attributes:
        model: The classification model used to make predictions.
        records: A "dictionary" of radar track records over time.
    """
    def __init__(self, path=None):
        """
        Initializer for Model class, initializes the classification model and record of previous radar updates.
        :param path: The path to load a pickled model from (if None, a new model will be initialized).
        """
        # if path is None, initialize a new model, otherwise load the model from path
        self.model = RandomForestClassifier(class_weight='balanced') if path is None else self.load_model(path)

        # initialize the dictionary (record of previous radar updates)
        self.records = dictionary.Dictionary()

    def save_model(self, filename):
        """
        Saves a classification model to a given file.
        :param filename: The path to save the model to.
        :return: None
        """
        pickle.dump(self.model, open(filename, 'wb'))

    def load_model(self, filename):
        """
        Loads a classification model from a given file.
        :param filename: The path to load the model from.
        :return: The loaded model (if loaded successfully) or None (if the file could not be loaded).
        """
        # try to load the model from its file
        try:
            self.model = pickle.load(open(filename, 'rb'))
            return self.model

        # if the file can't be found, print a message and return
        except FileNotFoundError:
            print(f"no model found at {filename}")
            return None

    def clear_model(self):
        """
        Re-initializes the model attribute as a new Random Forest Classifier.
        :return: None (re-initializes the model attribute instead).
        """
        self.model = RandomForestClassifier(class_weight='balanced')

    def train_model(self, data):
        """
        Trains a new Random Forest Classifier, given a training dataset as input.
        :param data: The dataset to train (and evaluate using a 70-30 split) the model on.
        :return: None (the trained model is saved to the model class attribute).
        """
        # clean the input data (drop unnecessary columns)
        data = pre.clean_df(data)

        # group the input data on UUID (i.e., separate out each of the tracks in the data)
        print("Generating feature vectors...")
        grouped = data.groupby("UUID")

        # stores the feature vectors for each object in the data, as they're calculated
        results = []

        # calculate the feature vectors for each track in the data (parallelized for speed)
        pool = mp.Pool(mp.cpu_count())
        for result in tqdm.tqdm(pool.imap_unordered(calculate_feature, [[name, group] for name, group in grouped]),
                                total=len(grouped)):
            results.append(result)

        # turn the feature vector list back into a DataFrame
        features = pd.concat(results)

        # drop nan values from the data
        data = features.reset_index()
        data.dropna(how='any', inplace=True)

        # Create an un-labeled dataset, X, and the corresponding label vector, y
        print("\n\nTraining Model...")
        X = data.drop("Label", axis=1)
        y = data["Label"]
        X.drop("UUID", axis=1, inplace=True)

        # Perform 70-30 split test on given data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        # clone the current model and re-fit the clone
        rf = clone(self.model)
        rf.fit(X_train, y_train)

        # generate predictions and confidence pairs with the fitted model using the testing dataset
        rf_pred = rf.predict(X_test)
        rf_confidence_pair = rf.predict_proba(X_test)

        # calculate and display the accuracy of the predictions
        accuracy = metrics.accuracy_score(y_test, rf_pred)
        print(f'accuracy = {100 * accuracy}')

        # calculate and display the f1 score of the predictions
        accuracy = metrics.f1_score(y_test, rf_pred)
        print(f'f1 score = {100 * accuracy}')

        # predict_proba() returns a confidence for each class; the conf. of the prediction is the maximum of the two
        rf_confidence = [max(pair) for pair in rf_confidence_pair]

        # compute and display the average confidence level of the predictions
        avg_rf_confidence = np.mean(rf_confidence)
        print(f'average confidence level: {avg_rf_confidence}')

        # compute and display the median confidence level of the predictions
        med_rf_confidence = np.median(rf_confidence)
        print(f'median confidence level: {med_rf_confidence}')

        # display a classification report of for the fitted model.
        print("\nClassification Report")
        print(classification_report(y_test, rf_pred, target_names=["Bird", "Drone"], digits=4))

        # re-train the model attribute with the full dataset
        self.model.fit(X, y)

    def test_model(self, data, output_path):
        """
        Tests a trained model on a given dataset and writes the results to a csv file.
        :param data: The data to test the trained model on.
        :param output_path: The path to the output csv file.
        :return: None
        """
        # clean the input data (drop unnecessary columns)
        data = pre.clean_df(data)

        # group the input data on UUID (i.e., separate out each of the tracks in the data)
        print("Generating feature vectors...")
        grouped = data.groupby("UUID")

        # stores the feature vectors for each object in the data, as they're calculated
        results = []

        # calculate the feature vectors for each track in the data (parallelized for speed)
        pool = mp.Pool(mp.cpu_count())
        for result in tqdm.tqdm(pool.imap_unordered(calculate_feature, [[name, group] for name, group in grouped]),
                                total=len(grouped)):
            results.append(result)

        # turn the feature vector list back into a DataFrame
        features = pd.concat(results)

        # drop nan values from the data
        data = features.reset_index()
        data.dropna(how='any', inplace=True)

        # Create an un-labeled dataset, X, and the corresponding label vector, y
        print("\n\nTraining Model...")
        X = data.drop("Label", axis=1)
        y = data["Label"]
        X.drop("UUID", axis=1, inplace=True)

        # generate predictions and confidence pairs with the fitted model using the testing dataset
        rf_pred = self.model.predict(X)
        rf_confidence_pair = self.model.predict_proba(X)

        # calculate and display the accuracy of the predictions
        accuracy = metrics.accuracy_score(y, rf_pred)
        print(f'accuracy = {100 * accuracy}')

        # calculate and display the f1 score of the predictions
        accuracy = metrics.f1_score(y, rf_pred)
        print(f'f1 score = {100 * accuracy}')

        # predict_proba() returns a confidence for each class; the conf. of the prediction is the maximum of the two
        rf_confidence = [max(pair) for pair in rf_confidence_pair]

        # calculate and display the average confidence of the predictions
        avg_rf_confidence = np.mean(rf_confidence)
        print(f'\naverage confidence level: {avg_rf_confidence}')

        # calculate and display the median confidence of the predictions
        med_rf_confidence = np.median(rf_confidence)
        print(f'median confidence level: {med_rf_confidence}')

        # display a classification report of for the fitted model.
        print("\nClassification Report")
        print(classification_report(y, rf_pred, target_names=["Bird", "Drone"], digits=4))

        # add the predictions to the input data and write to csv at output_path
        X["Label"] = rf_pred
        X.to_csv(output_path, index=False)

    def make_inference(self, input_df, output_path=None, demo=False):
        """
        Predicts whether the radar tracks in a DataFrame (input_df) represent a bird or a drone.
        :param input_df: The DataFrame containing the radar tracks to classify.
        :param output_path: The path to save the resulting DataFrame (which includes predictions) to.
        :param demo: True if running the demonstration, False otherwise.
        :return: If running the demonstration, a DataFrame with the predictions, otherwise None.
        """
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

        # otherwise, output the augmented dataframe as a protobuff file
        # currently disabled to avoid errors in working branches
        else:
            print(f"{input_df}\n")
            # output.dataframe_to_protomessage(input_df, output_path)
