DEMO_PLOT_X_LOWER = 39.99       # x-axis lower limit for the track plot in the demo
DEMO_PLOT_X_UPPER = 40.01       # x-axis upper limit for the track plot in the demo
DEMO_PLOT_Y_LOWER = -90.01      # y-axis lower limit for the track plot in the demo
DEMO_PLOT_Y_UPPER = -89.99      # y-axis upper limit for the track plot in the demo

# the columns to drop from a DataFrame when training or making a prediction
DROP_COLUMNS = ['Name', 'Create Time', 'User Edit Time', 'Type', 'Associated UUID', 'Note', 'Source Name',
                'Source Class', 'Source LID', 'Combat ID', 'Object ID', 'Range To Contact', 'Bearing To Contact',
                'Creator', 'Editor', 'Origin Position (lat)', 'Origin Position (lon)', 'Origin Position (alt MSL)',
                '2525', 'Closest Time', 'Course', 'Source ID', 'Closest Distance',
                'Deleted', 'Deleted Time', 'AIS MMSI', 'AIS IMO', 'AIS Call Sign', 'AIS Ship Type',
                'AIS Destination', 'AIS ETA', 'Fused', 'Fused Tracks']

MODEL_PATH = '../models/apr17_full.sav'
