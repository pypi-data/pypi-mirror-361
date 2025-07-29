from abc import ABC

from src.notifiers.base import BaseNotifier


class TestBaseNotifier:
    def test_is_abstract(self) -> None:
        assert issubclass(BaseNotifier, ABC)

    def test_has_abstract_methods(self) -> None:
        assert hasattr(BaseNotifier, "notify")
        assert hasattr(BaseNotifier, "create_if_configured")
