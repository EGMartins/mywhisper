import pyautogui
import pyperclip
import time
import logging
import subprocess
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
            # Use xclip directly for more reliable clipboard setting
            try:
                # Set clipboard using xclip
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                          stdin=subprocess.PIPE)
                process.communicate(input=text.encode('utf-8'))
                process.wait()
                logger.debug("Clipboard set via xclip")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to pyperclip
                pyperclip.copy(text)
                logger.debug("Clipboard set via pyperclip")

            # Wait for clipboard to be fully set
            time.sleep(0.15)

            # Verify clipboard content
            try:
                verify = subprocess.run(['xclip', '-o', '-selection', 'clipboard'],
                                       capture_output=True, text=True, timeout=1)
                if verify.stdout != text:
                    logger.warning(f"Clipboard verification failed. Expected: '{text[:30]}...', Got: '{verify.stdout[:30]}...'")
            except:
                pass

            # Get active window name to determine paste method
            paste_success = False
            try:
                window_name = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'],
                                            capture_output=True, text=True, check=True).stdout.lower()

                # Terminals use Ctrl+Shift+V
                is_terminal = any(term in window_name for term in ['terminal', 'konsole', 'gnome-terminal', 'xterm', 'alacritty', 'kitty', 'zellij'])

                if is_terminal:
                    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+v'],
                                  check=True, capture_output=True)
                    logger.info(f"Text inserted via xdotool (terminal mode): {text[:50]}...")
                else:
                    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+v'],
                                  check=True, capture_output=True)
                    logger.info(f"Text inserted via xdotool: {text[:50]}...")
                paste_success = True
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.debug(f"xdotool failed: {e}")

            # Fallback to pyautogui
            if not paste_success:
                pyautogui.hotkey('ctrl', 'v')
                logger.info(f"Text inserted via pyautogui: {text[:50]}...")

            time.sleep(0.1)

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