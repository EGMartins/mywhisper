"""Wayland-compatible window for MyWhisper"""

import sys
import threading
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction

import logging

logger = logging.getLogger(__name__)


class RecordingThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, audio_capture, transcriber):
        super().__init__()
        self.audio_capture = audio_capture
        self.transcriber = transcriber

    def run(self):
        try:
            audio_file = self.audio_capture.stop_recording()
            if audio_file:
                text = self.transcriber.transcribe(audio_file)
                if text:
                    self.finished.emit(text)
                else:
                    self.error.emit("No text transcribed")
            else:
                self.error.emit("No audio captured")
        except Exception as e:
            self.error.emit(str(e))


class WaylandWindow(QWidget):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.is_recording = False
        self.init_ui()
        self.create_tray_icon()

    def init_ui(self):
        self.setWindowTitle('MyWhisper')
        self.setFixedSize(250, 120)

        # Window flags for staying on top
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Status label
        self.status_label = QLabel('Ready')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)

        # Record button
        self.record_button = QPushButton('Hold to Record')
        self.record_button.setCheckable(True)
        self.record_button.pressed.connect(self.start_recording)
        self.record_button.released.connect(self.stop_recording)
        self.record_button.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:pressed {
                background-color: #ff4444;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.record_button)

        # Toggle mode button
        self.toggle_button = QPushButton('Minimize')
        self.toggle_button.clicked.connect(self.hide)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                padding: 5px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.toggle_button)

        self.setLayout(layout)

        # Position window in bottom-right corner
        self.move_to_corner()

    def move_to_corner(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20,
                  screen.height() - self.height() - 100)

    def create_tray_icon(self):
        try:
            self.tray_icon = QSystemTrayIcon(self)

            # Create icon
            icon = QIcon("icon.png")
            if icon.isNull():
                # Create a default icon if file doesn't exist
                from PyQt6.QtGui import QPixmap
                pixmap = QPixmap(16, 16)
                pixmap.fill(Qt.GlobalColor.blue)
                icon = QIcon(pixmap)

            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip("MyWhisper - Click to show/hide")

            # Create menu
            menu = QMenu()

            show_action = QAction("Show/Hide", self)
            show_action.triggered.connect(self.toggle_visibility)
            menu.addAction(show_action)

            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.quit_application)
            menu.addAction(quit_action)

            self.tray_icon.setContextMenu(menu)

            # Click to show/hide
            self.tray_icon.activated.connect(self.on_tray_activated)

            self.tray_icon.show()
            logger.info("System tray icon created")
        except Exception as e:
            logger.error(f"Failed to create tray icon: {e}")

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visibility()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            self.move_to_corner()

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.status_label.setText('🔴 Recording...')
            self.record_button.setText('Release to Stop')
            self.app_controller.start_recording()
            logger.info("Started recording (GUI button)")

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.status_label.setText('Processing...')
            self.record_button.setText('Hold to Record')

            # Create and start recording thread
            self.recording_thread = RecordingThread(
                self.app_controller.audio_capture,
                self.app_controller.transcriber
            )
            self.recording_thread.finished.connect(self.on_transcription_complete)
            self.recording_thread.error.connect(self.on_transcription_error)
            self.recording_thread.start()
            logger.info("Stopped recording (GUI button)")

    def on_transcription_complete(self, text):
        logger.info(f"Transcription complete: {text[:50]}...")
        self.status_label.setText(f'✓ Transcribed')
        self.app_controller.text_inserter.insert_at_cursor(text)

        # Reset status after 2 seconds
        QTimer.singleShot(2000, lambda: self.status_label.setText('Ready'))

    def on_transcription_error(self, error):
        logger.error(f"Transcription error: {error}")
        self.status_label.setText(f'Error: {error[:20]}')
        QTimer.singleShot(3000, lambda: self.status_label.setText('Ready'))

    def quit_application(self):
        self.app_controller.quit()

    def closeEvent(self, event):
        # Hide instead of closing
        event.ignore()
        self.hide()
        if self.tray_icon:
            self.tray_icon.showMessage(
                "MyWhisper",
                "Application minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )