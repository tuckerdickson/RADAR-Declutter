import pandas as pd

from radar_track import RADARTrack


class Dictionary:
    def __init__(self):
        self.dictionary = dict()

    def add_plot(self, uuid, plot):
        # if the uuid is already in the dictionary, add it to the collection
        vals = {
            "speed": plot["Speed"],
            "azimuth": plot["AZ"],
            "elevation": plot["EL"],
            "range": plot["Range"],
            "lat": plot["Position_lat_"],
            "lon": plot["Position_lon_"],
        }
        if uuid in self.dictionary:
            self.dictionary[uuid].calculate_new_values(vals)

        # if the uuid is not in the dictionary, create a new entry for it
        else:
            new_track = RADARTrack(init_vals=vals)
            self.dictionary[uuid] = new_track
            # TODO: if the maximum number of entries is exceeded, remove the oldest entry

    def get_features(self):
        res_list = []
        for uuid in self.dictionary.keys():
            res_list.append(self.get_feature_vector(uuid))

        return pd.DataFrame(res_list)

    def get_feature_vector(self, uuid):
        # raise an exception if the UUID isn't in the dictionary
        if uuid not in self.dictionary:
            raise Exception(
                f"The following UUID was not found in the dictionary: {uuid}"
            )

        track_object = self.dictionary[uuid]
        fv = [uuid]
        fv.extend(track_object.get_feature_vector())

        return fv
