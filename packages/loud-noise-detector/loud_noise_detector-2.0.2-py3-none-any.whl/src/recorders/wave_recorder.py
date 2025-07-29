import os
import wave
from typing import Any, Dict, List, Optional

from src.utils.config import Config

from .base import BaseRecorder


class WaveRecorder(BaseRecorder):
    def __init__(
        self,
        output_dir: Optional[str] = None,
        prefix: str = "loud_",
        temporary: bool = True,
    ):
        self.output_dir = output_dir or os.getcwd()
        self.prefix = prefix
        self.temporary = temporary

        os.makedirs(self.output_dir, exist_ok=True)

    def save(
        self,
        chunks: List[bytes],
        config: Config,
        timestamp: str,
        normalized_rms: float,
    ) -> Dict[str, Any]:
        filename = f"{self.prefix}{timestamp}.wav"
        filepath = os.path.join(self.output_dir, filename)

        sample_width = 2

        with wave.open(filepath, "wb") as wf:
            wf.setnchannels(config.channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(config.rate)
            wf.writeframes(b"".join(chunks))

        if config.verbose:
            config.logger.info(
                f"{config.get_localized_text('recording_saved')}: {filepath}"
            )

        return {
            "path": filepath,
            "format": "wav",
            "temporary": self.temporary,
            "timestamp": timestamp,
            "rms": normalized_rms,
        }

    def remove_file(self, file_path: str, config: Config) -> bool:
        try:
            os.remove(file_path)
            if config.verbose:
                config.logger.info(
                    f"{config.get_localized_text('temp_file_removed')}: "
                    f"{file_path}"
                )
            return True
        except Exception as e:
            if config.verbose:
                config.logger.error(
                    f"Error removing file {file_path}: {str(e)}"
                )
            return False
