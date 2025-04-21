#!/bin/bash

# Script to set up environment and run zeta analysis

echo "Setting up environment for zeta analysis..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install requests numpy matplotlib pandas scipy

# Run the analysis script
echo "Starting zeta analysis in background..."
nohup python3 zeta_analysis.py > zeta_analysis.log 2>&1 &

# Get the process ID
PID=$!
echo "Analysis running with PID: $PID"
echo "You can monitor progress with: tail -f zeta_analysis.log"
echo "Results will be saved in the output and figures directories"
