import json
import os
import tempfile
from typing import Any, Generator

import pytest
import yaml
from pytest import MonkeyPatch

from src.utils.config import Config


@pytest.fixture
def temp_yaml_config() -> Generator[str, None, None]:
    config_data = {
        "threshold": 0.2,
        "cooldown_seconds": 10,
        "seconds_to_record": 10,
        "keep_files": False,
        "verbose": True,
        "language": "es",
    }

    with tempfile.NamedTemporaryFile(
        suffix=".yaml", delete=False, mode="w"
    ) as temp:
        yaml.dump(config_data, temp)
        temp_path = temp.name

    yield temp_path

    os.unlink(temp_path)


@pytest.fixture
def temp_json_config() -> Generator[str, None, None]:
    config_data = {
        "threshold": 0.3,
        "cooldown_seconds": 15,
        "seconds_to_record": 15,
        "keep_files": True,
        "verbose": False,
        "language": "en",
    }

    with tempfile.NamedTemporaryFile(
        suffix=".json", delete=False, mode="w"
    ) as temp:
        json.dump(config_data, temp)
        temp_path = temp.name

    yield temp_path

    os.unlink(temp_path)


class TestConfig:
    def test_default_config(self) -> None:
        config = Config()
        expected_defaults = {
            "threshold": 0.1,
            "cooldown_seconds": 5,
            "seconds_to_record": 5,
            "pre_buffer_seconds": 2,
            "rate": 44100,
            "channels": 1,
            "format": 8,
            "chunk_size": 1024,
            "keep_files": True,
            "verbose": False,
            "language": "en",
            "timestamp_format": "%Y%m%d_%H%M%S",
            "notifier_options": {},
        }
        for attr, value in expected_defaults.items():
            assert getattr(config, attr) == value

    @pytest.mark.parametrize(
        "config_fixture,expected_values",
        [
            (
                "temp_yaml_config",
                {"threshold": 0.2, "cooldown_seconds": 10, "language": "es"},
            ),
            (
                "temp_json_config",
                {"threshold": 0.3, "cooldown_seconds": 15, "language": "en"},
            ),
        ],
    )
    def test_config_file_loading(
        self,
        request: Any,
        config_fixture: str,
        expected_values: dict[str, Any],
    ) -> None:
        config = Config(request.getfixturevalue(config_fixture))
        for key, value in expected_values.items():
            assert getattr(config, key) == value

    @pytest.mark.parametrize(
        "scenario,setup,key,expected",
        [
            (
                "found_key",
                {"mock_json": {"listening": "Escuchando ruidos fuertes..."}},
                "listening",
                "Escuchando ruidos fuertes...",
            ),
            (
                "missing_key",
                {"mock_json": {"listening": "Escuchando ruidos fuertes..."}},
                "unknown_key",
                "unknown_key",
            ),
            ("missing_file", {"raise_error": True}, "some_key", "some_key"),
        ],
    )
    def test_get_localized_text_scenarios(
        self,
        monkeypatch: MonkeyPatch,
        scenario: str,
        setup: dict[str, Any],
        key: str,
        expected: str,
    ) -> None:
        if setup.get("raise_error", False):

            def mock_open(*args: Any, **kwargs: Any) -> Any:
                raise FileNotFoundError()

            monkeypatch.setattr("builtins.open", mock_open)
        else:
            mock_translations = setup.get("mock_json", {})

            def mock_open(*args: Any, **kwargs: Any) -> Any:
                class MockFile:
                    def __enter__(self) -> Any:
                        return self

                    def __exit__(self, *args: Any, **kwargs: Any) -> None:
                        pass

                    def read(self) -> str:
                        return json.dumps(mock_translations)

                return MockFile()

            monkeypatch.setattr("builtins.open", mock_open)

        config = Config()
        config.language = "es"

        assert config.get_localized_text(key) == expected

    @pytest.mark.parametrize(
        "attribute,value",
        [
            ("threshold", 0.5),
            ("cooldown_seconds", 10),
            (
                "notifier_options",
                {"slack": {"token": "test_token", "channel": "test_channel"}},
            ),
        ],
    )
    def test_config_attributes(self, attribute: str, value: Any) -> None:
        config = Config()

        assert hasattr(config, attribute)

        original_value = getattr(config, attribute)

        setattr(config, attribute, value)

        assert getattr(config, attribute) == value

        if original_value != value:
            assert getattr(config, attribute) != original_value

    @pytest.mark.parametrize(
        "config_file,content",
        [
            (".yaml", "invalid: yaml: content: :"),
            (".json", "{invalid json content"),
            (".txt", "some content"),
            ("noextension", ""),
        ],
    )
    def test_invalid_config_files(
        self, config_file: str, content: str
    ) -> None:
        with tempfile.NamedTemporaryFile(
            suffix=config_file, delete=False, mode="w"
        ) as temp:
            temp.write(content)
            temp_path = temp.name

        try:
            config = Config(temp_path)
            assert config.threshold == 0.1
            assert config.language == "en"
        finally:
            os.unlink(temp_path)


class TestConfigBenchmarks:
    @pytest.mark.parametrize(
        "config_fixture,expected_values,file_type",
        [
            ("temp_yaml_config", {"threshold": 0.2, "language": "es"}, "YAML"),
            ("temp_json_config", {"threshold": 0.3, "language": "en"}, "JSON"),
        ],
    )
    def test_benchmark_load_config(
        self,
        request: Any,
        config_fixture: str,
        expected_values: dict[str, Any],
        file_type: str,
        benchmark: Any,
    ) -> None:
        def load_config() -> Config:
            return Config(request.getfixturevalue(config_fixture))

        benchmark.extra_info["file_type"] = file_type
        result = benchmark(load_config)

        for key, value in expected_values.items():
            assert getattr(result, key) == value

    def test_benchmark_get_localized_text(
        self,
        monkeypatch: MonkeyPatch,
        benchmark: Any,
    ) -> None:
        mock_translations = {
            "listening": "Escuchando ruidos fuertes...",
            "detected": "Ruido fuerte detectado",
            "saved": "Grabación guardada en {path}",
            "notify": "Enviando notificación...",
        }

        def mock_open(*args: Any, **kwargs: Any) -> Any:
            class MockFile:
                def __enter__(self) -> Any:
                    return self

                def __exit__(self, *args: Any, **kwargs: Any) -> None:
                    pass

                def read(self) -> str:
                    return json.dumps(mock_translations)

            return MockFile()

        monkeypatch.setattr("builtins.open", mock_open)

        config = Config()
        config.language = "es"

        keys = list(mock_translations.keys()) + ["unknown_key"]

        def get_texts() -> list[str]:
            results = []
            for key in keys:
                results.append(config.get_localized_text(key))
            return results

        benchmark.extra_info["num_keys"] = len(keys)
        results = benchmark(get_texts)

        assert len(results) == len(keys)
        assert results[0] == "Escuchando ruidos fuertes..."
        assert results[-1] == "unknown_key"
