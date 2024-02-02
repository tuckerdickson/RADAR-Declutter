import pickle

import dictionary
import preprocess as pre


class Model:
    def __init__(self, path):
        self.model_path = path
        self.model = self.load_model()
        self.records = dictionary.Dictionary()

    def load_model(self):
        try:
            model = pickle.load(open(self.model_path, 'rb'))
        except FileNotFoundError:
            print(f"no model found at {self.model_path}")
            return None

        return model

    def make_inference(self, input_path, output_path):
        # try to read the input csv into a dataframe
        try:
            input_df = pre.read_df(input_path)
        except FileNotFoundError as error:
            print(error)
            return None

        # drop appropriate columns (commented for now because the current model uses all fields in the combined data)
        # df = input_df.drop(columns=c.DROP_COLUMNS)

        # add plots to dictionary
        for idx, row in input_df.iterrows():
            uuid = row["UUID"]
            self.records.add_plot(uuid, row)

        # TODO: calculate feature vectors
        feature_df = self.records.get_features()
        print(feature_df)

        # # TODO: classifier
        # predictions = self.model.predict(input_df.drop(columns=['UUID']))
        # conf_levels = self.model.predict_proba(input_df.drop(columns=['UUID']))
        # max_conf_levels = conf_levels.max(axis=1)
        #
        # # TODO: add the prediction to input data
        # input_df["Prediction"] = predictions
        # input_df["Confidence"] = max_conf_levels
        #
        # print(input_df.head(5))
        # print(input_df.tail(5))

        # # output the augmented dataframe as a csv
        # input_df.to_csv(output_path, index=False)
