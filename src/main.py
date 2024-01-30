# built-in
import sys

# external

# local
import evaluate
import inference
import train

if __name__ == "__main__":
    command = [""]

    # keep looping until the user requests to exit
    while command[0] != "quit":
        # split the input for parsing
        command = input("> ").split()

        if command[0] == "evaluate":
            print("evaluate")

        elif command[0] == "inference":
            print("inference")

        elif command[0] == "train":
            print("train")

        elif command[0] == "quit":
            pass

        else:
            print("invalid command")