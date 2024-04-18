import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import time

from matplotlib.animation import FuncAnimation
from sklearn import metrics
from . import constants


class CsvDemo:
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


class NetworkDemo:
    def __init__(self, model):
        # the column names displayed in the table in the pyplot window
        self.table_cols = ["UUID", "Update #", "Ground Truth", "Prediction", "Confidence"]

        # stores the rows for the table in the pyplot window
        self.table_data = []

        # stores other fields displayed in the pyplot window
        self.text_data = {
            "current_time": 1,
            "elapsed_time": 0,
        }

        # used for calculating the accuracy and F1 score at each time point
        self.results = {
            "TP": 0,
            "FP": 0,
            "TN": 0,
            "FN": 0
        }

        # stores the (x, y) coordinate pairs that make up the tracks displayed within the pyplot window
        self.tracks = {}

        # the classifier, used to make predictions
        self.model = model

        # the pyplot window
        plt.ion()
        # plt.ticklabel_format(style='plain')
        self.fig, self.axes = plt.subplots(nrows=1,
                                           ncols=2,
                                           figsize=(14, 8),
                                           gridspec_kw={'width_ratios': [1.5, 1]})

        self.axes[0].set_title("Object Trajectories")

    def update_plot(self):
        # plot the trajectories
        for uuid in self.tracks.keys():
            # use blue markers for birds and red markers for drones
            marker = 'b-' if self.tracks[uuid]["gt"] == "Bird" else 'r-'
            self.axes[0].plot(self.tracks[uuid]["xs"], self.tracks[uuid]["ys"], marker, markersize=20, label=uuid)

        # # clear the right axis (table and text)
        self.axes[1].cla()
        self.axes[1].axis('off')

        # create the table
        bbox = [0, 0, 1.2, 0.05*(1+len(self.table_data))]
        table = self.axes[1].table(cellText=self.table_data,
                                   colLabels=self.table_cols,
                                   bbox=bbox,
                                   loc='center')

        # set the font size and scale so that it will fit on the figure
        table.set_fontsize(10)
        table.scale(1.5, 1.5)

        txt = f"""Time = {self.text_data["current_time"]}
        \n
        Objects present: {len(self.table_data)}
        Process Time: {self.text_data["elapsed_time"]:.4f} seconds
        \n
        TP: {self.results["TP"]}   FP: {self.results["FP"]}
        TN: {self.results["TN"]}   FN: {self.results["FN"]}
        \n
        Accuracy: {self.calculate_accuracy():.2f}
        F1 score: {self.calculate_f1():.2f}
        Average confidence: {np.mean(self.calculate_avg_conf()):.2f}"""

        self.axes[1].text(0, 0.68, txt, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

        self.axes[0].relim()
        self.axes[0].autoscale_view()

        # write out the new trajectory plots
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        # increment the current time and reset the elapsed time
        self.text_data["current_time"] += 1
        self.text_data["elapsed_time"] = 0

        # clear the table data so that the rows appear updated in the next time step
        self.table_data = []

        # zero the results
        for r in ["TP", "FP", "TN", "FN"]:
            self.results[r] = 0

    def run_test(self, input_df):
        # pass the update through the model, keeping track of how long it takes
        start = time.time()
        df = self.model.make_inference(input_df, demo=True)
        end = time.time()

        # add the elapsed time for this update to the running time for this time point
        self.text_data["elapsed_time"] += end - start

        # extract the necessary fields from the update (to be put into the table)
        uuid = int(df.iloc[0]["UUID"])
        x = df.iloc[0]["Position (lat)"]
        y = df.iloc[0]["Position (lon)"]
        gt = "Bird" if df.iloc[0]["Class"] == 0 else "Drone"
        pred = "Bird" if df.iloc[0]["Prediction"] == 0 else "Drone"
        conf = df.iloc[0]["Confidence"]

        # if this object has already been encountered, add the current position to the plot
        if uuid in self.tracks:
            self.tracks[uuid]["xs"].append(x)
            self.tracks[uuid]["ys"].append(y)
            self.tracks[uuid]["count"] += 1

        # if this is a new object, start a new plot
        else:
            self.tracks[uuid] = {"xs": [x],
                                 "ys": [y],
                                 "count": 1,
                                 "gt": gt}

        # add the current update to the table
        self.table_data.append([uuid, self.tracks[uuid]["count"], gt, pred, f"{conf:.2f}"])

        # update the results
        if pred == "Bird" and gt == "Bird":
            self.results["TN"] += 1
        elif pred == "Bird" and gt == "Drone":
            self.results["FN"] += 1
        elif pred == "Drone" and gt == "Bird":
            self.results["FP"] += 1
        elif pred == "Drone" and gt == "Drone":
            self.results["TP"] += 1

    def calculate_accuracy(self):
        tp = self.results["TP"]
        fp = self.results["FP"]
        tn = self.results["TN"]
        fn = self.results["FN"]

        return (tp + tn) / (tp + tn + fp + fn)

    def calculate_f1(self):
        tp = self.results["TP"]
        fp = self.results["FP"]
        fn = self.results["FN"]

        precision = tp / (tp + fp) if tp + fp != 0 else 0
        recall = tp / (tp + fn) if tp + fn != 0 else 0
        return (2 * precision * recall) / (precision + recall) if precision + recall != 0 else 0

    def calculate_avg_conf(self):
        confs = [float(update[4]) for update in self.table_data]
        return np.mean(confs)
