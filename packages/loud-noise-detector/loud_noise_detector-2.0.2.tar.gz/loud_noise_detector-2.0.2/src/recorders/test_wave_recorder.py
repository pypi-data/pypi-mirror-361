import os
import tempfile
import wave
from typing import Any, Callable, Generator, Protocol
from unittest.mock import MagicMock

import pytest

from src.recorders.wave_recorder import WaveRecorder
from src.utils.config import Config


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def config() -> Config:
    config = Config()
    config.channels = 1
    config.rate = 44100
    config.verbose = False

    logger = MagicMock()

    logger.info = MagicMock()
    logger.error = MagicMock()
    logger.warning = MagicMock()
    logger.debug = MagicMock()
    logger.critical = MagicMock()

    config.logger = logger  # type: ignore[assignment]
    return config


@pytest.fixture
def recorder(temp_dir: str) -> WaveRecorder:
    return WaveRecorder(output_dir=temp_dir, prefix="test_", temporary=True)


@pytest.fixture
def create_test_file(temp_dir: str) -> Callable[..., str]:
    def _create_file(
        filename: str = "test_file.wav", content: bytes = b"test"
    ) -> str:
        path = os.path.join(temp_dir, filename)
        with open(path, "wb") as f:
            f.write(content)
        return path

    return _create_file


class TestWaveRecorder:
    def test_init_creates_directory(self, temp_dir: str) -> None:
        os.rmdir(temp_dir)
        assert not os.path.exists(temp_dir)

        WaveRecorder(output_dir=temp_dir)
        assert os.path.exists(temp_dir)

    @pytest.mark.parametrize(
        "verbose,expected_log_calls", [(False, 0), (True, 1)]
    )
    def test_save(
        self,
        recorder: WaveRecorder,
        config: Config,
        temp_dir: str,
        verbose: bool,
        expected_log_calls: int,
    ) -> None:
        config.verbose = verbose
        chunks = [b"\x00\x00" * 1024, b"\x01\x00" * 1024]
        timestamp = "20230525_123456"
        normalized_rms = 0.5

        info_mock = MagicMock()
        config.logger.info = info_mock  # type: ignore[assignment]

        result = recorder.save(chunks, config, timestamp, normalized_rms)

        expected_path = os.path.join(temp_dir, f"test_{timestamp}.wav")
        assert os.path.exists(expected_path)

        with wave.open(expected_path, "rb") as wf:
            assert wf.getnchannels() == config.channels
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == config.rate
            assert wf.readframes(wf.getnframes()) == b"".join(chunks)

        assert result["path"] == expected_path
        assert result["format"] == "wav"
        assert result["temporary"] is True
        assert result["timestamp"] == timestamp
        assert result["rms"] == normalized_rms

        assert info_mock.call_count == expected_log_calls

    @pytest.mark.parametrize(
        "verbose,expected_log_calls", [(False, 0), (True, 1)]
    )
    def test_remove_file(
        self,
        recorder: WaveRecorder,
        config: Config,
        create_test_file: Callable[..., str],
        verbose: bool,
        expected_log_calls: int,
    ) -> None:
        config.verbose = verbose
        test_file = create_test_file()

        info_mock = MagicMock()
        config.logger.info = info_mock  # type: ignore[assignment]

        assert os.path.exists(test_file)

        result = recorder.remove_file(test_file, config)

        assert result is True
        assert not os.path.exists(test_file)
        assert info_mock.call_count == expected_log_calls

    def test_remove_nonexistent_file(
        self,
        recorder: WaveRecorder,
        config: Config,
    ) -> None:
        result = recorder.remove_file("/nonexistent/path.wav", config)

        assert result is False

    def test_remove_file_error_verbose(
        self,
        recorder: WaveRecorder,
        config: Config,
        create_test_file: Callable[..., str],
    ) -> None:
        config.verbose = True
        test_file = create_test_file()

        error_mock = MagicMock()
        config.logger.error = error_mock  # type: ignore[assignment]

        original_remove = os.remove
        try:
            os.remove = MagicMock(
                side_effect=OSError("Simulated error")
            )  # type: ignore[assignment]

            result = recorder.remove_file(test_file, config)

            assert result is False
            assert error_mock.call_count == 1

        finally:
            os.remove = original_remove  # type: ignore[assignment]
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except:  # noqa: E722
                    pass


class BenchmarkFixture(Protocol):
    def __call__(
        self, func: Callable[[], Any], *args: Any, **kwargs: Any
    ) -> Any: ...


class TestWaveRecorderBenchmarks:
    def test_benchmark_save(
        self,
        recorder: WaveRecorder,
        config: Config,
        temp_dir: str,
        benchmark: BenchmarkFixture,
    ) -> None:
        chunks = [b"\x00\x00" * 1024, b"\x01\x00" * 1024]
        timestamp = "20230525_123456"
        normalized_rms = 0.5

        def run_save() -> dict[str, Any]:
            return recorder.save(chunks, config, timestamp, normalized_rms)

        result = benchmark(run_save)

        expected_path = os.path.join(temp_dir, f"test_{timestamp}.wav")
        assert os.path.exists(expected_path)
        assert isinstance(result, dict)
        assert result["path"] == expected_path
        assert result["format"] == "wav"

    def test_benchmark_remove_file(
        self,
        recorder: WaveRecorder,
        config: Config,
        create_test_file: Callable[..., str],
        benchmark: BenchmarkFixture,
    ) -> None:
        test_files = []
        for i in range(10):
            test_files.append(create_test_file(f"test_file_{i}.wav", b"test"))

        for test_file in test_files:
            assert os.path.exists(test_file)

        def run_remove() -> None:
            for test_file in test_files:
                if os.path.exists(test_file):
                    recorder.remove_file(test_file, config)

        benchmark(run_remove)

        for test_file in test_files:
            assert not os.path.exists(test_file)
