from abc import ABC

from src.recorders.base import BaseRecorder


class TestBaseRecorder:
    def test_is_abstract(self) -> None:
        assert issubclass(BaseRecorder, ABC)

    def test_has_abstract_methods(self) -> None:
        assert hasattr(BaseRecorder, "save")
        assert hasattr(BaseRecorder, "remove_file")
