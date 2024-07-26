#!/bin/bash


PYTHON_SCRIPT="query.py"
WEBSITE_SCRIPT="app.py"

# Run queries
echo "Running Queries..."
# python3 "$PYTHON_SCRIPT"


# Run webserver
echo "Starting Website..."
cd Website
python3 "$WEBSITE_SCRIPT"
