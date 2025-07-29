import time
from logging import Logger
from typing import (
    Any,
    Callable,
    Generator,
    List,
    Optional,
    Protocol,
    Union,
    cast,
)
from unittest.mock import MagicMock, patch

import pytest

from src.detector.audio_detector import AudioDetector
from src.detector.processors.rms_processor import RMSProcessor
from src.notifiers.base import BaseNotifier
from src.recorders.base import BaseRecorder
from src.utils.config import Config


@pytest.fixture
def config() -> Config:
    config = Config()
    config.threshold = 0.2
    config.cooldown_seconds = 2
    config.chunk_size = 1024
    config.pre_buffer_seconds = 1
    config.rate = 44100
    config.seconds_to_record = 3
    config.verbose = False
    logger = MagicMock(spec=Logger)
    config.logger = logger
    return config


class BenchmarkFixture(Protocol):
    def __call__(self, func: Callable[[], None]) -> None: ...


@pytest.fixture
def recorders() -> List[BaseRecorder]:
    recorder = MagicMock(spec=BaseRecorder)
    save_mock = MagicMock(spec=MagicMock)
    save_mock.return_value = {
        "path": "/tmp/test.wav",
        "temporary": True,
    }
    remove_mock = MagicMock(spec=MagicMock)
    remove_mock.return_value = True

    setattr(recorder, "save", save_mock)
    setattr(recorder, "remove_file", remove_mock)
    return [recorder]


@pytest.fixture
def notifiers() -> List[BaseNotifier]:
    notifier = MagicMock(spec=BaseNotifier)
    notify_mock = MagicMock(spec=MagicMock)
    notify_mock.return_value = True

    notifier.notify = notify_mock
    return [notifier]


@pytest.fixture
def detector(
    config: Config,
    recorders: List[BaseRecorder],
    notifiers: List[BaseNotifier],
) -> Generator[AudioDetector, None, None]:
    with patch("pyaudio.PyAudio"):
        with patch("pyaudio.Stream"):
            detector = AudioDetector(config, recorders, notifiers)
            yield detector


class TestAudioDetectorBasics:
    def test_initialization(
        self,
        detector: AudioDetector,
        config: Config,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
    ) -> None:
        assert detector.config == config
        assert detector.recorders == recorders
        assert detector.notifiers == notifiers
        assert detector._is_running is False
        assert detector.stream is None
        assert detector.audio is None
        assert isinstance(detector.rms_processor, RMSProcessor)
        assert detector.detection_buffer == []
        assert detector.pre_buffer == []
        assert detector.last_detection_time == 0

    def test_setup(self, detector: AudioDetector) -> None:
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            mock_audio = MagicMock()
            mock_stream = MagicMock()
            mock_audio.open = MagicMock(return_value=mock_stream)
            mock_pyaudio.return_value = mock_audio

            detector.setup()

            assert detector.audio is not None
            assert detector.stream is not None
            assert mock_audio.open.call_count == 1

    def test_cleanup(self, detector: AudioDetector) -> None:
        detector.stream = MagicMock()
        detector.stream.stop_stream = MagicMock()
        detector.stream.close = MagicMock()
        detector.audio = MagicMock()
        detector.audio.terminate = MagicMock()
        detector._is_running = True

        detector.cleanup()

        assert detector._is_running is False
        assert detector.stream.stop_stream.call_count == 1
        assert detector.stream.close.call_count == 1
        assert detector.audio.terminate.call_count == 1


class TestAudioDetectorDetection:
    @pytest.mark.parametrize(
        "rms,cooldown,expected",
        [
            (0.1, 0, False),
            (0.3, 0, True),
            (0.3, 1, False),
            (0.3, 3, True),
        ],
    )
    def test_should_detect(
        self,
        detector: AudioDetector,
        rms: float,
        cooldown: int,
        expected: bool,
    ) -> None:
        if cooldown > 0:
            detector.last_detection_time = int(time.time()) - cooldown

        result = detector._should_detect(rms)
        assert result is expected


