import pyaudio
import wave
import threading
import queue
import tempfile
import numpy as np
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class AudioCapture:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        audio_format: int = pyaudio.paInt16
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = audio_format

        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recording_thread: Optional[threading.Thread] = None

    def start_recording(self) -> None:
        if self.is_recording:
            logger.warning("Already recording")
            return

        self.is_recording = True
        self.audio_queue = queue.Queue()

        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            self.recording_thread = threading.Thread(
                target=self._record_audio,
                daemon=True
            )
            self.recording_thread.start()
            logger.info("Started recording")

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            raise

    def _record_audio(self) -> None:
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_queue.put(data)
            except Exception as e:
                logger.error(f"Error during recording: {e}")
                break

    def stop_recording(self) -> Optional[str]:
        if not self.is_recording:
            logger.warning("Not currently recording")
            return None

        self.is_recording = False

        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        logger.info("Stopped recording")
        return self._save_audio_to_file()

    def _save_audio_to_file(self) -> Optional[str]:
        if self.audio_queue.empty():
            logger.warning("No audio data to save")
            return None

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )
        temp_filename = temp_file.name
        temp_file.close()

        try:
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)

                while not self.audio_queue.empty():
                    data = self.audio_queue.get()
                    wf.writeframes(data)

            logger.info(f"Audio saved to {temp_filename}")
            return temp_filename

        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None

    def get_audio_level(self) -> float:
        if not self.is_recording or not self.stream:
            return 0.0

        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            level = np.abs(audio_data).mean() / 32768.0
            return level
        except:
            return 0.0

    def cleanup(self) -> None:
        if self.is_recording:
            self.stop_recording()

        if self.audio:
            self.audio.terminate()

    def __del__(self):
        self.cleanup()