#!/usr/bin/env python3

import sys
import os
import signal
import logging
import threading
from src.audio_capture import AudioCapture
from src.transcriber import WhisperTranscriber
from src.hotkey_manager import HotkeyManager
from src.text_inserter import TextInserter
from src.gui.system_tray import SystemTrayIcon
from src.config import Config

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MyWhisperApp:
    def __init__(self):
        logger.info("Initializing MyWhisper...")

        self.config = Config()

        audio_config = self.config.get_audio_config()
        self.audio_capture = AudioCapture(
            sample_rate=audio_config["sample_rate"],
            channels=audio_config["channels"],
            chunk_size=audio_config["chunk_size"]
        )

        self.transcriber = WhisperTranscriber(
            model_name=self.config.get_model(),
            language=self.config.get_language()
        )

        self.text_inserter = TextInserter()

        # Check if we're on Wayland
        self.is_wayland = os.environ.get('XDG_SESSION_TYPE') == 'wayland'

        if self.is_wayland:
            logger.info("Wayland detected - using GUI mode")
            self.hotkey_manager = None
            self.system_tray = None
            self.wayland_window = None
        else:
            logger.info("X11 detected - using hotkey mode")
            self.hotkey_manager = HotkeyManager()
            self.hotkey_manager.set_hotkey(self.config.get_hotkey())
            self.hotkey_manager.set_recording_mode(self.config.get_recording_mode())
            self.hotkey_manager.register_callback(self.handle_hotkey)
            self.system_tray = SystemTrayIcon(self)
            self.wayland_window = None

        self.is_recording = False
        self.running = True

    def handle_hotkey(self, action: str):
        logger.debug(f"Hotkey action: {action}")

        if action == "start":
            self.start_recording()
        elif action == "stop":
            self.stop_recording()
        elif action == "toggle":
            if self.is_recording:
                self.stop_recording()
            else:
                self.start_recording()

    def start_recording(self):
        if not self.is_recording:
            logger.info("Starting recording...")
            self.is_recording = True
            self.system_tray.update_recording_status(True)
            self.audio_capture.start_recording()

    def stop_recording(self):
        if self.is_recording:
            logger.info("Stopping recording...")
            self.is_recording = False
            self.system_tray.update_recording_status(False)

            audio_file = self.audio_capture.stop_recording()
            if audio_file:
                self.transcriber.transcribe_async(
                    audio_file,
                    self.on_transcription_complete
                )

    def on_transcription_complete(self, text: str):
        if text:
            logger.info(f"Transcription complete: {text}")
            success = self.text_inserter.insert_at_cursor(text)
            if success:
                logger.info("Text inserted successfully")
            else:
                logger.error("Failed to insert text")

    def get_recording_mode(self) -> str:
        return self.config.get_recording_mode()

    def set_recording_mode(self, mode: str):
        self.config.set_recording_mode(mode)
        self.hotkey_manager.set_recording_mode(mode)

    def get_model(self) -> str:
        return self.config.get_model()

    def change_model(self, model_name: str):
        if self.transcriber.change_model(model_name):
            self.config.set_model(model_name)
            return True
        return False

    def run(self):
        logger.info("Starting MyWhisper...")

        if self.is_wayland:
            # Use PyQt6 for Wayland
            from PyQt6.QtWidgets import QApplication
            from src.wayland_window import WaylandWindow

            app = QApplication(sys.argv)
            app.setApplicationName("MyWhisper")
            app.setApplicationDisplayName("MyWhisper")

            self.wayland_window = WaylandWindow(self)
            self.wayland_window.show()

            sys.exit(app.exec())
        else:
            # Use hotkeys for X11
            if self.hotkey_manager:
                self.hotkey_manager.start()

            if self.system_tray:
                self.system_tray.run()

            try:
                while self.running:
                    threading.Event().wait(1)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                self.quit()

    def quit(self):
        logger.info("Shutting down MyWhisper...")
        self.running = False

        if self.is_recording:
            self.stop_recording()

        if self.hotkey_manager:
            self.hotkey_manager.stop()

        self.audio_capture.cleanup()

        if not self.is_wayland:
            sys.exit(0)


def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    app = MyWhisperApp()
    app.run()


if __name__ == "__main__":
    main()