import sounddevice as sd
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
        audio_format: str = 'int16'
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.dtype = audio_format

        self.stream: Optional[sd.InputStream] = None
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
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            self.stream.start()
            logger.info("Started recording")

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            raise

    def _audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def stop_recording(self) -> Optional[str]:
        if not self.is_recording:
            logger.warning("Not currently recording")
            return None

        self.is_recording = False

        if self.stream:
            self.stream.stop()
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
            audio_data = []
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())

            if audio_data:
                audio_array = np.concatenate(audio_data)

                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 2 bytes for int16
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_array.tobytes())

                logger.info(f"Audio saved to {temp_filename}")
                return temp_filename
            else:
                logger.warning("No audio data collected")
                return None

        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None

    def get_audio_level(self) -> float:
        if not self.is_recording:
            return 0.0

        try:
            if not self.audio_queue.empty():
                data = list(self.audio_queue.queue)[-1]
                level = np.abs(data).mean() / 32768.0
                return float(level)
        except:
            pass
        return 0.0

    def cleanup(self) -> None:
        if self.is_recording:
            self.stop_recording()

    def __del__(self):
        self.cleanup()