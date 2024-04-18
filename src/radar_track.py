import numpy as np
import time
import pandas as pd


class RADARTrack:
    def __init__(self, uuid, init_vals):
        self.n = 1
        self.last_update = time.time()
        self.updates = pd.DataFrame(init_vals)
        self.uuid = uuid
        self.feature_vector = {
            'UUID': uuid,
            'avg_speed': init_vals['Speed'][0],
            'std_speed': 0,
            'std_heading': 0,
            'mav_factor': 0,
            'avg_curvature': 0,
            'avg_rcs': init_vals['Radar Cross Section'][0],
            "m1_range": 0,
            "m1_az": 0,
            "m1_el": 0,
            "m1_speed": 0,
            "m1_heading": 0,
            "m2_range": 0,
            "m2_az": 0,
            "m2_el": 0,
            "m2_speed": 0,
            "m2_heading": 0,
        }

    def __len__(self):
        return self.n

    def add_update(self, value_updates):
        self.updates = pd.concat([self.updates, pd.DataFrame(value_updates)], ignore_index=True)
        self.n += len(value_updates)
        self.last_update = time.time()
        
    def past_stale_time(self):
        dif = time.time() - self.last_update
        return dif > 90

    def get_feature_vector(self):
        return self.feature_vector

    def calculate_average_curvature(self, df):
        # Calculate the differences for Position (lat), Position (lon), and Position (alt MSL)
        lat_diff = df["Position (lat)"].diff(-1)
        lon_diff = df["Position (lon)"].diff(-1)
    
        # Calculate difference between first time step and second 
        a = np.sqrt(lat_diff ** 2 + lon_diff ** 2)

        # Calculate difference between first time step and third 
        lat_diff_2 = df["Position (lat)"].diff(-2)
        lon_diff_2 = df["Position (lon)"].diff(-2)
       
        b = np.sqrt(lat_diff_2 ** 2 + lon_diff_2 ** 2)
    
        # Calculate difference between second time step and third 
        lat_diff_1_2 = lat_diff.shift(-1).dropna()
        lon_diff_1_2 = lon_diff.shift(-1).dropna()
        c = np.sqrt(lat_diff_1_2 ** 2 + lon_diff_1_2 ** 2)
        
        # Calculate curvature
        with np.errstate(invalid="ignore"):
            numerator = a ** 2 - b ** 2 - c ** 2
            denominator = 2 * b * c + 1e-6
            # Arccos is throwing errors when it seems like it shouldn't
            curvature = np.arccos(numerator / denominator)
    
        # Calculate the average curvature
        average_curvature = curvature.mean()
    
        return average_curvature
        
    def calculate_m1(self, df, field):
        diff = df[field].diff(1)
        q = np.sum(diff) / len(df)
        m1 = np.sum((diff - q)**2)/len(df)
        return m1
        
    def calculate_m2(self, df,field):
        diff = df[field].diff(1)
        q = np.sum(diff) / len(df)
        m1 = np.sum((diff - q)**2) / len(df)
        c = np.sum(np.abs(diff)) / len(df)
        c += 1e-6
        m2 = m1/c
        return m2
    
    def calculate_new_values(self, value_updates):
        self.add_update(value_updates)

        self.feature_vector['avg_speed'] = np.mean(self.updates['Speed'])
        self.feature_vector['std_speed'] = np.std(self.updates['Speed'], ddof=1) # ddof=1 is to make std an unbiased estimator of the population
        heading = np.arctan2((self.updates["Position (lat)"].diff(-1)), 
                             (self.updates["Position (lon)"].diff(-1)))
        self.feature_vector['std_heading'] = np.std(heading, ddof=1)
        self.feature_vector['avg_curvature'] = self.calculate_average_curvature(self.updates)
        self.feature_vector['avg_rcs'] = np.mean(self.updates['Radar Cross Section'])
        self.feature_vector['mav_factor'] = self.feature_vector['avg_speed']/(self.feature_vector['std_heading'] + 1e-6)

        sm_df = self.updates[['Speed', 'Range', 'AZ', 'EL']]
        sm_df = sm_df.assign(Heading=heading)
        for name,field in [('speed','Speed'), ('range','Range'), ('az','AZ'), ('el','EL'), ('heading','Heading')]:
            self.feature_vector['m1_' + name] = self.calculate_m1(sm_df, field)
            self.feature_vector['m2_' + name] = self.calculate_m2(sm_df, field)
