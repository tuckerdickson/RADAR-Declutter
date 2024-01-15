# built-in
import sys

# external

# local
import evaluate
import inference
import train

if __name__ == "__main__":
    # the first command-line argument specifies the action to perform (train, evalute, or make inference)
    command = sys.argv[1]

    if command == "evaluate":
        print("evaluate")

    elif command == "inference":
        inference.make_inference(sys.argv[2], sys.argv[3])

    elif command == "train":
        print("train")

    else:
        print("Invalid command.")