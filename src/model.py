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
        feature_df.set_index(0, inplace=True)
        feature_df.columns = c.RETURNED_FEATURES

        # rename the columns to match what the current classifier expects
        feature_df.rename(columns=c.FEATURE_MAP, inplace=True)

        # reorder the columns to match what the current classifier expects
        feature_df = feature_df[c.USE_FEATURES]

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
        input_df.to_csv(output_path, index=False)
