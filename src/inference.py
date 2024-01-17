# built-in

# external

# local
import preprocess as pre


def make_inference(input_path, output_path):
    # read the input csv into a dataframe
    input_df = pre.read_df(input_path)

    # drop appropriate columns

    # TODO: calculate feature vectors

    # TODO: classifier

    # TODO: add the prediction to input data
    input_df["Prediction"] = "Bird"
    input_df["Confidence"] = 100.0

    print(input_df.head(10))

    # output the augmented dataframe as a csv
    input_df.to_csv(output_path, index=False)
