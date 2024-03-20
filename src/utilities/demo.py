import os
import time

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.animation import FuncAnimation
from sklearn import metrics

from . import constants


class Demo:
    def __init__(self, input_path, output_path, model):
        self.input_path = input_path
        self.output_path = output_path
        self.model = model

        self.input_files = sorted(os.listdir(input_path))
        self.tracks = {}
        self.table_cols = ["UUID", "Update #", "Ground Truth", "Prediction", "Confidence"]

    def run_tests(self):
        if not os.path.isdir(self.input_path):
            print(f"Error: {self.input_path} is not a valid directory path.")
            return

        if not os.path.isdir(self.output_path):
            print(f"Error: {self.output_path} is not a valid directory path.")
            return

        fig, axes = plt.subplots(nrows=1,
                                 ncols=2,
                                 figsize=(14, 8),
                                 gridspec_kw={'width_ratios': [1.5, 1]})
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

        start = time.time()
        df = self.model.make_inference(in_file, out_file, demo=True)
        end = time.time()

        elapsed = end - start

        ax1.cla()
        ax1.set_xlim(constants.DEMO_PLOT_X_LOWER, constants.DEMO_PLOT_X_UPPER)
        ax1.set_ylim(constants.DEMO_PLOT_Y_LOWER, constants.DEMO_PLOT_Y_UPPER)
        ax1.set_title("temp")

        table_data = []
        for idx, row in df.iterrows():
            uuid = row["UUID"]

            x = row["Position (lat)"]
            y = row["Position (lon)"]

            gt = "Bird" if row["Class"] == 0 else "Drone"
            pred = "Bird" if row["Prediction"] == 0 else "Drone"
            conf = row["Confidence"]

            if uuid in self.tracks:
                self.tracks[uuid]["xs"].append(x)
                self.tracks[uuid]["ys"].append(y)
                self.tracks[uuid]["count"] += 1
            else:
                self.tracks[uuid] = {"xs": [x],
                                     "ys": [y],
                                     "count": 0}

            marker = 'b-' if row["Class"] == 0 else 'r-'
            ax1.plot(self.tracks[uuid]["xs"], self.tracks[uuid]["ys"], marker, markersize=20)
            table_data.append([uuid[0:5], self.tracks[uuid]["count"], gt, pred, conf])

        ax2.cla()
        ax2.axis('off')

        bbox = [0, 0, 1, 0.05*(1+len(df))]
        ax2.table(cellText=table_data,
                  colLabels=self.table_cols,
                  bbox=bbox,
                  loc='center')

        accuracy = metrics.accuracy_score(df["Class"], df["Prediction"])
        f1 = metrics.f1_score(df["Class"], df["Prediction"], zero_division=0)

        txt = f"""Time = {frame+1} ({self.input_files[frame]})\n
        \n
        Objects present: {len(df)}\n
        Process Time: {elapsed:.4f} seconds\n
        \n
        Accuracy: {accuracy:.2f}
        F1 Score:{f1:.2f}
        Average confidence: {df["Confidence"].mean():.2f}"""

        ax2.text(0, 0.65, txt, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
        return
