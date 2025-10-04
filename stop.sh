#!/bin/bash
# Stop MyWhisper

echo "Stopping MyWhisper..."
pkill -f "python.*main.py"
pkill -f "python.*mywhisper"
echo "MyWhisper stopped"