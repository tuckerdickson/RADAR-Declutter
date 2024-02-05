import numpy as np


class FeatureVector:
    def __init__(self, df=None):
        if df != None:
            # implement training feature creation
            pass
        else:
            self.avg_speed = 0
            self.std_speed = 0
            self.prev_speed = 0
            self.avg_heading = 0
            self.std_heading = 0
            self.prev_heading = 0
            self.prev_az = 0
            self.prev_el = 0
            self.prev_range = 0
            self.prev_delta_x = 0
            self.prev_lat = 0
            self.prev_lon = 0
            self.prev_delta_y = 0
            self.mav_score = 0
            self.n = 0
            self.smoothness_vectors = dict()
            self.list_of_smoothness_features = [
                "speed",
                "heading",
                "azimuth",
                "elevation",
                "range",
            ]

    def calculate_new_values(
        self, cur_speed, cur_az, cur_el, cur_range, cur_lat, cur_lon
    ):
        cur_avg_speed = self.calculate_avg(self.avg_speed, cur_speed, self.n)
        cur_std_speed = self.calculate_std(
            self.std_speed, cur_avg_speed, self.avg_speed, cur_speed, self.n
        )
        cur_heading = self.calculate_heading(cur_lat, cur_lon)
        cur_avg_heading = self.calculate_avg(self.avg_heading, cur_heading, self.n)
        cur_std_heading = self.calculate_std(
            self.std_heading, cur_avg_heading, self.avg_heading, cur_heading, self.n
        )
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
        self.mav_score = self.calculate_mav_factor(cur_avg_speed, cur_std_heading)

    def return_vector(self):
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

    def create_smoothness_vectors(self):
        for feature in self.list_of_smoothness_features:
            self.smoothness_vectors[feature] = SmoothnessVector()

    def calculate_smoothnesses(self, value_updates):
        for feature, vector in self.smoothness_vectors.items():
            vector.calculate_new_values(value_updates[feature], self.n)

    def calculate_avg(self, prev_avg, cur_val, n):
        return ((n - 1) * prev_avg + cur_val) / n

    def calculate_std(self, prev_std, cur_avg, prev_avg, cur_val, n):
        prev_var = prev_std**2
        numerator = (n - 2) * prev_var + (cur_val - cur_avg) * (cur_val - prev_avg)
        return np.sqrt(numerator / n - 1)

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
    def __init__(self):
        self.prev_q = 0
        self.prev_c = 0
        self.prev_m1 = 0
        self.prev_m2 = 0
        self.prev_val = 0

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
        ) ** 2

    def calculate_c(self, cur_val, n):
        return (1 / n) * (self.prev_c * (n - 1) + np.abs(cur_val - self.prev_val))

    def calculate_smoothness_factor_m2(self, cur_m1, cur_c):
        return cur_m1 / cur_c

    def update_prevs(self, cur_q, cur_c, cur_m1, cur_m2, cur_val):
        self.prev_q = cur_q
        self.prev_c = cur_c
        self.prev_m1 = cur_m1
        self.prev_m2 = cur_m2
        self.prev_val = cur_val
