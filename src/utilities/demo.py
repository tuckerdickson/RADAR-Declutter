import matplotlib.pyplot as plt
import os
import pandas as pd
import time

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
        if frame > 0:
            in_file = os.path.join(self.input_path, self.input_files[frame])
            out_file = os.path.join(self.output_path, self.input_files[frame])

            start = time.time()
            df = self.model.make_inference(pd.read_csv(in_file), out_file, demo=True)
            end = time.time()

            elapsed = end - start

            ax1.cla()
            ax1.set_xlim(constants.DEMO_PLOT_X_LOWER, constants.DEMO_PLOT_X_UPPER)
            ax1.set_ylim(constants.DEMO_PLOT_Y_LOWER, constants.DEMO_PLOT_Y_UPPER)

            ax1.set_title("Object Trajectories")
            ax1.ticklabel_format(useOffset=False)

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
                                         "count": 1}

                marker = 'b-' if row["Class"] == 0 else 'r-'
                ax1.plot(self.tracks[uuid]["xs"], self.tracks[uuid]["ys"], marker, markersize=20)
                table_data.append([uuid[0:5], self.tracks[uuid]["count"], gt, pred, f"{conf:.2f}"])

            ax2.cla()
            ax2.axis('off')

            bbox = [0, 0, 1.2, 0.05*(1+len(df))]
            table = ax2.table(cellText=table_data,
                              colLabels=self.table_cols,
                              bbox=bbox,
                              loc='center')
            table.set_fontsize(10)
            table.scale(1.5, 1.5)

            accuracy = metrics.accuracy_score(df["Class"], df["Prediction"])

            txt = f"""Time = {frame+1} ({self.input_files[frame]})\n
            \n
            Objects present: {len(df)}\n
            Process Time: {elapsed:.4f} seconds\n
            \n
            Accuracy: {accuracy:.2f}
            Average confidence: {df["Confidence"].mean():.2f}"""

            ax2.text(0, 0.68, txt, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

            plt.ticklabel_format(style='plain')

            return
