# componentTracking

Tracks the current prices of all modern GPUs and does some analysis.
Currently does not account for condition.

## Setup

### 1. Clone the Repository

Clone this repository to your local machine.

```bash
git clone git@github.com:wlauer3/componentTracking.git
cd componentTracking
```

### 2. Create and Activate a Virtual Environment

Create a virtual environment to manage your dependencies.

```bash
python3 -m venv venv

# Activate the virtual environment

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

## Usage

### Easiest way

This way runs the quering and the website automatically.

#### 1. Permissons

- `chmod +x run.sh`

#### 2. Run the script

- `./run.sh`

### Alternative way

#### 1. Configure the Script

Before running the script, you may need to set the following options in the `query.py` file:

- `SEARCHGPUS`: Set to `True` if you want to search for GPUs, `False` otherwise.
- `SEARCHCPUS`: Set to `True` if you want to search for CPUs, `False` otherwise.

#### 2. Run the Script

Run the script to update the CSV file with the latest prices and performance data.

```bash
python query.py
```

#### 3. Run the website

##### 2. Run the Script

1. cd to the Website dir
2. `python app.py`
3. Open localhost:5000 in a browser
