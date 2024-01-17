# built-in
import pickle

# external

# local
import preprocess as pre
from utilities import constants as c


def make_inference(input_path, output_path):
    # read the input csv into a dataframe
    input_df = pre.read_df(input_path)

    # drop appropriate columns (commented out for now because the current model uses all fields in the combined data)
    # df = input_df.drop(columns=c.DROP_COLUMNS)

    # TODO: calculate feature vectors
    # again, not doing this right now because the current model uses fields in the combined data

    # TODO: classifier
    model = pickle.load(open(c.MODEL_PATH, 'rb'))
    predictions = model.predict(input_df.drop(columns=['UUID']))
    conf_levels = model.predict_proba(input_df.drop(columns=['UUID']))
    max_conf_levels = conf_levels.max(axis=1)

    # TODO: add the prediction to input data
    input_df["Prediction"] = predictions
    input_df["Confidence"] = max_conf_levels

    print(input_df.head(5))
    print(input_df.tail(5))

    # # output the augmented dataframe as a csv
    # input_df.to_csv(output_path, index=False)
