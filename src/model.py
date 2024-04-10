import dictionary
import output
import pickle
import preprocess as pre

from sklearn.ensemble import RandomForestClassifier


class Model:
    def __init__(self, path=None):
        self.model = RandomForestClassifier() if path is None else self.load_model(path)
        self.records = dictionary.Dictionary()

    def save_model(self, filename):
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
        print(input_df)
        # input_df.to_csv(output_path, index=False)

        # otherwise, output the augmented dataframe as a protobuff file
        # currently disabled to avoid errors in working branches
        # output.dataframe_to_protomessage(input_df, output_path)