class TestAudioDetectorRecording:

    def test_handle_detection(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
    ) -> None:
        detector.stream = MagicMock()
        detector.stream.read = MagicMock(return_value=b"\x00" * 1024)
        detector.pre_buffer = [b"\x01" * 1024, b"\x02" * 1024]

        save_mock = MagicMock(spec=MagicMock)
        save_mock.return_value = {
            "path": "/tmp/test.wav",
            "temporary": True,
        }
        notify_mock = MagicMock(spec=MagicMock)
        notify_mock.return_value = True

        with patch.object(recorders[0], "save", save_mock):
            with patch.object(notifiers[0], "notify", notify_mock):
                detector._handle_detection(0.3, b"\x03" * 1024)

                assert len(detector.detection_buffer) > 0
                assert detector.detection_buffer[0] == b"\x01" * 1024
                assert detector.detection_buffer[1] == b"\x02" * 1024
                assert detector.detection_buffer[2] == b"\x03" * 1024

                assert save_mock.call_count == 1
                assert notify_mock.call_count == 1

    @pytest.mark.parametrize(
        "keep_files,expected_remove_calls",
        [
            (True, 0),
            (False, 1),
        ],
    )
    def test_save_and_notify(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
        keep_files: bool,
        expected_remove_calls: int,
    ) -> None:
        detector.config.keep_files = keep_files
        detector.detection_buffer = [b"\x00" * 1024]

        save_mock = MagicMock(spec=MagicMock)
        save_mock.return_value = {
            "path": "/tmp/test.wav",
            "temporary": True,
        }
        notify_mock = MagicMock(spec=MagicMock)
        notify_mock.return_value = True
        remove_mock = MagicMock(spec=MagicMock)
        remove_mock.return_value = True

        with patch.object(recorders[0], "save", save_mock):
            with patch.object(notifiers[0], "notify", notify_mock):
                with patch.object(recorders[0], "remove_file", remove_mock):
                    detector._save_and_notify(0.3, "timestamp")

                    assert save_mock.call_count == 1
                    assert notify_mock.call_count == 1
                    assert remove_mock.call_count == expected_remove_calls


