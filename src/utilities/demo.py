import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pandas as pd
import time

from matplotlib.animation import FuncAnimation
from sklearn import metrics
from . import constants


class CsvDemo:
    def __init__(self, input_path, output_path, model):
        """
        The initializer for the CSV demo. Initializes all class attributes.
        :param input_path: The path to the directory containing all input CSV files.
        :param output_path: The path to the directory to save the resulting CSV files (with the prediction appended).
        :param model: The classification model.
        """
        self.input_path = input_path        # directory with input CSV files
        self.output_path = output_path      # directory to write output CSV files
        self.model = model                  # classification model

        # all the individual input CSV files
        self.input_files = sorted(os.listdir(input_path))

        # stores the (x, y) coordinate pairs for plotting each of the track trajectories
        self.tracks = {}

        # column headers for the table
        self.table_cols = ["UUID", "Update #", "Ground Truth", "Prediction", "Confidence"]

    def run_tests(self):
        """
        Kicks off the demo, running a classification for each CSV file in input_files and plotting the results.
        :return: None.
        """
        # create a subplot with 1 row and 2 columns (one for the trajectory plot and 1 for the table/text)
        fig, axes = plt.subplots(nrows=1,
                                 ncols=2,
                                 figsize=(14, 8),
                                 gridspec_kw={'width_ratios': [1.5, 1]})

        # the table/text axis doesn't need any axes so turn them off
        axes[1].axis('off')

        # this FunctionAnimation calls run_test once every second
        ani = FuncAnimation(fig,
                            self.run_test,
                            fargs=(axes[0], axes[1]),
                            frames=len(self.input_files),
                            repeat=False,
                            interval=1000)
        plt.show()

    def run_test(self, frame, ax1, ax2):
        """
        Runs a "test" (i.e., a classification and plotting the results) for a single CSV file.
        :param frame: The frame (i.e., time point) in which this test is being run.
        :param ax1: The first axis of the figure (left, or trajectory plot)
        :param ax2: The second axis of the figure (right, or table/text)
        :return: None.
        """
        # for some reason, weird behavior happens in the first frame, so we skip it
        if frame > 0:
            # using frame as an index, get the current input and output files
            in_file = os.path.join(self.input_path, self.input_files[frame])
            out_file = os.path.join(self.output_path, self.input_files[frame])

            # keeping track of how long it takes, pass the input file through the classifier to get its predictions
            start = time.time()
            df = self.model.make_inference(pd.read_csv(in_file), out_file, demo=True)
            end = time.time()

            # calculate the time elapsed during the classification
            elapsed = end - start

            # clear the trajectory plot axis; this keeps things from layering on top of each other
            ax1.cla()

            # set the upper and lower bounds for the x and y axes on the trajectory plot
            ax1.set_xlim(constants.DEMO_PLOT_X_LOWER, constants.DEMO_PLOT_X_UPPER)
            ax1.set_ylim(constants.DEMO_PLOT_Y_LOWER, constants.DEMO_PLOT_Y_UPPER)

            # set the title of the trajectory plot
            ax1.set_title("Object Trajectories")

            # this line prevents the trajectory plot axis labels from being formatted as scientific notation
            ax1.ticklabel_format(useOffset=False, style='plain')

            # stores the track information that will be displayed in the table (each row is a different track)
            table_data = []

            # iterate through each of the updates in the input csv file
            for idx, row in df.iterrows():
                # extract the UUID, latitude, and longitude of the object
                uuid = row["UUID"]

                x = row["Position (lat)"]
                y = row["Position (lon)"]

                # here we convert 0/1 to Bird/Drone for readability
                gt = "Bird" if row["Class"] == 0 else "Drone"
                pred = "Bird" if row["Prediction"] == 0 else "Drone"
                conf = row["Confidence"]

                # if this track has been encountered, add its (lat,lon) coordinates to whatever is there already
                if uuid in self.tracks:
                    self.tracks[uuid]["xs"].append(x)
                    self.tracks[uuid]["ys"].append(y)
                    self.tracks[uuid]["count"] += 1

                # otherwise, start a new list of (lat,lon) coordinates
                else:
                    self.tracks[uuid] = {"xs": [x],
                                         "ys": [y],
                                         "count": 1}

                # blue marker for birds, red for drones
                marker = 'b-' if row["Class"] == 0 else 'r-'

                # plot the track and add its data to the table
                ax1.plot(self.tracks[uuid]["xs"], self.tracks[uuid]["ys"], marker, markersize=20)
                table_data.append([uuid[0:5], self.tracks[uuid]["count"], gt, pred, f"{conf:.2f}"])

            # clear the table/text axis; this keeps things from layering on top of each other
            ax2.cla()

            # the table/text axis doesn't need any axes so turn them off
            ax2.axis('off')

            # create the table from table_data, set the font size and scale so that it fits in the window
            bbox = [0, 0, 1.2, 0.05*(1+len(df))]
            table = ax2.table(cellText=table_data,
                              colLabels=self.table_cols,
                              bbox=bbox,
                              loc='center')
            table.set_fontsize(10)
            table.scale(1.5, 1.5)

            # calculate the accuracy of the predictions this time point
            accuracy = metrics.accuracy_score(df["Class"], df["Prediction"])

            # create the text to be displayed in the top right
            txt = f"""Time = {frame+1} ({self.input_files[frame]})\n
            \n
            Objects present: {len(df)}\n
            Process Time: {elapsed:.4f} seconds\n
            \n
            Accuracy: {accuracy:.2f}
            Average confidence: {df["Confidence"].mean():.2f}"""

            ax2.text(0, 0.68, txt, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})


