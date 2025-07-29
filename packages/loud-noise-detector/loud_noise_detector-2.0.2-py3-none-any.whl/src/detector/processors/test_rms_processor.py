import array
import math
import random
from typing import Any, Callable, Protocol

import pytest

from src.detector.processors.rms_processor import RMSProcessor
from src.utils.config import Config


class BenchmarkFixture(Protocol):
    def __call__(
        self, func: Callable[[], float], *args: Any, **kwargs: Any
    ) -> float: ...

    extra_info: dict[str, str]


@pytest.fixture
def config() -> Config:
    return Config()


@pytest.fixture
def processor(config: Config) -> RMSProcessor:
    return RMSProcessor(config)


class TestRMSProcessorFunctionality:

    def test_calculate_normal_data(self, processor: RMSProcessor) -> None:
        sample_data = array.array("h", [100, 200, 300, 400]).tobytes()

        data_array = array.array("h", sample_data)
        sum_squares = sum(sample * sample for sample in data_array)
        expected_rms = math.sqrt(sum_squares / len(data_array))
        expected_normalized_rms = expected_rms / 32767

        result = processor.calculate(sample_data)

        assert result == pytest.approx(expected_normalized_rms)

    def test_calculate_zero_data(self, processor: RMSProcessor) -> None:
        sample_data = array.array("h", [0, 0, 0, 0]).tobytes()
        result = processor.calculate(sample_data)
        assert result == 0

    def test_calculate_empty_data(self, processor: RMSProcessor) -> None:
        sample_data = array.array("h", []).tobytes()

        result = processor.calculate(sample_data)

        assert result == 0


class TestRMSProcessorBenchmarks:

    def test_benchmark_rms_small_data(
        self, processor: RMSProcessor, benchmark: BenchmarkFixture
    ) -> None:
        small_data = array.array("h", [100] * 1024).tobytes()

        def run_small_data() -> float:
            return processor.calculate(small_data)

        benchmark.extra_info["data_size"] = "1024 samples (~2KB)"
        result = benchmark(run_small_data)
        assert result > 0

    def test_benchmark_rms_medium_data(
        self, processor: RMSProcessor, benchmark: BenchmarkFixture
    ) -> None:
        medium_data = array.array("h", [100] * 8192).tobytes()

        def run_medium_data() -> float:
            return processor.calculate(medium_data)

        benchmark.extra_info["data_size"] = "8192 samples (~16KB)"
        result = benchmark(run_medium_data)
        assert result > 0

    def test_benchmark_rms_large_data(
        self, processor: RMSProcessor, benchmark: BenchmarkFixture
    ) -> None:
        large_data = array.array("h", [100] * 32768).tobytes()

        def run_large_data() -> float:
            return processor.calculate(large_data)

        benchmark.extra_info["data_size"] = "32768 samples (~64KB)"
        result = benchmark(run_large_data)
        assert result > 0

    def test_benchmark_rms_varied_data(
        self, processor: RMSProcessor, benchmark: BenchmarkFixture
    ) -> None:
        varied_data = array.array(
            "h", [i % 32767 for i in range(4096)]
        ).tobytes()

        def run_varied_data() -> float:
            return processor.calculate(varied_data)

        benchmark.extra_info["data_type"] = "4096 samples with varied values"
        result = benchmark(run_varied_data)
        assert result > 0

    def test_benchmark_rms_random_data(
        self, processor: RMSProcessor, benchmark: BenchmarkFixture
    ) -> None:
        random.seed(42)
        random_data = array.array(
            "h", [random.randint(-32767, 32767) for _ in range(4096)]
        ).tobytes()

        def run_random_data() -> float:
            return processor.calculate(random_data)

        benchmark.extra_info["data_type"] = "4096 samples with random values"
        result = benchmark(run_random_data)
        assert result > 0


class TestRMSProcessor:
    @pytest.fixture
    def config(self) -> Config:
        return Config()

    def test_process_zero_data(self, processor: RMSProcessor) -> None:
        result = processor.calculate(b"\x00" * 1024)
        assert result == 0.0

    def test_process_max_data(self, processor: RMSProcessor) -> None:
        result = processor.calculate(b"\xff" * 1024)
        assert result > 0.0

    def test_process_mixed_data(self, processor: RMSProcessor) -> None:
        result = processor.calculate(b"\x80" * 512 + b"\x00" * 512)
        assert 0.0 < result < 1.0

    def test_benchmark_rms_calculation(
        self,
        processor: RMSProcessor,
        benchmark: Any,
    ) -> None:
        data = b"\x80" * 1024 * 100
        benchmark(processor.calculate, data)