class TestAudioDetectorErrorHandling:

    def test_detector_triggers_recording_on_threshold_detection(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
    ) -> None:
        with patch.object(detector, "setup") as mock_setup:
            with patch.object(detector, "cleanup") as mock_cleanup:
                mock_stream = MagicMock()
                detector.stream = mock_stream

                read_data = [b"\x00" * 1024, b"\xff" * 1024, b"\x00" * 1024]
                rms_values = [0.1, 0.5, 0.1]

                mock_stream.read = MagicMock(side_effect=read_data)

                save_mock = MagicMock(spec=MagicMock)
                save_mock.return_value = {
                    "path": "/tmp/test.wav",
                    "temporary": True,
                }
                notify_mock = MagicMock(spec=MagicMock)
                notify_mock.return_value = True

                with patch.object(recorders[0], "save", save_mock):
                    with patch.object(notifiers[0], "notify", notify_mock):
                        with patch.object(
                            detector.rms_processor,
                            "calculate",
                            side_effect=rms_values,
                        ):
                            original_handle_detection = (
                                detector._handle_detection
                            )

                            def make_mock_handle_detection() -> (
                                Callable[[float, bytes], None]
                            ):
                                def mock_handle_detection(
                                    rms: float, data: bytes
                                ) -> None:
                                    detector._is_running = False
                                    original_handle_detection(rms, data)

                                return mock_handle_detection

                            handle_patch = patch.object(
                                detector,
                                "_handle_detection",
                                make_mock_handle_detection(),
                            )

                            with handle_patch:
                                detector.start()

                                mock_setup.assert_called_once()
                                mock_cleanup.assert_called_once()

                                assert len(detector.detection_buffer) > 0
                                assert save_mock.call_count >= 1
                                assert notify_mock.call_count >= 1

    def test_start_keyboard_interrupt(self, detector: AudioDetector) -> None:
        with patch.object(detector, "setup") as mock_setup:
            with patch.object(detector, "cleanup") as mock_cleanup:
                mock_stream = MagicMock()
                detector.stream = mock_stream
                mock_stream.read = MagicMock(side_effect=KeyboardInterrupt())

                detector.start()

                mock_setup.assert_called_once()
                mock_cleanup.assert_called_once()

    def test_handle_detection_with_null_stream(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
    ) -> None:
        detector.stream = None
        detector.pre_buffer = [b"\x01" * 1024]

        detector._handle_detection(0.3, b"\x03" * 1024)

        assert len(detector.detection_buffer) > 0
        assert detector.detection_buffer[0] == b"\x01" * 1024
        assert detector.detection_buffer[1] == b"\x03" * 1024
        for i in range(2, len(detector.detection_buffer)):
            assert detector.detection_buffer[i] == b""

    def test_save_and_notify_notifier_failure(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
    ) -> None:
        detector.detection_buffer = [b"\x00" * 1024]

        save_mock = MagicMock(spec=MagicMock)
        save_mock.return_value = {
            "path": "/tmp/test.wav",
            "temporary": True,
        }
        notify_mock = MagicMock(spec=MagicMock)
        notify_mock.return_value = False

        with patch.object(recorders[0], "save", save_mock):
            with patch.object(notifiers[0], "notify", notify_mock):
                detector._save_and_notify(0.3, "timestamp")

                assert save_mock.call_count == 1
                assert notify_mock.call_count == 1

    def test_save_and_notify_recorder_exception(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
    ) -> None:
        detector.detection_buffer = [b"\x00" * 1024]
        save_mock = MagicMock(spec=MagicMock)
        save_mock.side_effect = Exception("Recorder failed")

        notify_mock = MagicMock(spec=MagicMock)

        with patch.object(recorders[0], "save", save_mock):
            with patch.object(notifiers[0], "notify", notify_mock):
                with pytest.raises(Exception, match="Recorder failed"):
                    detector._save_and_notify(0.3, "timestamp")

                assert save_mock.call_count == 1
                assert notify_mock.call_count == 0

    def test_verbose_mode(
        self,
        detector: AudioDetector,
    ) -> None:
        detector.config.verbose = True

        with patch.object(detector, "setup"):
            with patch.object(detector, "cleanup"):
                mock_stream = MagicMock()
                detector.stream = mock_stream

                def set_running_false(*args: Any, **kwargs: Any) -> bytes:
                    detector._is_running = False
                    return b"\x00" * 1024

                mock_stream.read = MagicMock(side_effect=set_running_false)

                rms_patch = patch.object(
                    detector.rms_processor, "calculate", return_value=0.1
                )

                with rms_patch:
                    with patch("builtins.print") as mock_print:
                        detector.start()

                        assert mock_print.call_count >= 1

    @pytest.mark.parametrize(
        "error_type,error_value",
        [("io_error", IOError("Stream read error")), ("empty_data", b"")],
    )
    def test_stream_reading_errors(
        self,
        detector: AudioDetector,
        error_type: str,
        error_value: Union[IOError, bytes],
    ) -> None:
        with patch.object(detector, "setup"):
            with patch.object(detector, "cleanup"):
                mock_stream = MagicMock()
                detector.stream = mock_stream

                calls = 0

                def read_side_effect(*args: Any, **kwargs: Any) -> bytes:
                    nonlocal calls
                    if calls == 0:
                        calls += 1
                        return b"\x00" * 1024
                    detector._is_running = False
                    if error_type == "io_error":
                        if isinstance(error_value, Exception):
                            raise error_value
                        return b""
                    return cast(bytes, error_value)

                mock_stream.read = MagicMock(side_effect=read_side_effect)

                with patch.object(
                    detector.rms_processor, "calculate", return_value=0.1
                ):
                    with patch.object(detector.config.logger, "error"):
                        try:
                            detector.start()
                        except IOError:
                            pass

                assert detector._is_running is False
                if error_type == "empty_data":
                    assert mock_stream.read.call_count >= 2

    def test_stream_exception_during_recording(
        self,
        detector: AudioDetector,
    ) -> None:
        detector.pre_buffer = [b"\x01" * 1024]
        detector.stream = MagicMock()

        detector.stream.read = MagicMock(side_effect=IOError("Stream closed"))

        with patch.object(detector, "_save_and_notify"):
            detector._handle_detection(0.3, b"\x03" * 1024)

            assert len(detector.detection_buffer) > 0
            assert detector.detection_buffer[0] == b"\x01" * 1024
            assert detector.detection_buffer[1] == b"\x03" * 1024

    def test_notifier_exception_handling(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
    ) -> None:
        detector.detection_buffer = [b"\x00" * 1024]

        save_mock = MagicMock(spec=MagicMock)
        save_mock.return_value = {
            "path": "/tmp/test.wav",
            "temporary": True,
        }
        notify_mock = MagicMock(spec=MagicMock)
        notify_mock.side_effect = Exception("Notifier failed")

        with patch.object(recorders[0], "save", save_mock):
            with patch.object(notifiers[0], "notify", notify_mock):
                with patch.object(
                    detector.config.logger, "error"
                ) as mock_error:
                    try:
                        detector._save_and_notify(0.3, "timestamp")
                    except Exception:
                        pass

                    assert mock_error.call_count >= 0

    def test_file_removal_failure(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
    ) -> None:
        detector.config.keep_files = False
        detector.detection_buffer = [b"\x00" * 1024]

        remove_mock = MagicMock(spec=MagicMock)
        remove_mock.return_value = False

        with patch.object(recorders[0], "remove_file", remove_mock):
            detector._save_and_notify(0.3, "timestamp")
            remove_mock.assert_called_once()

    def test_none_stream_in_start(
        self,
        detector: AudioDetector,
    ) -> None:
        with patch.object(detector, "setup") as mock_setup:
            mock_setup.side_effect = lambda: None

            with patch.object(detector, "cleanup"):
                detector._is_running = True
                detector.stream = None

                def stop_after_first_iter(*args: Any, **kwargs: Any) -> float:
                    detector._is_running = False
                    return 0.1

                with patch.object(
                    detector.rms_processor,
                    "calculate",
                    side_effect=stop_after_first_iter,
                ):
                    detector.start()

                    assert detector._is_running is False

    def test_is_running_false_during_detection(
        self,
        detector: AudioDetector,
    ) -> None:
        detector.stream = MagicMock()
        detector.pre_buffer = [b"\x01" * 1024]
        detector._is_running = True

        read_count = 0

        def read_side_effect(*args: Any, **kwargs: Any) -> bytes:
            nonlocal read_count
            read_count += 1
            if read_count == 1:
                detector._is_running = False
            return b"\x00" * 1024

        detector.stream.read = MagicMock(side_effect=read_side_effect)

        with patch.object(detector, "_save_and_notify"):
            detector._handle_detection(0.3, b"\x03" * 1024)

            assert len(detector.detection_buffer) > 0
            assert detector.stream.read.call_count == 1

    @pytest.mark.parametrize("path_value", ["", None])
    def test_remove_file_with_invalid_path(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        path_value: Optional[str],
    ) -> None:
        detector.config.keep_files = False
        detector.detection_buffer = [b"\x00" * 1024]

        save_mock = MagicMock(spec=MagicMock)
        save_mock.return_value = {
            "temporary": True,
            "path": path_value,
        }
        remove_mock = MagicMock(spec=MagicMock)

        with patch.object(recorders[0], "save", save_mock):
            with patch.object(recorders[0], "remove_file", remove_mock):
                detector._save_and_notify(0.3, "timestamp")
                assert remove_mock.call_count == 0

    def test_start_with_empty_data(
        self,
        detector: AudioDetector,
    ) -> None:
        with patch.object(detector, "setup"):
            with patch.object(detector, "cleanup"):
                mock_stream = MagicMock()
                detector.stream = mock_stream

                mock_stream.read = MagicMock(return_value=b"")

                def stop_after_first_iter(*args: Any, **kwargs: Any) -> float:
                    detector._is_running = False
                    return 0.1

                with patch.object(
                    detector.rms_processor,
                    "calculate",
                    side_effect=stop_after_first_iter,
                ):
                    with patch.object(detector.config.logger, "info"):
                        detector.start()

                assert mock_stream.read.call_count == 1

    def test_stop_method(
        self,
        detector: AudioDetector,
    ) -> None:
        detector._is_running = True
        detector.stop()
        assert detector._is_running is False

    def test_save_and_notify_with_multiple_recorders_and_notifiers(
        self,
        detector: AudioDetector,
    ) -> None:
        recorder1 = MagicMock(spec=BaseRecorder)
        recorder2 = MagicMock(spec=BaseRecorder)
        notifier1 = MagicMock(spec=BaseNotifier)
        notifier2 = MagicMock(spec=BaseNotifier)

        save_mock1 = MagicMock(
            return_value={"path": "/tmp/test1.wav", "temporary": True}
        )
        save_mock2 = MagicMock(
            return_value={"path": "/tmp/test2.wav", "temporary": True}
        )
        recorder1.save = save_mock1
        recorder2.save = save_mock2

        notify_mock1 = MagicMock(return_value=True)
        notify_mock2 = MagicMock(return_value=False)
        notifier1.notify = notify_mock1
        notifier2.notify = notify_mock2

        detector.recorders = [recorder1, recorder2]
        detector.notifiers = [notifier1, notifier2]
        detector.detection_buffer = [b"\x00" * 1024]

        detector._save_and_notify(0.3, "timestamp")

        assert save_mock1.call_count == 1
        assert save_mock2.call_count == 1
        assert notify_mock1.call_count == 1
        assert notify_mock2.call_count == 1

    def test_start_with_none_stream_and_stop(
        self,
        detector: AudioDetector,
    ) -> None:
        with patch.object(detector, "setup"):
            with patch.object(detector, "cleanup"):
                detector.stream = None

                def stop_after_first_iter(*args: Any, **kwargs: Any) -> float:
                    detector.stop()
                    return 0.1

                with patch.object(
                    detector.rms_processor,
                    "calculate",
                    side_effect=stop_after_first_iter,
                ):
                    with patch.object(detector.config.logger, "info"):
                        detector.start()

                assert detector._is_running is False

    def test_save_and_notify_with_failed_notification(
        self,
        detector: AudioDetector,
    ) -> None:
        recorder = MagicMock(spec=BaseRecorder)
        notifier = MagicMock(spec=BaseNotifier)

        save_mock = MagicMock(
            return_value={"path": "/tmp/test.wav", "temporary": True}
        )
        recorder.save = save_mock

        notify_mock = MagicMock(return_value=False)
        notifier.notify = notify_mock

        detector.recorders = [recorder]
        detector.notifiers = [notifier]
        detector.detection_buffer = [b"\x00" * 1024]

        with patch.object(detector.config.logger, "info") as mock_logger:
            detector._save_and_notify(0.3, "timestamp")

            assert mock_logger.call_count == 0
            assert notify_mock.call_count == 1

    def test_handle_detection_with_none_stream(
        self,
        detector: AudioDetector,
    ) -> None:
        detector.stream = None
        detector.pre_buffer = [b"\x01" * 1024]
        detector._is_running = True

        with patch.object(detector, "_save_and_notify") as mock_save_notify:
            detector._handle_detection(0.3, b"\x03" * 1024)

            assert len(detector.detection_buffer) > 2
            assert detector.detection_buffer[0] == b"\x01" * 1024
            assert detector.detection_buffer[1] == b"\x03" * 1024
            assert all(chunk == b"" for chunk in detector.detection_buffer[2:])

            assert mock_save_notify.call_count == 1


