import numpy as np


class RADARTrack:
    def __init__(self, init_vals, df=None):
        if df != None:
            # implement training feature creation
            pass
        else:
            # TODO figure out ideal initial values
            self.avg_speed = init_vals["speed"]
            self.std_speed = 0
            self.prev_speed = init_vals["speed"]
            self.avg_heading = 0
            self.std_heading = 0
            self.prev_heading = 0
            self.prev_az = init_vals["azimuth"]
            self.prev_el = init_vals["elevation"]
            self.prev_range = init_vals["range"]
            self.prev_delta_x = 0
            self.prev_delta_y = 0
            self.prev_lat = init_vals["lat"]
            self.prev_lon = init_vals["lon"]
            self.mav_score = 0
            self.n = 1
            self.smoothness_vectors = dict()
            list_of_smoothness_features = {
                "speed": init_vals["speed"],
                "heading": 0,
                "azimuth": init_vals["azimuth"],
                "elevation": init_vals["elevation"],
                "range": init_vals["range"],
            }
            self.create_smoothness_vectors(list_of_smoothness_features)

    def __len__(self):
        return self.n

    def calculate_new_values(self, value_updates):
        self.n += 1
        cur_speed = value_updates["speed"]
        cur_az = value_updates["azimuth"]
        cur_el = value_updates["elevation"]
        cur_range = value_updates["range"]
        cur_lat = value_updates["lat"]
        cur_lon = value_updates["lon"]
        cur_avg_speed = self.calculate_avg(self.avg_speed, cur_speed, self.n)
        cur_std_speed = self.calculate_std(
            self.std_speed, cur_avg_speed, self.avg_speed, cur_speed, self.n
        )
        cur_heading = self.calculate_heading(cur_lat, cur_lon)
        cur_avg_heading = self.calculate_avg(self.avg_heading, cur_heading, self.n)
        if self.n > 2:
            cur_std_heading = self.calculate_std(
                self.std_heading, cur_avg_heading, self.avg_heading, cur_heading, self.n
            )
        else:
            cur_std_heading = 0
        self.calculate_smoothnesses(
            {
                "speed": cur_speed,
                "heading": cur_heading,
                "azimuth": cur_az,
                "elevation": cur_el,
                "range": cur_range,
            }
        )
        self.update_prevs(
            cur_speed, cur_heading, cur_az, cur_el, cur_range, cur_lat, cur_lon
        )
        self.avg_speed = cur_avg_speed
        self.std_speed = cur_std_speed
        self.avg_heading = cur_avg_heading
        self.std_heading = cur_std_heading
        if self.n != 2:
            self.mav_score = self.calculate_mav_factor(cur_avg_speed, cur_std_heading)

    def get_feature_vector(self):
        vec = [
            self.avg_speed,
            self.std_speed,
            self.avg_heading,
            self.std_heading,
            self.mav_score,
        ]
        for smoothness_vec in self.smoothness_vectors.values():
            vec.append(smoothness_vec.prev_m1)
            vec.append(smoothness_vec.prev_m2)
        return vec

    def create_smoothness_vectors(self, list_of_smoothness_features):
        for feature, init_val in list_of_smoothness_features.items():
            self.smoothness_vectors[feature] = SmoothnessVector(init_val)

    def calculate_smoothnesses(self, value_updates):
        for feature, vector in self.smoothness_vectors.items():
            vector.calculate_new_values(value_updates[feature], self.n)

    def calculate_avg(self, prev_avg, cur_val, n):
        return ((n - 1) * prev_avg + cur_val) / n

    # TODO fix division by zero error
    def calculate_std(self, prev_std, cur_avg, prev_avg, cur_val, n):
        prev_var = prev_std**2
        numerator = (n - 2) * prev_var + (cur_val - cur_avg) * (cur_val - prev_avg)
        return np.sqrt(numerator / (n - 1))

    def calculate_mav_factor(self, cur_avg_speed, cur_std_heading):
        return cur_avg_speed / cur_std_heading

    def calculate_heading(self, cur_lat, cur_lon):
        return np.arctan2(self.prev_lon - cur_lon, self.prev_lat - cur_lat)

    def calculate_osc_factor(self, heading):
        ###
        ### TODO readup on what osc is
        ### NOT FINAL
        ###
        theta = heading.shift(1) - heading

        O = theta.copy(deep=True)
        O[theta > 0.5] = 1
        O[theta < -0.5] = -1
        O[abs(theta) <= 0.5] = 0

        w = O.copy(deep=True)
        osc_number = 1
        for i in range(1, O.shape[0] - 1):
            w[i] = osc_number

    def update_prevs(
        self,
        cur_speed,
        cur_heading,
        cur_az,
        cur_el,
        cur_range,
        cur_lat,
        cur_lon,
    ):
        self.prev_speed = cur_speed
        self.prev_heading = cur_heading
        self.prev_az = cur_az
        self.prev_el = cur_el
        self.prev_range = cur_range
        self.cur_lat = cur_lat
        self.prev_lon = cur_lon


class SmoothnessVector:
    def __init__(self, init_val):
        # TODO figure out ideal initial values
        self.prev_q = init_val
        self.prev_c = init_val
        self.prev_m1 = 0
        self.prev_m2 = 0
        self.prev_val = init_val

    def calculate_new_values(self, cur_val, n):
        cur_q = self.calculate_q(cur_val, n)
        cur_c = self.calculate_c(cur_val, n)
        cur_m1 = self.calculate_smoothness_factor_m1(cur_q, cur_val, n)
        cur_m2 = self.calculate_smoothness_factor_m2(cur_m1, cur_c)
        self.update_prevs(cur_q, cur_c, cur_m1, cur_m2, cur_val)

    def calculate_q(self, cur_val, n):
        return (1 / n) * ((n - 1) * self.prev_q + (cur_val - self.prev_val))

    def calculate_smoothness_factor_m1(self, cur_q, cur_val, n):
        return (1 / n) * (
            self.prev_m1 * (n - 1) + (cur_val - self.prev_val - cur_q) ** 2
        )

    def calculate_c(self, cur_val, n):
        return (1 / n) * (self.prev_c * (n - 1) + np.abs(cur_val - self.prev_val))

    def calculate_smoothness_factor_m2(self, cur_m1, cur_c):
        if cur_c != 0:
            ret_val = cur_m1 / cur_c
        else:
            ret_val = 0
        return ret_val

    def update_prevs(self, cur_q, cur_c, cur_m1, cur_m2, cur_val):
        self.prev_q = cur_q
        self.prev_c = cur_c
        self.prev_m1 = cur_m1
        self.prev_m2 = cur_m2
        self.prev_val = cur_val
