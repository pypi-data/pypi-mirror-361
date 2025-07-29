from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.utils.config import Config


class BaseRecorder(ABC):

    @abstractmethod
    def save(
        self,
        chunks: List[bytes],
        config: Config,
        timestamp: str,
        normalized_rms: float,
    ) -> Dict[str, Any]:
        raise NotImplementedError("Recorder must implement save")

    @abstractmethod
    def remove_file(self, file_path: str, config: Config) -> bool:
        raise NotImplementedError("Recorder must implement remove_file")
