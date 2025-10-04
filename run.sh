#!/bin/bash
# MyWhisper launcher script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Run MyWhisper
echo "Starting MyWhisper..."
echo "Press Ctrl+C to quit"
echo ""
echo "Default hotkey: Ctrl+Alt+Space (hold to record)"
echo "System tray icon will appear in your taskbar"
echo ""

./venv/bin/python main.py