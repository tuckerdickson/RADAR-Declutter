import model
import pandas as pd

from utilities import constants as c
from utilities import demo
from utilities.input import receiver

# start of flow of execution, this is what's called from command line
if __name__ == "__main__":
    # load the machine learning model (specified by constants.MODEL_PATH)
    model = model.Model(path=c.MODEL_PATH)

    # used to store and parse command line commands
    command = [""]

    # keep the program going until the user requests to quit
    while len(command) == 0 or command[0] != "quit":
        # get input from command line and split for parsing
        command = input("> ").split()

        # if the command is inference (i.e., make predictions), use the model to make predictions
        if command[0] == "inference":
            # for this command, the user must provide paths to input and output files
            try:
                model.make_inference(pd.read_csv(command[1]), command[2])
            except IndexError:
                print("error: inference command must include input file and output file.")

        elif command[0] == "listen":
            receiver = receiver.Receiver(model, "localhost", 12345)
            receiver.begin_listening()

        # run the demonstration simulation
        elif command[0] == "demo":
            # for this command, the user must provide paths to input and output directories
            try:
                d = demo.Demo(command[1], command[2], model)
            except IndexError:
                print("error: demo command must include input file and output directory.")
                continue

            d.run_tests()

        # retrain the model
        elif command[0] == "train":
            print("train")

        # provide help to the user
        elif command[0] == "help":
            print("help")

        # any other command (other than quit) is invalid
        elif command[0] != "quit":
            print("invalid command")
