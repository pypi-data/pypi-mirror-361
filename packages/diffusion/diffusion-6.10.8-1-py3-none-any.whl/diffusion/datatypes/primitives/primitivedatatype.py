#  Copyright (c) 2021 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

from __future__ import annotations
import typing

from diffusion.datatypes.exceptions import InvalidDataError
from diffusion.datatypes.foundation.abstract import AbstractDataType
from diffusion.features.topics.details.topic_specification import (
    TopicSpecification,
)

T = typing.TypeVar('T')
TypeTupleVar = typing.TypeVar('TypeTupleVar', bound=typing.Tuple[type, ...])


class PrimitiveDataType(
    typing.Generic[T],
    AbstractDataType[
        TopicSpecification["PrimitiveDataType"],
        "PrimitiveDataType[T]",
        typing.Optional[T]
    ],
):
    raw_types: typing.Tuple[type, ...]

    def __init__(self, value: typing.Optional[T]):
        super().__init__(value)

    _cls_map: typing.Dict[T, typing.Type[PrimitiveDataType]] = {}

    @classmethod
    def __class_getitem__(cls, item: T) -> typing.Type[PrimitiveDataType[T]]:
        result = cls._cls_map.get(item)
        if not result:

            class Derived(PrimitiveDataType):
                raw_types = item if isinstance(item, tuple) else (item,)

            result = cls._cls_map[item] = typing.cast(
                typing.Type["PrimitiveDataType[T]"], Derived
            )
        return result

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid.
        """
        if not (
            self.value is None
            or isinstance(self.value, self.raw_types)
        ):
            raise InvalidDataError(
                f"Expected {self.raw_types} but got {type(self.value).__name__}"
            )
