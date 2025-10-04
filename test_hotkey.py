#!/usr/bin/env python3
"""Test script to verify hotkey detection"""

from pynput import keyboard
import logging

logging.basicConfig(level=logging.DEBUG)

print("Hotkey Test - Press Ctrl+Alt+Space")
print("Press ESC to exit")
print("-" * 40)

current_keys = set()

def on_press(key):
    current_keys.add(key)
    print(f"Pressed: {key}")

    # Check for Ctrl+Alt+Space
    if (keyboard.Key.ctrl_l in current_keys or keyboard.Key.ctrl_r in current_keys) and \
       (keyboard.Key.alt_l in current_keys or keyboard.Key.alt_r in current_keys) and \
       keyboard.Key.space in current_keys:
        print("\n*** HOTKEY DETECTED! Ctrl+Alt+Space ***\n")

    # Exit on ESC
    if key == keyboard.Key.esc:
        return False

def on_release(key):
    try:
        current_keys.remove(key)
        print(f"Released: {key}")
    except KeyError:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()