from dataclasses import dataclass
from typing import TypeVar, dataclass_transform

T = TypeVar("T")


@dataclass_transform(
    frozen_default=False,
)
def maxo_error(cls: type[T]) -> type[T]:
    return dataclass(
        frozen=False,
    )(cls)


@maxo_error
class MaxoError(Exception): ...
