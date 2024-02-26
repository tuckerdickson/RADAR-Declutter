import pickle

import dictionary
import preprocess as pre

from utilities import constants as c


class Model:
    def __init__(self, path):
        self.model_path = path  # the path to the model file
        self.model = self.load_model()  # the actual model
        self.records = dictionary.Dictionary()  # dictionary that stores historic radar data

    def load_model(self):
        # try to load the model from its file
        try:
            model = pickle.load(open(self.model_path, 'rb'))
            return model

        # if the file can't be found, print a message and return
        # TODO: figure out a better way to handle this error
        except FileNotFoundError:
            print(f"no model found at {self.model_path}")
            return None

    def make_inference(self, input_path, output_path):
        # try to read the input csv into a dataframe
        try:
            input_df = pre.read_df(input_path)

        # if the file can't be found, print the error and return
        # TODO: figure out a better way to handle this error
        except FileNotFoundError as error:
            print(error)
            return None

        # drop appropriate columns (commented for now because the current model uses all fields in the combined data)
        df = input_df.drop(columns=c.DROP_COLUMNS, errors='ignore')

        # add plots to dictionary
        for idx, row in df.iterrows():
            uuid = row["UUID"]
            self.records.add_plot(uuid, row)

        # calculate feature vectors
        feature_df = self.records.get_features()

        feature_df.set_index(0, inplace=True)
        feature_df.columns = c.FEATURE_NAMES

        print(feature_df)
        return

        # make predictions with classifier
        predictions = self.model.predict(feature_df)
        conf_levels = self.model.predict_proba(feature_df)
        max_conf_levels = conf_levels.max(axis=1)

        # add the prediction to input data
        input_df["Prediction"] = predictions
        input_df["Confidence"] = max_conf_levels

        # output the augmented dataframe as a csv
        input_df.to_csv(output_path, index=False)
