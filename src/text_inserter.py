import pyautogui
import pyperclip
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TextInserter:
    def __init__(self):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01

    def insert_text(self, text: str, method: str = "clipboard") -> bool:
        if not text:
            logger.warning("No text to insert")
            return False

        try:
            if method == "clipboard":
                return self._insert_via_clipboard(text)
            elif method == "typing":
                return self._insert_via_typing(text)
            else:
                logger.error(f"Unknown insertion method: {method}")
                return False

        except Exception as e:
            logger.error(f"Failed to insert text: {e}")
            return False

    def _insert_via_clipboard(self, text: str) -> bool:
        try:
            old_clipboard = pyperclip.paste()

            pyperclip.copy(text)

            time.sleep(0.05)

            pyautogui.hotkey('ctrl', 'v')

            time.sleep(0.1)

            try:
                pyperclip.copy(old_clipboard)
            except:
                pass

            logger.info(f"Text inserted via clipboard: {text[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Clipboard insertion failed: {e}")
            return False

    def _insert_via_typing(self, text: str) -> bool:
        try:
            pyautogui.write(text, interval=0.01)
            logger.info(f"Text inserted via typing: {text[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Typing insertion failed: {e}")
            return False

    def insert_at_cursor(self, text: str) -> bool:
        return self.insert_text(text, method="clipboard")

    def simulate_key(self, key: str) -> bool:
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            logger.error(f"Failed to simulate key {key}: {e}")
            return False

    def simulate_hotkey(self, *keys) -> bool:
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            logger.error(f"Failed to simulate hotkey {keys}: {e}")
            return False