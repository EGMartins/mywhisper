import whisper
import os
import threading
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    def __init__(
        self,
        model_name: str = "base",
        language: str = "en",
        device: Optional[str] = None
    ):
        self.model_name = model_name if model_name in self.AVAILABLE_MODELS else "base"
        self.language = language
        self.device = device
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(
                self.model_name,
                device=self.device
            )
            logger.info(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def transcribe(
        self,
        audio_file: str,
        callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        if not self.model:
            logger.error("Model not loaded")
            return None

        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        try:
            logger.info(f"Transcribing audio file: {audio_file}")

            result = self.model.transcribe(
                audio_file,
                language=self.language,
                fp16=False
            )

            text = result["text"].strip()
            logger.info(f"Transcription complete: {text[:50]}...")

            if callback:
                callback(text)

            return text

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

        finally:
            try:
                os.remove(audio_file)
                logger.debug(f"Deleted temporary audio file: {audio_file}")
            except:
                pass

    def transcribe_async(
        self,
        audio_file: str,
        callback: Callable[[str], None]
    ) -> None:
        thread = threading.Thread(
            target=self.transcribe,
            args=(audio_file, callback),
            daemon=True
        )
        thread.start()

    def change_model(self, model_name: str) -> bool:
        if model_name not in self.AVAILABLE_MODELS:
            logger.error(f"Invalid model name: {model_name}")
            return False

        if model_name == self.model_name:
            logger.info(f"Model {model_name} already loaded")
            return True

        try:
            self.model_name = model_name
            self._load_model()
            return True
        except Exception as e:
            logger.error(f"Failed to change model: {e}")
            return False

    def set_language(self, language: str) -> None:
        self.language = language
        logger.info(f"Language set to: {language}")

    def get_available_models(self) -> list:
        return self.AVAILABLE_MODELS

    def get_current_model(self) -> str:
        return self.model_name