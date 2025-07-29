import time
from datetime import datetime
from typing import List, Optional

import pyaudio

from src.detector.processors.rms_processor import RMSProcessor
from src.notifiers.base import BaseNotifier
from src.recorders.base import BaseRecorder
from src.utils.config import Config


class AudioDetector:

    def __init__(
        self,
        config: Config,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
    ) -> None:
        self.config = config
        self.recorders = recorders
        self.notifiers = notifiers
        self._is_running = False
        self.stream: Optional[pyaudio.Stream] = None
        self.audio: Optional[pyaudio.PyAudio] = None
        self.rms_processor = RMSProcessor(config)
        self.detection_buffer: List[bytes] = []
        self.pre_buffer: List[bytes] = []
        self.last_detection_time = 0

    def setup(self) -> None:
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.config.format,
            channels=self.config.channels,
            rate=self.config.rate,
            input=True,
            frames_per_buffer=self.config.chunk_size,
        )

    def cleanup(self) -> None:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        self._is_running = False

    def start(self) -> None:
        self._is_running = True
        self.setup()

        self.config.logger.info(self.config.get_localized_text("listening"))

        try:
            pre_buffer_chunks = int(
                self.config.pre_buffer_seconds
                * self.config.rate
                / self.config.chunk_size
            )
            self.pre_buffer = []

            while self._is_running:
                if self.stream is not None:
                    data: bytes = self.stream.read(
                        self.config.chunk_size, exception_on_overflow=False
                    )
                else:
                    data = b""
                normalized_rms: float = self.rms_processor.calculate(data)

                self.pre_buffer.append(data)
                if len(self.pre_buffer) > pre_buffer_chunks:
                    self.pre_buffer.pop(0)

                if self.config.verbose:
                    print(
                        f"{self.config.get_localized_text('current_rms')}: "
                        f"{normalized_rms:.3f}",
                        end="\r",
                        flush=True,
                    )

                if self._should_detect(normalized_rms):
                    if self.config.verbose:
                        print()
                    self._handle_detection(normalized_rms, data)

        except KeyboardInterrupt:
            if self.config.verbose:
                print()
            self.config.logger.info(self.config.get_localized_text("stopping"))
        finally:
            self.cleanup()

    def stop(self) -> None:
        self._is_running = False

    def _should_detect(self, normalized_rms: float) -> bool:
        if normalized_rms < self.config.threshold:
            return False

        current_time = time.time()
        if (
            current_time - self.last_detection_time
            < self.config.cooldown_seconds
        ):
            return False

        return True

    def _handle_detection(self, normalized_rms: float, data: bytes) -> None:
        self.last_detection_time = int(time.time())
        timestamp: str = datetime.now().strftime(self.config.timestamp_format)

        self.config.logger.info(
            f"{self.config.get_localized_text('noise_detected')} "
            f"({self.config.get_localized_text('rms_amplitude')}: "
            f"{normalized_rms:.3f})"
        )

        self.detection_buffer = list(self.pre_buffer)
        self.detection_buffer.append(data)

        chunks_per_second = self.config.rate / self.config.chunk_size
        total_chunks_needed = int(
            self.config.seconds_to_record * chunks_per_second
        )

        remaining_chunks = total_chunks_needed - len(self.detection_buffer)

        for _ in range(remaining_chunks):
            if not self._is_running:
                break
            if self.stream is not None:
                data = self.stream.read(
                    self.config.chunk_size, exception_on_overflow=False
                )
            else:
                data = b""
            self.detection_buffer.append(data)

        self._save_and_notify(normalized_rms, timestamp)

    def _save_and_notify(self, normalized_rms: float, timestamp: str) -> None:
        recordings = []
        for recorder in self.recorders:
            recording = recorder.save(
                self.detection_buffer, self.config, timestamp, normalized_rms
            )
            recordings.append(recording)

        for notifier in self.notifiers:
            if notifier.notify(
                recordings, timestamp, normalized_rms, self.config
            ):
                self.config.logger.info(
                    self.config.get_localized_text("notification_sent")
                )

        if not self.config.keep_files:
            for recording in recordings:
                if recording["temporary"] and recording["path"]:
                    for recorder in self.recorders:
                        if recorder.remove_file(
                            recording["path"], self.config
                        ):  # noqa: E501
                            break
