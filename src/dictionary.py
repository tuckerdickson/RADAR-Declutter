import pandas as pd

import preprocess as pre


class Dictionary:
    def __init__(self):
        self.dictionary = {}

    def add_plot(self, uuid, plot):
        # if the uuid is already in the dictionary, add it to the collection
        if uuid in self.dictionary:
            combined = pd.concat([self.dictionary[uuid], plot], axis=1, ignore_index=True)
            self.dictionary[uuid] = combined

        # if the uuid is not in the dictionary, create a new entry for it
        else:
            self.dictionary[uuid] = plot
            # TODO: if the maximum number of entries is exceeded, remove the oldest entry

    def get_features(self):
        res_list = []
        for uuid, df in self.dictionary.items():
            fv = self.get_feature_vector(uuid)
            res_list.append(fv)

        return pd.DataFrame(res_list)

    def get_feature_vector(self, uuid):
        # raise an exception if the UUID isn't in the dictionary
        if uuid not in self.dictionary:
            raise Exception(f"The following UUID was not found in the dictionary: {uuid}")

        df = self.dictionary[uuid]

        # TODO: calculate feature vectors
        avg_speed = pre.calculate_avg_speed(df)
        std_speed = pre.calculate_std_speed(df)
        std_heading = pre.calculate_std_heading(df)
        mav_factor = pre.calculate_mav_factor(df)

        feature_vector = [uuid, avg_speed, std_speed, std_heading, mav_factor]
        return feature_vector
