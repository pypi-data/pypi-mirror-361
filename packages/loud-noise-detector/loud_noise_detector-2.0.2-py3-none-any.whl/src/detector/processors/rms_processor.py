import array
import math

from src.utils.config import Config


class RMSProcessor:

    def __init__(self, config: Config) -> None:
        self.config = config

    def calculate(self, data: bytes) -> float:
        data_array = array.array("h", data)

        sum_squares = sum(sample * sample for sample in data_array)

        if sum_squares > 0 and len(data_array) > 0:
            rms = math.sqrt(sum_squares / len(data_array))
        else:
            rms = 0

        max_amplitude = 32767
        normalized_rms = rms / max_amplitude

        return normalized_rms
