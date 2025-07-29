import os
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest

from src.main import main, parse_arguments


class TestArgumentParsing:

    def test_parse_arguments_default(self) -> None:
        with patch("sys.argv", ["main.py"]):
            args = parse_arguments()
            assert args.config == "config/default_config.yaml"
            assert args.verbose is False
            assert args.output_dir == "data/recordings"
            assert args.threshold is None
            assert args.language == "en"
            assert args.delete_files is False

    def test_parse_arguments_custom(self) -> None:
        test_args = [
            "main.py",
            "--config",
            "custom_config.yaml",
            "--verbose",
            "--output-dir",
            "custom/dir",
            "--threshold",
            "0.3",
            "--language",
            "es",
            "--no-keep-files",
        ]
        with patch("sys.argv", test_args):
            args = parse_arguments()
            assert args.config == "custom_config.yaml"
            assert args.verbose is True
            assert args.output_dir == "custom/dir"
            assert args.threshold == 0.3
            assert args.language == "es"
            assert args.delete_files is True


class TestMainFunction:

    @pytest.fixture
    def setup_mocks(self) -> Generator[dict, None, None]:
        mocks = {}

        with patch("src.main.Config") as mock_config_class, patch(
            "src.main.setup_logger"
        ) as mock_setup_logger, patch(
            "src.main.WaveRecorder"
        ) as mock_recorder_class, patch(
            "src.main.AudioDetector"
        ) as mock_detector_class, patch(
            "os.makedirs"
        ) as mock_makedirs:

            mocks["config"] = MagicMock()
            mocks["config"].verbose = False
            mocks["config"].language = "en"
            mocks["config"].keep_files = True
            mock_config_class.return_value = mocks["config"]

            mocks["logger"] = MagicMock()
            mock_setup_logger.return_value = mocks["logger"]

            mocks["recorder"] = MagicMock()
            mock_recorder_class.return_value = mocks["recorder"]

            mocks["detector"] = MagicMock()
            mock_detector_class.return_value = mocks["detector"]

            mocks["makedirs"] = mock_makedirs
            mocks["detector_class"] = mock_detector_class
            mocks["recorder_class"] = mock_recorder_class

            yield mocks

    def test_main_success(
        self,
        setup_mocks: dict,
    ) -> None:
        with patch("sys.argv", ["main.py"]):
            with patch.dict(os.environ, {}, clear=True):
                result = main()

                assert result == 0
                setup_mocks["detector_class"].assert_called_once()
                setup_mocks["detector"].start.assert_called_once()

    @pytest.mark.parametrize(
        "notifier_configured,expected_notifiers", [(True, 1), (False, 0)]
    )
    def test_main_with_slack_configuration(
        self,
        setup_mocks: dict,
        notifier_configured: bool,
        expected_notifiers: int,
    ) -> None:
        mock_slack = MagicMock() if notifier_configured else None

        with patch(
            "src.main.SlackNotifier.create_if_configured",
            return_value=mock_slack,
        ):
            with patch("sys.argv", ["main.py"]):
                result = main()

                assert result == 0
                setup_mocks["detector_class"].assert_called_once()

                call_args = setup_mocks["detector_class"].call_args[0]
                assert call_args[0] == setup_mocks["config"]
                assert call_args[1] == [setup_mocks["recorder"]]
                assert len(call_args[2]) == expected_notifiers

    @pytest.mark.parametrize(
        "args,expected_config,makedirs_call",
        [
            (["--threshold", "0.5"], {"threshold": 0.5}, "data/recordings"),
            (["--output-dir", "custom/output"], {}, "custom/output"),
            (["--no-keep-files"], {"keep_files": False}, "data/recordings"),
        ],
    )
    def test_main_with_command_line_args(
        self,
        setup_mocks: dict,
        args: list[str],
        expected_config: dict[str, Any],
        makedirs_call: str,
    ) -> None:
        with patch("sys.argv", ["main.py"] + args):
            result = main()

            assert result == 0

            for key, value in expected_config.items():
                assert getattr(setup_mocks["config"], key) == value

            setup_mocks["makedirs"].assert_called_once_with(
                makedirs_call, exist_ok=True
            )

            setup_mocks["detector_class"].assert_called_once()
            setup_mocks["detector"].start.assert_called_once()

            if "--no-keep-files" in args:
                setup_mocks["recorder_class"].assert_called_with(
                    output_dir=makedirs_call, temporary=True
                )


class TestMainErrorHandling:

    @pytest.fixture
    def setup_mocks(self) -> Generator[dict, None, None]:
        mocks = {}

        with patch("src.main.Config") as mock_config_class, patch(
            "src.main.setup_logger"
        ) as mock_setup_logger, patch(
            "src.main.WaveRecorder"
        ) as mock_recorder_class, patch(
            "src.main.AudioDetector"
        ) as mock_detector_class, patch(
            "os.makedirs"
        ) as mock_makedirs:

            mocks["config"] = MagicMock()
            mocks["config"].verbose = False
            mocks["config"].language = "en"
            mocks["config"].keep_files = True
            mock_config_class.return_value = mocks["config"]

            mocks["logger"] = MagicMock()
            mock_setup_logger.return_value = mocks["logger"]

            mocks["recorder"] = MagicMock()
            mock_recorder_class.return_value = mocks["recorder"]

            mocks["detector"] = MagicMock()
            mock_detector_class.return_value = mocks["detector"]

            mocks["makedirs"] = mock_makedirs
            mocks["detector_class"] = mock_detector_class

            yield mocks

    def test_main_keyboard_interrupt(
        self,
        setup_mocks: dict,
    ) -> None:
        setup_mocks["detector"].start.side_effect = KeyboardInterrupt()

        with patch("sys.argv", ["main.py"]):
            result = main()

            assert result == 0
            setup_mocks["logger"].info.assert_called_once()
            setup_mocks["detector_class"].assert_called_once()

    def test_main_exception(
        self,
        setup_mocks: dict,
    ) -> None:
        setup_mocks["detector"].start.side_effect = Exception("Test error")

        with patch("sys.argv", ["main.py"]):
            result = main()

            assert result == 1
            setup_mocks["logger"].error.assert_called_once()
            setup_mocks["detector_class"].assert_called_once()
