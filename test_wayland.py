#!/usr/bin/env python3
"""Test for Wayland - uses a simple GUI window with a button"""

import sys
import time
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from src.audio_capture import AudioCapture
from src.transcriber import WhisperTranscriber
from src.text_inserter import TextInserter

class RecordingThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, audio, transcriber):
        super().__init__()
        self.audio = audio
        self.transcriber = transcriber

    def run(self):
        audio_file = self.audio.stop_recording()
        if audio_file:
            text = self.transcriber.transcribe(audio_file)
            if text:
                self.finished.emit(text)

class MyWhisperWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.audio = AudioCapture()
        self.transcriber = WhisperTranscriber(model_name="tiny")
        self.text_inserter = TextInserter()
        self.is_recording = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('MyWhisper - Wayland Mode')
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.status_label = QLabel('Ready')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.record_button = QPushButton('Push to Record')
        self.record_button.setCheckable(True)
        self.record_button.pressed.connect(self.start_recording)
        self.record_button.released.connect(self.stop_recording)
        self.record_button.setStyleSheet("""
            QPushButton {
                padding: 20px;
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: #ff4444;
                color: white;
            }
        """)
        layout.addWidget(self.record_button)

        self.setLayout(layout)

        # Keep window on top
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.status_label.setText('🔴 Recording...')
            self.audio.start_recording()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.status_label.setText('Processing...')

            self.recording_thread = RecordingThread(self.audio, self.transcriber)
            self.recording_thread.finished.connect(self.on_transcription_complete)
            self.recording_thread.start()

    def on_transcription_complete(self, text):
        self.status_label.setText(f'Text: {text[:30]}...')
        self.text_inserter.insert_at_cursor(text)
        # Reset status after 2 seconds
        threading.Timer(2.0, lambda: self.status_label.setText('Ready')).start()

if __name__ == '__main__':
    print("=" * 50)
    print("MyWhisper - Wayland Compatible Mode")
    print("=" * 50)
    print("\nSince you're on Wayland, global hotkeys don't work.")
    print("Use the GUI window instead:")
    print("- Click and HOLD the button to record")
    print("- RELEASE to stop and transcribe")
    print("\nThe window stays on top for easy access.")
    print("=" * 50)

    app = QApplication(sys.argv)
    window = MyWhisperWindow()
    window.show()
    sys.exit(app.exec())