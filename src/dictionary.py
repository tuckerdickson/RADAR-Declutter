import pandas as pd
import schedule

from radar_track import RADARTrack


class Dictionary:
    def __init__(self):
        self.dictionary = dict()
        self.first_half = True
        schedule.every(30).seconds.do(self.clear_stale_feature_vectors)

    def __len__(self):
        """
        Return number of feature vectors in the dictionary.
        """
        return len(self.dictionary)

    def add_plot(self, uuid, plot):
        """
        Function called whenever a new track update enters the system.
        If the UUID associated with the track hasn't been encountered yet, 
        create a new feature vector object using the update values and 
        add it to the dictionary. Otherwise, update the feature vector entries 
        with the new update values. 
        Afterwards, if the cleanup procedure is queued, run the cleanup 
        procedure to remove any tracks which haven't been updated in over
        a minute.
        """
        # if the uuid is already in the dictionary, add it to the collection
        vals = {
            "speed": plot["Speed"],
            "azimuth": plot["AZ"],
            "elevation": plot["EL"],
            "range": plot["Range"],
            "lat": plot["Position_lat_"],
            "lon": plot["Position_lon_"],
            "msl_alt": plot["Position_altMSL_"],
        }
        if uuid in self.dictionary:
            self.dictionary[uuid].calculate_new_values(vals)

        # if the uuid is not in the dictionary, create a new entry for it
        else:
            new_track = RADARTrack(init_vals=vals)
            self.dictionary[uuid] = new_track
            # TODO: if the maximum number of entries is exceeded, remove the oldest entry
        schedule.run_pending()

    def get_features(self):
        """
        Function to return all feature vectors in the dictionary as a DataFrame.
        """
        res_list = []
        for uuid in self.dictionary.keys():
            res_list.append(self.get_feature_vector(uuid))

        return pd.DataFrame(res_list)

    def get_feature_vector(self, uuid):
        """
        Function to return a feature vector entry from the dictionary.
        """
        # raise an exception if the UUID isn't in the dictionary
        if uuid not in self.dictionary:
            raise Exception(
                f"The following UUID was not found in the dictionary: {uuid}"
            )

        track_object = self.dictionary[uuid]
        fv = [uuid]
        fv.extend(track_object.get_feature_vector())

        return fv

    def clear_stale_feature_vectors(self):
        """
        Function run periodically to clear feature vector entries which haven't had a recent
        track update. 
        """
        # n = len(self) // 2
        stale_list = []
        if len(self) > 0:
            # Decide whether or not to check first or second half of dictionary 
            # depending on the iteration for a faster processing time
            # check_list = list(self.dictionary.items())[:n] if self.first_half else list(self.dictionary.items())[n:]
            for uuid, fv in self.dictionary.items():
                # Pop every feature vector which has had over a minute since its last update, stale
                if fv.past_stale_time():
                    stale_list.append(uuid)
            for uuid in stale_list:
                self.dictionary.pop(uuid)
            # Check next half of list on the next iteration
            # self.first_half = not self.first_half