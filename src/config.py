import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Config:
    DEFAULT_CONFIG = {
        "hotkey": ["ctrl", "alt", "space"],
        "recording_mode": "push",  # "push" or "toggle"
        "model": "base",
        "language": "en",
        "insertion_method": "clipboard",  # "clipboard" or "typing"
        "audio": {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024
        },
        "ui": {
            "show_notifications": True,
            "play_sound": False
        }
    }

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_dir = Path.home() / ".config" / "mywhisper"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"
        else:
            self.config_path = Path(config_path)

        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded_config)
                    logger.info(f"Configuration loaded from {self.config_path}")
                    return config
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            logger.info("No configuration file found, using defaults")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config: Dict[str, Any] = None) -> bool:
        if config is None:
            config = self.config

        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

    def get_hotkey(self) -> list:
        return self.config.get("hotkey", self.DEFAULT_CONFIG["hotkey"])

    def set_hotkey(self, keys: list) -> None:
        self.set("hotkey", keys)

    def get_recording_mode(self) -> str:
        return self.config.get("recording_mode", self.DEFAULT_CONFIG["recording_mode"])

    def set_recording_mode(self, mode: str) -> None:
        if mode in ["push", "toggle"]:
            self.set("recording_mode", mode)

    def get_model(self) -> str:
        return self.config.get("model", self.DEFAULT_CONFIG["model"])

    def set_model(self, model: str) -> None:
        self.set("model", model)

    def get_language(self) -> str:
        return self.config.get("language", self.DEFAULT_CONFIG["language"])

    def set_language(self, language: str) -> None:
        self.set("language", language)

    def get_audio_config(self) -> dict:
        return self.config.get("audio", self.DEFAULT_CONFIG["audio"])

    def reset_to_defaults(self) -> None:
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()