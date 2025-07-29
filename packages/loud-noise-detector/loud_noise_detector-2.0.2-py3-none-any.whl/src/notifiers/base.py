from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar

from src.utils.config import Config

T = TypeVar("T", bound="BaseNotifier")


class BaseNotifier(ABC):

    @classmethod
    @abstractmethod
    def create_if_configured(
        cls: Type[T], config: Config, **kwargs: Any
    ) -> Optional[T]:
        raise NotImplementedError(
            "Notifier must implement create_if_configured"
        )

    @abstractmethod
    def notify(
        self,
        recordings: List[Dict[str, Any]],
        timestamp: str,
        normalized_rms: float,
        config: Config,
    ) -> bool:
        raise NotImplementedError("Notifier must implement notify")
