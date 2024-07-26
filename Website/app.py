from flask import Flask
from flask import render_template
import pandas as pd

app = Flask(__name__)


@app.route("/")
def display_gpu_data():
    gpu_data = pd.read_csv("./CSVs/gpu_info.csv")
    data_to_display = gpu_data.to_html(index=False)
    return render_template("display_gpu.html", table=data_to_display)


@app.route("/cpu")
def display_cpu_data():
    cpu_data = pd.read_csv("./CSVs/cpu_info.csv")
    data_to_display = cpu_data.to_html(index=False)
    return render_template("display_cpu.html", table=data_to_display)


@app.route("/ddr4")
def display_ddr_four():
    cpu_data = pd.read_csv("./CSVs/memoryDDR4.csv")
    data_to_display = cpu_data.to_html(index=False)
    return render_template("display_ddr4.html", table=data_to_display)


@app.route("/ddr5")
def display_ddr_five():
    cpu_data = pd.read_csv("./CSVs/memoryDDR5.csv")
    data_to_display = cpu_data.to_html(index=False)
    return render_template("display_ddr5.html", table=data_to_display)


if __name__ == "__main__":
    app.run(debug=False)
