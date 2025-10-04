from pynput import keyboard
from typing import Callable, Optional, Set
import threading
import logging

logger = logging.getLogger(__name__)


class HotkeyManager:
    def __init__(self):
        self.listener: Optional[keyboard.Listener] = None
        self.hotkey_callback: Optional[Callable] = None
        self.hotkey_combination: Set[keyboard.Key | keyboard.KeyCode] = {
            keyboard.Key.ctrl_l,
            keyboard.Key.alt_l,
            keyboard.Key.space
        }
        self.current_keys: Set[keyboard.Key | keyboard.KeyCode] = set()
        self.recording_mode = "push"  # "push" or "toggle"
        self.is_pressed = False

    def set_hotkey(self, keys: list) -> None:
        self.hotkey_combination = set()
        for key in keys:
            if isinstance(key, str):
                if key.lower() == "ctrl":
                    self.hotkey_combination.add(keyboard.Key.ctrl_l)
                elif key.lower() == "alt":
                    self.hotkey_combination.add(keyboard.Key.alt_l)
                elif key.lower() == "shift":
                    self.hotkey_combination.add(keyboard.Key.shift_l)
                elif key.lower() == "space":
                    self.hotkey_combination.add(keyboard.Key.space)
                else:
                    try:
                        self.hotkey_combination.add(keyboard.KeyCode.from_char(key))
                    except:
                        logger.warning(f"Invalid key: {key}")

        logger.info(f"Hotkey set to: {keys}")

    def set_recording_mode(self, mode: str) -> None:
        if mode in ["push", "toggle"]:
            self.recording_mode = mode
            logger.info(f"Recording mode set to: {mode}")
        else:
            logger.warning(f"Invalid recording mode: {mode}")

    def register_callback(self, callback: Callable) -> None:
        self.hotkey_callback = callback

    def start(self) -> None:
        if self.listener:
            self.stop()

        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        logger.info("Hotkey listener started")

    def _on_press(self, key) -> None:
        self.current_keys.add(key)

        if self._is_hotkey_pressed() and not self.is_pressed:
            self.is_pressed = True
            if self.hotkey_callback:
                if self.recording_mode == "push":
                    threading.Thread(
                        target=lambda: self.hotkey_callback("start"),
                        daemon=True
                    ).start()
                elif self.recording_mode == "toggle":
                    threading.Thread(
                        target=lambda: self.hotkey_callback("toggle"),
                        daemon=True
                    ).start()

    def _on_release(self, key) -> None:
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass

        if self.recording_mode == "push" and self.is_pressed:
            if not self._is_hotkey_pressed():
                self.is_pressed = False
                if self.hotkey_callback:
                    threading.Thread(
                        target=lambda: self.hotkey_callback("stop"),
                        daemon=True
                    ).start()
        elif self.recording_mode == "toggle":
            if not self._is_hotkey_pressed():
                self.is_pressed = False

    def _is_hotkey_pressed(self) -> bool:
        for key in self.hotkey_combination:
            if isinstance(key, keyboard.Key):
                if key not in self.current_keys:
                    alt_key = None
                    if key == keyboard.Key.ctrl_l:
                        alt_key = keyboard.Key.ctrl_r
                    elif key == keyboard.Key.alt_l:
                        alt_key = keyboard.Key.alt_r
                    elif key == keyboard.Key.shift_l:
                        alt_key = keyboard.Key.shift_r

                    if alt_key and alt_key not in self.current_keys:
                        return False
                    elif not alt_key:
                        return False
            else:
                if key not in self.current_keys:
                    return False
        return True

    def stop(self) -> None:
        if self.listener:
            self.listener.stop()
            self.listener = None
            logger.info("Hotkey listener stopped")

    def __del__(self):
        self.stop()