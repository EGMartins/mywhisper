#!/usr/bin/env python3
"""Simple test to verify the core functionality works"""

import time
import logging
from src.audio_capture import AudioCapture
from src.transcriber import WhisperTranscriber
from src.text_inserter import TextInserter
from src.hotkey_manager import HotkeyManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("=" * 50)
print("MyWhisper Simple Test")
print("=" * 50)
print("\nPress and HOLD Ctrl+Alt+Space to record")
print("RELEASE to stop recording and transcribe")
print("Press Ctrl+C to exit\n")
print("=" * 50)

# Initialize components
audio = AudioCapture()
transcriber = WhisperTranscriber(model_name="tiny")  # Use tiny for faster testing
text_inserter = TextInserter()
hotkey = HotkeyManager()

is_recording = False

def handle_hotkey(action):
    global is_recording

    if action == "start":
        if not is_recording:
            print("\n🔴 RECORDING... Speak now!")
            is_recording = True
            audio.start_recording()

    elif action == "stop":
        if is_recording:
            print("⏹️  Stopping recording...")
            is_recording = False
            audio_file = audio.stop_recording()

            if audio_file:
                print("🔄 Transcribing...")
                text = transcriber.transcribe(audio_file)

                if text:
                    print(f"📝 Transcribed: {text}")
                    print("✏️  Inserting text...")
                    text_inserter.insert_at_cursor(text)
                    print("✅ Done!\n")
                else:
                    print("❌ No text transcribed\n")

# Set up hotkey
hotkey.set_hotkey(["ctrl", "alt", "space"])
hotkey.set_recording_mode("push")  # Push-to-talk mode
hotkey.register_callback(handle_hotkey)
hotkey.start()

print("\nReady! The hotkey listener is active.\n")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nShutting down...")
    hotkey.stop()
    audio.cleanup()
    print("Goodbye!")