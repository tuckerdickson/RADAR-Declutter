import pandas as pd

from radar_track import RADARTrack


class Dictionary:
    def __init__(self):
        self.dictionary = dict()

    def add_plot(self, uuid, plot):
        # if the uuid is already in the dictionary, add it to the collection
        vals = {
            "Speed": [plot["Speed"]],
            "AZ": [plot["AZ"]],
            "EL": [plot["EL"]],
            "Range": [plot["Range"]],
            "Position (lat)": [plot["Position (lat)"]],
            "Position (lon)": [plot["Position (lon)"]],
            "Position (alt MSL)": [plot["Position (alt MSL)"]]
        }
        if uuid in self.dictionary:
            self.dictionary[uuid].calculate_new_values(vals)

        # if the uuid is not in the dictionary, create a new entry for it
        else:
            new_track = RADARTrack(uuid=uuid, init_vals=vals)
            self.dictionary[uuid] = new_track

    def get_features(self, curr_uuids):
        res_list = []
        for uuid in curr_uuids:
            res_list.append(self.get_feature_vector(uuid))
        df = pd.DataFrame(res_list)
        df.fillna(0, inplace=True)
        #print(df)
        return df

    def get_feature_vector(self, uuid):
        # raise an exception if the UUID isn't in the dictionary
        if uuid not in self.dictionary:
            raise Exception(
                f"The following UUID was not found in the dictionary: {uuid}"
            )
            
        return self.dictionary[uuid].get_feature_vector()
