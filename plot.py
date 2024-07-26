# This should be easy to instantiate and use elsewhere.

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class InfoPlot:
    """Provides an easy way for users to visualize the csvs."""

    def __init__(self, component_type=0, split_plot=False, save=True):
        self.component_type = component_type
        self.split_plot = split_plot
        self.file_path = (
            "Website/CSVs/gpu_info.csv"
            if component_type == 0
            else "Website/CSVs/cpu_info.csv"
        )
        self.df = None
        self.df1 = None
        self.df2 = None
        self.save = save

    def _read_data(self):
        self.df = pd.read_csv(self.file_path)
        self.df2 = self.df[len(self.df) // 2 :]
        self.df1 = self.df[: len(self.df) // 2]

    def plot(self):
        """Decides how to plot based on users wishes."""
        self._read_data()
        if self.component_type == 0:
            if self.split_plot:
                self._plot_gpu(self.df1)
                self._plot_gpu(self.df2)
                return
            self._plot_gpu(self.df)
            return
        if self.split_plot:
            self._plot_cpu(self.df1)
            self._plot_cpu(self.df2)
            return
        self._plot_cpu(self.df)
        return

    def _plot_gpu(self, data):
        _, ax = plt.subplots(figsize=(16, 12))
        width = 0.8
        space = 2
        indices = np.arange(len(data))
        r1 = indices * (3 * width + space)
        r2 = [x + width for x in r1]
        r3 = [x + width for x in r2]
        ax.bar(
            r1,
            data["Power Efficiency (FPS/W)"],
            width,
            label="Power Efficiency (FPS/W)",
            color="skyblue",
        )
        ax.bar(
            r2,
            data["Price Efficiency (FPS/$)"],
            width,
            label="Price Efficiency (FPS/$)",
            color="lightgreen",
        )
        ax.bar(
            r3,
            data["Average Efficiency"],
            width,
            label="Average Efficiency",
            color="salmon",
        )
        ax.set_xlabel("Graphics Cards", fontsize=12)
        ax.set_ylabel("Efficiency", fontsize=12)
        ax.set_title("Graphics Card Efficiency Comparison", fontsize=14)
        ax.set_xticks([r + width for r in r1])
        ax.set_xticklabels(data["Card"], rotation=90, ha="right", fontsize=12)
        ax.legend(fontsize=10)
        plt.tight_layout()
        self._add_value_labels(ax)

        if not self.save:
            plt.show()
        else:
            plt.savefig("Website/static/gpu_plot.png")

    def _plot_cpu(self, data):
        pass

    def _add_value_labels(self, ax, spacing=5):
        for rect in ax.patches:
            y_value = rect.get_height()
            x_value = rect.get_x() + rect.get_width() / 2
            label = f"{y_value:.3f}"
            ax.annotate(
                label,
                (x_value, y_value),
                xytext=(0, spacing),
                textcoords="offset points",
                ha="center",
                va="bottom",
                rotation=90,
                fontsize=8,
            )


plot = InfoPlot()
plot.plot()
