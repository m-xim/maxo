import pytest

from maxo.types.base import MaxoType


def test_facade_property_cannot_become_field_default() -> None:
    class Facade:
        @property
        def chat_id(self) -> int:
            return 0

    with pytest.raises(TypeError, match=r"Host\.chat_id .* Facade\.chat_id"):

        class Host(MaxoType, Facade):
            chat_id: int
