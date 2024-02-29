import os
import sys
import time

import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation


def run_tests(in_path, out_path, model):
    if not os.path.isdir(in_path):
        print(f"Error: {in_path} is not a valid directory path.")
        return

    if not os.path.isdir(out_path):
        print(f"Error: {out_path} is not a valid directory path.")
        return

    in_files = sorted(os.listdir(in_path))

    xs = []
    ys = []

    ani = FuncAnimation(plt.gcf(), run_test, fargs=(xs, ys), interval=1000)  # Update every 1000 milliseconds (1 second)
    plt.show()

    # for file in in_files:
        # print(f"Processing {file}")
        # in_file = os.path.join(in_path, file)
        # out_file = os.path.join(out_path, file)
        #
        # run_test(in_file, out_file, model)
        # time.sleep(1)
        # input("Press any key to continue...\n")


def run_test(frame, xs, ys):
    plt.cla()

    xs.append(frame)
    ys.append(frame)

    plt.plot(xs, ys, 'bo')
    plt.xlim(0, 10)  # Example limits for the X-axis
    plt.ylim(0, 10)

    # plt.legend(loc='upper left')
    # plt.tight_layout()


# def run_test(file_path, out_path, model):
    # results = model.make_inference(file_path, out_path, demo=True)
    #
    # for idx, row in results.iterrows():
    #     pred_class = "Drone" if row["Prediction"] else "Bird"
    #     # print(f"{pred_class}: {100 * row["Confidence"]}%")
    #
    #     plot_point(row["Position (lat)"], row["Position (lon)"])

    return


def plot_point(x, y):
    plt.plot(x, y, "ro")
    plt.show()
    # print(f"Plotting point: {x}, {y}")