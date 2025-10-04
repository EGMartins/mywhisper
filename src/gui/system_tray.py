import pystray
from PIL import Image, ImageDraw
import threading
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


class SystemTrayIcon:
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.icon: Optional[pystray.Icon] = None
        self.is_recording = False
        self._create_icon()

    def _create_icon(self):
        menu = pystray.Menu(
            pystray.MenuItem(
                "Recording Mode",
                pystray.Menu(
                    pystray.MenuItem(
                        "Push to Talk",
                        self._on_mode_push,
                        checked=lambda item: self.app_controller.get_recording_mode() == "push"
                    ),
                    pystray.MenuItem(
                        "Toggle",
                        self._on_mode_toggle,
                        checked=lambda item: self.app_controller.get_recording_mode() == "toggle"
                    )
                )
            ),
            pystray.MenuItem(
                "Model",
                pystray.Menu(
                    pystray.MenuItem(
                        "Tiny (39MB)",
                        lambda: self._on_model_change("tiny"),
                        checked=lambda item: self.app_controller.get_model() == "tiny"
                    ),
                    pystray.MenuItem(
                        "Base (74MB)",
                        lambda: self._on_model_change("base"),
                        checked=lambda item: self.app_controller.get_model() == "base"
                    ),
                    pystray.MenuItem(
                        "Small (244MB)",
                        lambda: self._on_model_change("small"),
                        checked=lambda item: self.app_controller.get_model() == "small"
                    ),
                    pystray.MenuItem(
                        "Medium (769MB)",
                        lambda: self._on_model_change("medium"),
                        checked=lambda item: self.app_controller.get_model() == "medium"
                    ),
                    pystray.MenuItem(
                        "Large (1550MB)",
                        lambda: self._on_model_change("large"),
                        checked=lambda item: self.app_controller.get_model() == "large"
                    )
                )
            ),
            pystray.MenuItem("Settings", self._on_settings),
            pystray.MenuItem("", None),
            pystray.MenuItem("Quit", self._on_quit)
        )

        image = self._create_tray_image(recording=False)
        self.icon = pystray.Icon("MyWhisper", image, "MyWhisper - Voice Dictation", menu)

    def _create_tray_image(self, recording: bool = False) -> Image.Image:
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        if recording:
            color = (255, 0, 0, 255)
        else:
            color = (100, 100, 100, 255)

        draw.ellipse([size//4, size//4, 3*size//4, 3*size//4], fill=color)

        draw.ellipse([3*size//8, size//4-4, 5*size//8, size//4+12],
                    fill=(200, 200, 200, 255))

        return image

    def update_recording_status(self, is_recording: bool):
        self.is_recording = is_recording
        if self.icon:
            self.icon.icon = self._create_tray_image(recording=is_recording)

    def _on_mode_push(self, icon, item):
        self.app_controller.set_recording_mode("push")
        logger.info("Recording mode set to push-to-talk")

    def _on_mode_toggle(self, icon, item):
        self.app_controller.set_recording_mode("toggle")
        logger.info("Recording mode set to toggle")

    def _on_model_change(self, model_name: str):
        self.app_controller.change_model(model_name)
        logger.info(f"Model changed to {model_name}")

    def _on_settings(self, icon, item):
        logger.info("Settings menu clicked")

    def _on_quit(self, icon, item):
        logger.info("Quit requested")
        self.stop()
        self.app_controller.quit()

    def run(self):
        try:
            # Run in main thread for better compatibility
            self.icon.run_detached()
            logger.info("System tray icon started")
        except Exception as e:
            logger.error(f"Failed to start system tray: {e}")
            # Fallback to threaded approach
            thread = threading.Thread(target=self.icon.run, daemon=True)
            thread.start()
            logger.info("System tray icon started in thread")

    def stop(self):
        if self.icon:
            self.icon.stop()
            logger.info("System tray icon stopped")