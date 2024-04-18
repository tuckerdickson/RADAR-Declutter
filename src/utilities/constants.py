DEMO_PLOT_X_LOWER = 38.904

DEMO_PLOT_X_UPPER = 38.910

DEMO_PLOT_Y_LOWER = -86.872

DEMO_PLOT_Y_UPPER = -86.860

DROP_COLUMNS = ['Name', 'Create Time', 'User Edit Time', 'Type', 'Associated UUID', 'Note', 'Source Name',
                'Source Class', 'Source LID', 'Combat ID', 'Object ID', 'Range To Contact', 'Bearing To Contact',
                'Creator', 'Editor', 'Origin Position (lat)', 'Origin Position (lon)', 'Origin Position (alt MSL)',
                '2525', 'Radar Cross Section', 'Closest Time', 'Course', 'Source ID', 'Closest Distance',
                'Deleted', 'Deleted Time', 'AIS MMSI', 'AIS IMO', 'AIS Call Sign', 'AIS Ship Type',
                'AIS Destination', 'AIS ETA', 'Fused', 'Fused Tracks']

# mar14_SM.sav
#
#
# AVG_RCS INCLUDED IN FEATURE MAP
# NOT A FEATURE IN MAR14
# FEATURE FOR APR17 MODEL
#
FEATURE_MAP = {'avg_speed': 'Average Speed',
               'std_speed': 'Stan. Dev. Speed',
               'avg_heading': 'Average Heading',
               'std_heading': 'Stan. Dev. Heading',
               'avg_curvature': 'Average Curvature',
               'avg_rcs': 'Average Radar Cross Section',
               'mav_factor': 'Maneuverability',
               'm1_range': 'M1 Range',
               'm1_azimuth': 'M1 AZ',
               'm1_elevation': 'M1 EL',
               'm1_speed': 'M1 Speed',
               'm1_heading': 'M1 Heading',
               'm2_range': 'M2 Range',
               'm2_azimuth': 'M2 AZ',
               'm2_elevation': 'M2 EL',
               'm2_speed': 'M2 Speed',
               'm2_heading': 'M2 Heading',
               }

USE_FEATURES = ['Average Speed', 'Stan. Dev. Speed',
                'Stan. Dev. Heading', 'Average Curvature', 
                'Average Radar Cross Section', 'Maneuverability',
                'M1 Range', 'M1 AZ', 'M1 EL', 'M1 Speed', 'M1 Heading',
                'M2 Range', 'M2 AZ', 'M2 EL', 'M2 Speed', 'M2 Heading',
                ]

MODEL_PATH = '../models/bird_drone_20.sav'