class NetworkDemo:
    """
    This class is responsible for running the system demonstration, when using a networked connection as input (as
    opposed to csv files).

    Attributes:
        table_cols: List of column headers to be displayed in the table within the demo.
        table_data: List of lists containing the rows for the table in the demo (where each row is a different object).
        text_data: A dictionary containing the current time step and the processing time for the current time step.
        results: A dictionary breaking down the number of true positives, false positives, true negatives, and false
                    negatives per time step.
        tracks: The (x,y) coordinate pairs for each track, used for plotting the trajectories.
        model: The classification model used to make predictions.
        fig: The matplotlib figure used to display the demo.
        axes: The matplotlib axes (axes[0] <-> trajectory plot, axes[1] <-> table and text data)
    """
    def __init__(self, model):
        """
        Initializes the class attributes for the NetworkDemo class.
        :param model: The classification model used to make predictions.
        """
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
        self.fig, self.axes = plt.subplots(nrows=1,
                                           ncols=2,
                                           figsize=(14, 8),
                                           gridspec_kw={'width_ratios': [1.5, 1]})

        # set the title of the trajectory plot
        self.axes[0].set_title("Object Trajectories")

        # format the axes on the trajectory plot (so that they aren't in scientific notation)
        plt.ticklabel_format(useOffset=False, style='plain')
        self.axes[0].xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))
        self.axes[0].yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.3f}'))

    def update_plot(self):
        """
        Updates the window after all updates for a given time step have been received.
        :return: None.
        """
        # plot the trajectories
        for uuid in self.tracks.keys():
            # use blue markers for birds and red markers for drones
            marker = 'b-' if self.tracks[uuid]["gt"] == "Bird" else 'r-'
            self.axes[0].plot(self.tracks[uuid]["xs"], self.tracks[uuid]["ys"], marker, markersize=20, label=uuid)

        # # clear the right axis (table and text)
        self.axes[1].cla()
        self.axes[1].axis('off')

        # create the table
        bbox = [0, 0, 1.2, 0.05*(1+min(10, len(self.table_data)))]
        table = self.axes[1].table(cellText=self.table_data[-10:],
                                   colLabels=self.table_cols,
                                   bbox=bbox,
                                   loc='center')

        # set the font size and scale so that it will fit on the figure
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.5, 1.5)

        # the text to be displayed in the top right (includes time, objects present, processing time, accuracy, F1, ...)
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

        # display the text
        self.axes[1].text(0, 0.68, txt, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

        # recompute axis limits and automatically scale the trajectory plot, based on the data present
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
        """
        Runs a "test" (i.e., a timed classification and plotting the results) for a single update.
        :param input_df: A DataFrame containing information for an update on an object.
        :return: None.
        """
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

        # update the true positives, false positives, true negatives, or false negatives accordingly
        if pred == "Bird" and gt == "Bird":
            self.results["TN"] += 1
        elif pred == "Bird" and gt == "Drone":
            self.results["FN"] += 1
        elif pred == "Drone" and gt == "Bird":
            self.results["FP"] += 1
        elif pred == "Drone" and gt == "Drone":
            self.results["TP"] += 1

    def calculate_accuracy(self):
        """
        Calculates the accuracy of the predictions for a certain time point.
        :return: The accuracy of the predictions for the time point.
        """
        tp = self.results["TP"]     # true positives
        fp = self.results["FP"]     # false positives
        tn = self.results["TN"]     # true negatives
        fn = self.results["FN"]     # false negatives

        # return the accuracy
        return (tp + tn) / (tp + tn + fp + fn)

    def calculate_f1(self):
        """
        Calculates the F1 score of the predictions for a certain time point.
        :return: The F1 score of the predictions for the time point.
        """
        tp = self.results["TP"]     # true positives
        fp = self.results["FP"]     # false positives
        fn = self.results["FN"]     # true negatives

        # calculate precision, recall, and F1 score
        precision = tp / (tp + fp) if tp + fp != 0 else 0
        recall = tp / (tp + fn) if tp + fn != 0 else 0

        # return F1 score
        return (2 * precision * recall) / (precision + recall) if precision + recall != 0 else 0

    def calculate_avg_conf(self):
        """
        Calculates the average confidence level of all the tracks encountered in a certain time point.
        :return: The average confidence level of all the current tracks.
        """
        confs = [float(update[4]) for update in self.table_data]
        return np.mean(confs)
