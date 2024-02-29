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
        self.table_cols = ["UUID", "Update #", "Prediction", "Confidence"]

    def run_tests(self):
        if not os.path.isdir(self.input_path):
            print(f"Error: {self.input_path} is not a valid directory path.")
            return

        if not os.path.isdir(self.output_path):
            print(f"Error: {self.output_path} is not a valid directory path.")
            return

        fig, axes = plt.subplots(nrows=1,
                                 ncols=2,
                                 figsize=(10, 8),
                                 gridspec_kw={'width_ratios': [2, 1]})
        axes[1].axis('off')

        ani = FuncAnimation(fig,
                            self.run_test,
                            fargs=(axes[0], axes[1]),
                            frames=len(self.input_files),
                            repeat=False,
                            interval=1000)
        plt.show()

    def run_test(self, frame, ax1, ax2):
        in_file = os.path.join(self.input_path, self.input_files[frame])
        out_file = os.path.join(self.output_path, self.input_files[frame])

        df = self.model.make_inference(in_file, out_file, demo=True)

        ax1.cla()
        ax1.set_xlim(constants.DEMO_PLOT_X_LOWER, constants.DEMO_PLOT_X_UPPER)
        ax1.set_ylim(constants.DEMO_PLOT_Y_LOWER, constants.DEMO_PLOT_Y_UPPER)

        table_data = []
        for idx, row in df.iterrows():
            uuid = row["UUID"]

            x = row["Position (lat)"]
            y = row["Position (lon)"]

            pred = row["Prediction"]
            conf = row["Confidence"]

            if uuid in self.tracks:
                self.tracks[uuid]["xs"].append(x)
                self.tracks[uuid]["ys"].append(y)
                self.tracks[uuid]["count"] += 1
            else:
                self.tracks[uuid] = {"xs": [x],
                                     "ys": [y],
                                     "count": 0}

            ax1.plot(self.tracks[uuid]["xs"], self.tracks[uuid]["ys"], '-')
            table_data.append([uuid[0:5], self.tracks[uuid]["count"], pred, conf])

        ax2.table(cellText=table_data,
                  colLabels=self.table_cols,
                  loc='top')
        return
