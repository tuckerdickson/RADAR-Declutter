import os
import sys
import time

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from . import constants


class Demo:
    def __init__(self, input_path, output_path, model):
        self.input_path = input_path
        self.output_path = output_path
        self.model = model

        self.input_files = sorted(os.listdir(input_path))
        self.tracks = {}

    def run_tests(self):
        if not os.path.isdir(self.input_path):
            print(f"Error: {self.input_path} is not a valid directory path.")
            return

        if not os.path.isdir(self.output_path):
            print(f"Error: {self.output_path} is not a valid directory path.")
            return

        ani = FuncAnimation(plt.gcf(), self.run_test, frames=len(self.input_files), repeat=False, interval=1000)
        plt.show()

    def run_test(self, frame):
        in_file = os.path.join(self.input_path, self.input_files[frame])
        out_file = os.path.join(self.output_path, self.input_files[frame])

        df = self.model.make_inference(in_file, out_file, demo=True)

        plt.cla()
        plt.xlim(constants.DEMO_PLOT_X_LOWER, constants.DEMO_PLOT_X_UPPER)
        plt.ylim(constants.DEMO_PLOT_Y_LOWER, constants.DEMO_PLOT_Y_UPPER)

        for idx, row in df.iterrows():
            uuid = row["UUID"]
            x = row["Position (lat)"]
            y = row["Position (lon)"]

            if uuid in self.tracks:
                self.tracks[uuid]["xs"].append(x)
                self.tracks[uuid]["ys"].append(y)
            else:
                self.tracks[uuid] = {"xs": [x], "ys": [y]}

            # print(f"{uuid}: ({x}, {y})")
            plt.plot(self.tracks[uuid]["xs"], self.tracks[uuid]["ys"], '-')

        return
