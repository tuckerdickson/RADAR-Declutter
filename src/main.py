import argparse
import model
import os.path
import pandas as pd

from utilities import constants as c
from utilities import demo
from utilities.input import receiver


def directory_exists(path):
    """
    Checks if the path passed in is an existing directory.
    :param path: The path to be checked.
    :return: True if the path exists and is a directory, False otherwise.
    """
    return os.path.exists(path) and os.path.isdir(path)


def file_exists(path):
    """
    Checks if the path passed in is an existing file.
    :param path: The path to be checked.
    :return: True if the path exists and is a file, False otherwise.
    """
    return os.path.exists(path) and os.path.isfile(path)


def validate_args(args, parser):
    """
    Validates the command line arguments passed to the program.
    :param args: The command line arguments passed to the program.
    :param parser: An argparse parser instance, used to parse the command line arguments.
    :return: None (an error will be thrown if an invalid argument is found).
    """
    # checks for demonstration mode
    if args.mode == "demo":
        # both network host and port must be specified
        if not (args.host and args.port):
            parser.error("listen mode requires both host and port")

    # checks for listen (networked) mode
    elif args.mode == "listen":
        # both network host and port must be specified
        if not (args.host and args.port):
            parser.error("listen mode requires both host and port")

    # checks for inference (csv) mode
    elif args.mode == "inference":
        # both input and output files must be specified
        if not (args.input and args.output):
            parser.error("inference mode requires both input and output files")

        # both input and output files must exist (and be files)
        if not (file_exists(args.input) and file_exists(args.output)):
            parser.error("input or output file does not exist or is not accessible")


def execute_args(args):
    """
    Executes the proper functions, as specified by the (parsed) command line arguments.
    :param args: The parsed command line arguments.
    :return: None (program flow redirects to the desired function for the duration of the program's execution).
    """
    # define the classifier model (path specified in constants.py)
    classifier = model.Model(path=c.MODEL_PATH)

    # if the operation mode is demo, begin running the demo
    if args.mode == "demo":
        d = demo.NetworkDemo(classifier)
        listener = receiver.Receiver(classifier, args.host, args.port, demo=d)
        listener.begin_listening()

    # if the operation mode is listen, begin listening for messages
    elif args.mode == "listen":
        listener = receiver.Receiver(classifier, args.host, args.port)
        listener.begin_listening()

    # if the operation mode is inference, pass the input data through the classifier
    elif args.mode == "inference":
        classifier.make_inference(pd.read_csv(args.input), args.output)


def main(argv=None):
    """
    Main entry point of the program, creates an argument parser, parses the command line arguments, and then executes
    the appropriate function based on the arguments.
    :param argv: The parsed command line arguments passed to the program.
    :return: None (program flow redirects to the desired function for the duration of the program's execution).
    """
    # define the argument parser
    parser = argparse.ArgumentParser(
        prog="Radar Declutter",
        description="""Runs the Radar Declutter program in various different 
                    modes of operation: demo, listen, and inference."""
    )

    # mode of operation argument (either demo, listen, or inference), always required
    parser.add_argument(
        "mode",
        choices=['demo', 'listen', 'inference'],
        help="mode of operation"
    )

    # network host argument, required for LISTEN and DEMO modes
    parser.add_argument("-ho", "--host",
                        type=str,
                        help="network host (required for 'listen' and 'demo' modes)"
                        )

    # network port argument, required for LISTEN and DEMO modes
    parser.add_argument("-p", "--port",
                        type=int,
                        help="network port (required for 'listen' and 'demo' modes)"
                        )

    # input csv file argument, only required for INFERENCE mode
    parser.add_argument("-i", "--input",
                        type=str,
                        help="input file (required for 'inference' mode)"
                        )

    # output csv file argument, only required for INFERENCE mode
    parser.add_argument("-o", "--output",
                        type=str,
                        help="output file (required for 'inference' mode)"
                        )

    # parse the arguments
    args = parser.parse_args(argv)

    # ensure the args are valid
    validate_args(args, parser)

    # execute the appropriate function based on the arguments
    execute_args(args)


# start of flow of execution, this is what's called from command line
if __name__ == "__main__":
    exit(main())
