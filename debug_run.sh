#!/bin/bash
# Run MyWhisper with verbose logging to debug

cd /home/eduardo/Projects/mywhisper
source venv/bin/activate

# Kill any existing instance
pkill -f "mywhisper/main.py"

# Run with debug output to a log file
python3 main.py 2>&1 | tee mywhisper_debug.log
