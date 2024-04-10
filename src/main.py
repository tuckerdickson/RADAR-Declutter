import argparse
import model
import os.path
import pandas as pd

from utilities import constants as c
from utilities import demo
from utilities.input import receiver


def directory_exists(path):
    return os.path.exists(path) and os.path.isdir(path)


def file_exists(path):
    return os.path.exists(path) and os.path.isfile(path)


def validate_args(args, parser):
    # checks for demonstration mode
    if args.mode == "demo":
        # both input and output directories must be specified
        if not (args.indir and args.outdir):
            parser.error("demo mode requires both input and output directories")

        # both input and output directories must exist (and must be directories)
        if not (directory_exists(args.indir) and directory_exists(args.outdir)):
            parser.error("input or output directory does not exist or is not accessible")

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
    # define the classifier model (path specified in constants.py)
    classifier = model.Model(path=c.MODEL_PATH)

    # if operation mode is demo, run the demo
    if args.mode == "demo":
        d = demo.Demo(args.indir, args.outdir, classifier)
        d.run_tests()

    # if operation mode is listen, create a network connection and begin listening for messages
    elif args.mode == "listen":
        listener = receiver.Receiver(classifier, args.host, args.port)
        listener.begin_listening()

    # if the operation mode is inference, pass the data from input csv through classifier
    elif args.mode == "inference":
        classifier.make_inference(pd.read_csv(args.input), args.output)


def main(argv=None):
    # define the argument parser
    parser = argparse.ArgumentParser(
        prog="Radar Declutter",
        description="""Runs the Radar Declutter program in various different 
                    modes of operation: demo, listen, and inference."""
    )

    # mode of operation (either demo, listen, or inference), always required
    parser.add_argument(
        "mode",
        choices=['demo', 'listen', 'inference'],
        help="mode of operation"
    )

    # input directory, only required for DEMO mode
    parser.add_argument("-id", "--indir",
                        type=str,
                        help="input directory (required for 'demo' mode)"
                        )

    # output directory, only required for DEMO mode
    parser.add_argument("-od", "--outdir",
                        type=str,
                        help="out directory (required for 'demo' mode)"
                        )

    # network host, only required for LISTEN model
    parser.add_argument("-ho", "--host",
                        type=str,
                        help="network host (required for 'listen' mode)"
                        )

    # network port, only required for LISTEN model
    parser.add_argument("-p", "--port",
                        type=int,
                        help="network port (required for 'listen' mode)"
                        )

    # input csv file, only required for INFERENCE mode
    parser.add_argument("-i", "--input",
                        type=str,
                        help="input file (required for 'inference' mode)"
                        )

    # output csv file, only required for INFERENCE mode
    parser.add_argument("-o", "--output",
                        type=str,
                        help="output file (required for 'inference' mode)"
                        )

    # parse the arguments
    args = parser.parse_args(argv)

    # ensure the args are valid and then perform the appropriate actions
    validate_args(args, parser)
    execute_args(args)


# start of flow of execution, this is what's called from command line
if __name__ == "__main__":
    exit(main())
