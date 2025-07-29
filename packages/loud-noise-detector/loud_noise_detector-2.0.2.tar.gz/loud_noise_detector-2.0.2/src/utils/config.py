import json
import logging
import os
from typing import Any, Dict, Optional

import yaml


class Config:

    def __init__(self, config_file: Optional[str] = None) -> None:
        # Default configuration values
        self.threshold = 0.1
        self.cooldown_seconds = 5
        self.seconds_to_record = 5
        self.pre_buffer_seconds = 2
        self.rate = 44100
        self.channels = 1
        self.format = 8  # pyaudio.paInt16
        self.chunk_size = 1024
        self.keep_files = True
        self.verbose = False
        self.timestamp_format = "%Y%m%d_%H%M%S"
        self.language = "en"
        self.notifier_options: Dict[str, Any] = {}
        self.logger: logging.Logger = logging.getLogger("loud_noise_detector")

        # Load configuration from file if provided
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)

    def _load_from_file(self, config_file: str) -> None:
        try:
            with open(config_file, "r") as f:
                if config_file.endswith(".yaml") or config_file.endswith(
                    ".yml"
                ):
                    config_data = yaml.safe_load(f)
                elif config_file.endswith(".json"):
                    config_data = json.load(f)
                else:
                    raise ValueError(
                        f"Unsupported config file format: {config_file}"
                    )

                # Update configuration values
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except Exception as e:
            self.logger.error(
                f"Failed to load configuration from {config_file}: {e}"
            )

    def get_localized_text(self, key: str) -> str:
        try:
            translations_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "localization",
                "translations",
                f"{self.language}.json",
            )

            with open(translations_file, "r", encoding="utf-8") as f:
                translations = json.load(f)

            return str(translations.get(key, key))
        except Exception as e:
            self.logger.error(f"Translation error for key '{key}': {e}")
            return key
