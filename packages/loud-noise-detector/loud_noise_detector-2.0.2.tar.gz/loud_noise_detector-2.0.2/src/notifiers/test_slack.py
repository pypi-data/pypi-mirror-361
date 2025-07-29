import os
from typing import Any, Dict, Generator, Optional
from unittest.mock import MagicMock, patch

import pytest

from src.notifiers.slack import SlackNotifier
from src.utils.config import Config

TEST_RECORDING = {"path": "/tmp/test_recording.wav", "format": "wav"}
TEST_RECORDINGS = [TEST_RECORDING]
TEST_TIMESTAMP = "timestamp"
TEST_THRESHOLD = 0.5


class TestSlackNotifier:
    @pytest.fixture
    def config(self) -> Config:
        config = Config()
        return config

    @pytest.fixture
    def notifier(self) -> SlackNotifier:
        return SlackNotifier()

    @pytest.fixture
    def env_with_slack_config(self) -> Generator[None, None, None]:
        with patch.dict(
            os.environ,
            {"SLACK_TOKEN": "test_token", "SLACK_CHANNEL": "test_channel"},
            clear=True,
        ):
            yield

    @pytest.fixture
    def mock_file_read(self) -> Generator[None, None, None]:
        mock_content = MagicMock()
        mock_content.read.return_value = b"content"

        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_content
        mock_file.__exit__.return_value = None

        with patch("builtins.open", return_value=mock_file):
            yield

    @pytest.fixture
    def mock_file_size(self) -> Generator[None, None, None]:
        with patch("os.path.getsize", return_value=1024):
            yield

    @pytest.fixture
    def mock_successful_slack_upload(
        self,
        mock_file_read: Generator[None, None, None],
        mock_file_size: Generator[None, None, None],
    ) -> Generator[Dict[str, MagicMock], None, None]:
        mock_url_response = MagicMock()
        mock_url_response.json.return_value = {
            "ok": True,
            "upload_url": "https://slack-upload.example.com",
            "file_id": "F12345678",
        }

        mock_upload_response = MagicMock()
        mock_upload_response.status_code = 200

        mock_complete_response = MagicMock()
        mock_complete_response.json.return_value = {"ok": True}

        def mock_post_side_effect(url, **kwargs):
            if "getUploadURLExternal" in url:
                return mock_url_response
            elif "slack-upload.example.com" in url:
                return mock_upload_response
            elif "completeUploadExternal" in url:
                return mock_complete_response
            return MagicMock()

        mock_post = MagicMock()
        mock_post.side_effect = mock_post_side_effect

        with patch("requests.post", mock_post):
            yield {
                "post": mock_post,
                "url_response": mock_url_response,
                "upload_response": mock_upload_response,
                "complete_response": mock_complete_response,
            }

    @pytest.fixture
    def mock_logger(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def config_with_logger(
        self, config: Config, mock_logger: MagicMock
    ) -> Generator[Config, None, None]:
        with patch.object(config, "logger", mock_logger):
            yield config

    @pytest.mark.parametrize(
        "env_vars,expected_result,error_count",
        [
            ({"SLACK_TOKEN": "test_token"}, False, 1),
            ({"SLACK_CHANNEL": "test_channel"}, False, 1),
            ({}, False, 1),
        ],
    )
    def test_notify_missing_config(
        self,
        notifier: SlackNotifier,
        config_with_logger: Config,
        mock_logger: MagicMock,
        env_vars: Dict[str, str],
        expected_result: bool,
        error_count: int,
    ) -> None:
        with patch.dict(os.environ, env_vars, clear=True):
            result = notifier.notify(
                [], TEST_TIMESTAMP, TEST_THRESHOLD, config_with_logger
            )

            assert result is expected_result
            assert mock_logger.error.call_count == error_count

    def test_notify_successful(
        self,
        notifier: SlackNotifier,
        config: Config,
        mock_successful_slack_upload: Dict[str, MagicMock],
        env_with_slack_config: Generator[None, None, None],
        mock_file_size: Generator[None, None, None],
    ) -> None:
        result = notifier.notify(
            TEST_RECORDINGS, TEST_TIMESTAMP, TEST_THRESHOLD, config
        )
        assert result is True

        mock_post = mock_successful_slack_upload["post"]

        get_url_calls = [
            call
            for call in mock_post.call_args_list
            if "getUploadURLExternal" in call[0][0]
        ]
        assert len(get_url_calls) == 1

        complete_calls = [
            call
            for call in mock_post.call_args_list
            if "completeUploadExternal" in call[0][0]
        ]
        assert len(complete_calls) == 1

    @pytest.mark.parametrize(
        "stage,response_data,expected_result",
        [
            ("url", {"ok": False, "error": "invalid_token"}, False),
            ("upload", None, False),
            ("complete", {"ok": False, "error": "invalid_file"}, False),
        ],
    )
    def test_notify_handles_api_errors(
        self,
        notifier: SlackNotifier,
        config_with_logger: Config,
        mock_logger: MagicMock,
        stage: str,
        response_data: Optional[Dict[str, Any]],
        expected_result: bool,
        env_with_slack_config: Generator[None, None, None],
        mock_file_read: Generator[None, None, None],
        mock_file_size: Generator[None, None, None],
    ) -> None:
        url_response = MagicMock()
        url_response.json.return_value = (
            {
                "ok": True,
                "upload_url": "https://example.com",
                "file_id": "F12345",
            }
            if stage != "url"
            else response_data
        )

        upload_response = MagicMock()
        upload_response.status_code = 400 if stage == "upload" else 200

        complete_response = MagicMock()
        complete_response.json.return_value = (
            {"ok": True} if stage != "complete" else response_data
        )

        def mock_post_side_effect(url, **kwargs):
            if "getUploadURLExternal" in url:
                return url_response
            elif "example.com" in url:
                return upload_response
            elif "completeUploadExternal" in url:
                return complete_response
            return MagicMock()

        with patch("requests.post", side_effect=mock_post_side_effect):
            result = notifier.notify(
                TEST_RECORDINGS,
                TEST_TIMESTAMP,
                TEST_THRESHOLD,
                config_with_logger,
            )

            assert result is expected_result
            assert mock_logger.error.call_count > 0

    def test_notify_handles_exceptions(
        self,
        notifier: SlackNotifier,
        config_with_logger: Config,
        mock_logger: MagicMock,
        env_with_slack_config: Generator[None, None, None],
    ) -> None:
        with patch("requests.post", side_effect=Exception("Test error")):
            result = notifier.notify(
                TEST_RECORDINGS,
                TEST_TIMESTAMP,
                TEST_THRESHOLD,
                config_with_logger,
            )

            assert result is False
            assert mock_logger.error.call_count > 0

    @pytest.mark.parametrize(
        "config_source,expected_token,expected_channel",
        [
            ("env", "test_token", "test_channel"),
            ("config", "config_token", "config_channel"),
            ("params", "param_token", "param_channel"),
        ],
    )
    def test_create_if_configured_sources(
        self,
        config: Config,
        config_source: str,
        expected_token: str,
        expected_channel: str,
    ) -> None:
        if config_source == "env":
            with patch.dict(
                os.environ,
                {"SLACK_TOKEN": "test_token", "SLACK_CHANNEL": "test_channel"},
                clear=True,
            ):
                notifier = SlackNotifier.create_if_configured(config)
        elif config_source == "config":
            config.notifier_options = {
                "slack": {"token": "config_token", "channel": "config_channel"}
            }
            notifier = SlackNotifier.create_if_configured(config)
        else:
            notifier = SlackNotifier.create_if_configured(
                config, token="param_token", channel="param_channel"
            )

        assert notifier is not None
        assert notifier.token == expected_token
        assert notifier.channel == expected_channel

    def test_notify_no_recordings(
        self,
        notifier: SlackNotifier,
        config_with_logger: Config,
        mock_logger: MagicMock,
        env_with_slack_config: Generator[None, None, None],
    ) -> None:
        result = notifier.notify(
            [], TEST_TIMESTAMP, TEST_THRESHOLD, config_with_logger
        )

        assert result is False
        assert mock_logger.error.call_count == 1

    def test_create_if_configured_no_config(self, config: Config) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config.notifier_options = {}

            notifier = SlackNotifier.create_if_configured(config)

            assert notifier is None

    def test_get_recording_path(
        self,
        notifier: SlackNotifier,
        config_with_logger: Config,
        mock_logger: MagicMock,
    ) -> None:
        path = notifier._get_recording_path(
            TEST_RECORDINGS, config_with_logger
        )
        assert path == TEST_RECORDING["path"]

        path = notifier._get_recording_path([], config_with_logger)
        assert path is None
        assert mock_logger.error.call_count == 1

    def test_create_notification_message(
        self, notifier: SlackNotifier, config: Config
    ) -> None:
        with patch.object(
            config, "get_localized_text", side_effect=lambda key: key
        ):
            message = notifier._create_notification_message(
                TEST_TIMESTAMP, TEST_THRESHOLD, config
            )
            assert TEST_TIMESTAMP in message
            assert str(TEST_THRESHOLD) in message
            assert "noise_detected" in message
            assert "rms_amplitude" in message
