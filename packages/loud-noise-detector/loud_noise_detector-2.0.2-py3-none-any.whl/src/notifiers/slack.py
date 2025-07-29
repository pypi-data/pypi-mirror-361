import os
from typing import Any, Dict, List, Optional

import requests

from src.utils.config import Config

from .base import BaseNotifier


class SlackNotifier(BaseNotifier):

    @classmethod
    def create_if_configured(
        cls, config: Config, **kwargs: Any
    ) -> Optional["SlackNotifier"]:
        slack_config = config.notifier_options.get("slack", {})
        token = (
            kwargs.get("token")
            or slack_config.get("token")
            or os.getenv("SLACK_TOKEN")
        )
        channel = (
            kwargs.get("channel")
            or slack_config.get("channel")
            or os.getenv("SLACK_CHANNEL")
        )

        if not token or not channel:
            config.logger.warning(
                "Slack configuration not found."
                " Slack notifications will be disabled."
            )
            return None

        return cls(token=token, channel=channel)

    def __init__(
        self, token: Optional[str] = None, channel: Optional[str] = None
    ):
        self.token = token
        self.channel = channel

    def notify(
        self,
        recordings: List[Dict[str, Any]],
        timestamp: str,
        normalized_rms: float,
        config: Config,
    ) -> bool:
        recording_path = self._get_recording_path(recordings, config)
        if not recording_path:
            return False

        message = self._create_notification_message(
            timestamp, normalized_rms, config
        )

        try:
            filename = os.path.basename(recording_path)
            file_size = os.path.getsize(recording_path)

            upload_data = self._get_upload_url(
                filename, file_size, message, config
            )
            if not upload_data:
                return False

            if not self._upload_file_to_url(
                recording_path, upload_data["upload_url"], config
            ):
                return False

            if not self._complete_upload(
                upload_data["file_id"], filename, config
            ):
                return False

            return True
        except Exception as e:
            config.logger.error(f"Error sending notification to Slack: {e}")
            return False

    def _get_recording_path(
        self, recordings: List[Dict[str, Any]], config: Config
    ) -> Optional[str]:
        recording_path = None
        for recording in recordings:
            if "path" in recording:
                recording_path = recording["path"]
                break

        if not recording_path:
            config.logger.error("No recordings available to send to Slack.")

        return recording_path

    def _create_notification_message(
        self, timestamp: str, normalized_rms: float, config: Config
    ) -> str:
        return (
            f"@channel {config.get_localized_text('noise_detected')} "
            f"{timestamp}. "
            f"{config.get_localized_text('rms_amplitude')}: "
            f"{normalized_rms:.3f}. "
        )

    def _get_upload_url(
        self, filename: str, file_size: int, message: str, config: Config
    ) -> Optional[Dict[str, Any]]:
        headers = {"Authorization": f"Bearer {self.token}"}
        get_url_api = "https://slack.com/api/files.getUploadURLExternal"

        url_params = {
            "channels": self.channel,
            "filename": filename,
            "length": file_size,
            "initial_comment": message,
        }

        url_response = requests.post(
            get_url_api, headers=headers, data=url_params
        )
        url_result = url_response.json()

        if not url_result.get("ok", False):
            config.logger.error(
                "Error getting upload URL from Slack: "
                f"{url_result.get('error', 'Unknown error')}"
            )
            return None

        return {
            "upload_url": url_result.get("upload_url"),
            "file_id": url_result.get("file_id"),
        }

    def _upload_file_to_url(
        self, file_path: str, upload_url: str, config: Config
    ) -> bool:
        with open(file_path, "rb") as f:
            file_content = f.read()
            upload_response = requests.post(upload_url, data=file_content)

        if upload_response.status_code != 200:
            config.logger.error(
                f"Error uploading file to external URL: {upload_response.status_code}"
            )
            return False

        return True

    def _complete_upload(
        self, file_id: str, filename: str, config: Config
    ) -> bool:
        headers = {"Authorization": f"Bearer {self.token}"}
        complete_api = "https://slack.com/api/files.completeUploadExternal"

        complete_params = {
            "files": [{"id": file_id, "title": filename}],
            "channel_id": self.channel,
        }

        complete_response = requests.post(
            complete_api, headers=headers, json=complete_params
        )
        complete_result = complete_response.json()

        if not complete_result.get("ok", False):
            config.logger.error(
                "Error completing file upload: "
                f"{complete_result.get('error', 'Unknown error')}"
            )
            return False

        return True
