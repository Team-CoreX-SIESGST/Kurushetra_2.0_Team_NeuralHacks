#!/bin/bash

echo "Starting OmniSearch AI Streamlit Frontend..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

# Start Streamlit
echo "Starting Streamlit application..."
echo "Frontend will open at: http://localhost:8501"
echo
echo "Press Ctrl+C to stop the application"
echo

streamlit run app.py
