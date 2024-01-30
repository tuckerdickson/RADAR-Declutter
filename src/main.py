# built-in
import sys

# external

# local
import dictionary
import inference
import model
from utilities import constants as c

if __name__ == "__main__":
    model = model.Model(path=c.MODEL_PATH)
    dictionary = dictionary.Dictionary()
    command = [""]

    # keep looping until the user requests to exit
    while command[0] != "quit":
        # split the input for parsing
        command = input("> ").split()

        if command[0] == "evaluate":
            print("evaluate")

        elif command[0] == "inference":
            try:
                model.make_inference(command[1], command[2])
            except IndexError:
                print("error: inference command must include input file and output file.")

        elif command[0] == "train":
            print("train")

        elif command[0] == "quit":
            pass

        else:
            print("invalid command")