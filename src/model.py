import pickle

import dictionary
import preprocess as pre

from utilities import constants as c

from sklearn.ensemble import RandomForestClassifier


class Model:

    def __init__(self):
        self.model = RandomForestClassifier()  # the actual model
        self.records = dictionary.Dictionary()  # dictionary that stores historic radar data

    def save_model(self, filename):
        #save the model
        pickle.dump(self.model, open(filename, 'wb'))

    def load_model(self, filename):
        # try to load the model from its file
        try:
            model = pickle.load(open(filename, 'rb'))
            return model

        # if the file can't be found, print a message and return
        # TODO: figure out a better way to handle this error
        except FileNotFoundError:
            print(f"no model found at {filename}")
            return None
        
    def train_model(self, data):
        print("Not yet implemented")

    def make_inference(self, input_df, output_path):

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