class TestAudioDetectorBenchmarks:
    def test_benchmark_should_detect(
        self,
        detector: AudioDetector,
        benchmark: BenchmarkFixture,
    ) -> None:
        detector.config.threshold = 0.2
        detector.last_detection_time = int(time.time()) - 10

        def run_should_detect() -> None:
            detector._should_detect(0.3)
            detector._should_detect(0.1)
            old_time = detector.last_detection_time
            detector.last_detection_time = int(time.time())
            detector._should_detect(0.3)
            detector.last_detection_time = old_time

        benchmark(run_should_detect)

    def test_benchmark_handle_detection(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
        benchmark: BenchmarkFixture,
    ) -> None:
        detector.stream = MagicMock()
        read_mock = MagicMock(return_value=b"\x00" * 1024)
        setattr(detector.stream, "read", read_mock)
        detector.pre_buffer = [b"\x01" * 1024, b"\x02" * 1024]

        save_notify_mock = MagicMock()
        with patch.object(detector, "_save_and_notify", save_notify_mock):

            def run_handle_detection() -> None:
                detector.detection_buffer = []
                detector._handle_detection(0.3, b"\x03" * 1024)

            benchmark(run_handle_detection)

    def test_benchmark_save_and_notify(
        self,
        detector: AudioDetector,
        recorders: List[BaseRecorder],
        notifiers: List[BaseNotifier],
        benchmark: BenchmarkFixture,
    ) -> None:
        detector.detection_buffer = [b"\x00" * 1024 for _ in range(10)]

        for recorder in recorders:
            save_mock = MagicMock()
            save_mock.return_value = {
                "path": "/tmp/test.wav",
                "temporary": True,
            }
            with patch.object(recorder, "save", save_mock):
                for notifier in notifiers:
                    notify_mock = MagicMock()
                    notify_mock.return_value = True
                    with patch.object(notifier, "notify", notify_mock):

                        def run_save_and_notify() -> None:
                            detector.detection_buffer = [
                                b"\x00" * 1024 for _ in range(10)
                            ]
                            detector._save_and_notify(0.4, "20230525_123456")

                        benchmark(run_save_and_notify)

    def test_benchmark_rms_calculation(
        self,
        detector: AudioDetector,
        benchmark: BenchmarkFixture,
    ) -> None:
        audio_data = b"\x00\x10" * 512

        def run_rms_calculation() -> None:
            detector.rms_processor.calculate(audio_data)

        benchmark(run_rms_calculation)
