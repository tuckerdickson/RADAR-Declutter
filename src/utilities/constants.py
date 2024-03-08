CLASSIFIER_FEATURES = ['avg_speed', 'std_speed', 'std_heading', 'mav_factor']

DEMO_PLOT_X_LOWER = 38.901

DEMO_PLOT_X_UPPER = 38.902

DEMO_PLOT_Y_LOWER = -86.865

DEMO_PLOT_Y_UPPER = -86.864

DROP_COLUMNS = ['Name', 'Create Time', 'User Edit Time', 'Type', 'Associated UUID', 'Note', 'Source Name',
                'Source Class', 'Source LID', 'Combat ID', 'Object ID', 'Range To Contact', 'Bearing To Contact',
                'Creator', 'Editor', 'Origin Position (lat)', 'Origin Position (lon)', 'Origin Position (alt MSL)',
                '2525', 'Radar Cross Section', 'Closest Time', 'Course', 'Source ID', 'Closest Distance',
                'Deleted', 'Deleted Time', 'AIS MMSI', 'AIS IMO', 'AIS Call Sign', 'AIS Ship Type',
                'AIS Destination', 'AIS ETA', 'Fused', 'Fused Tracks']

FEATURE_NAMES = ['avg_speed', 'std_speed', 'avg_heading', 'std_heading', 'mav_factor', 'avg_curvature',
                 'm1_speed', 'm2_speed', 'm1_heading', 'm2_heading', 'm1_azimuth', 'm2_azimuth',
                 'm1_elevation', 'm2_elevation', 'm1_range', 'm2_range']

MODEL_PATH = '../models/feb9_fv.sav'
