#!/bin/bash

echo "MyWhisper Setup Script"
echo "====================="
echo ""

echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi
echo "Python $python_version found ✓"

echo ""
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv portaudio19-dev python3-dev

echo ""
echo "Creating virtual environment..."
python3 -m venv venv

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Making main script executable..."
chmod +x main.py

echo ""
echo "Creating desktop entry..."
cat > ~/.local/share/applications/mywhisper.desktop << EOF
[Desktop Entry]
Name=MyWhisper
Comment=Voice Dictation Tool
Exec=$PWD/venv/bin/python $PWD/main.py
Icon=$PWD/icon.png
Type=Application
Categories=Utility;Audio;
Terminal=false
StartupNotify=false
EOF

echo ""
echo "Setup complete! ✓"
echo ""
echo "To run MyWhisper:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: ./main.py"
echo ""
echo "Or launch from your applications menu (MyWhisper)"
echo ""
echo "Default hotkey: Ctrl+Alt+Space (configurable in system tray menu)"