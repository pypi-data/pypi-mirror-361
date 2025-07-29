from __future__ import annotations

import typing
from typing import Optional, Union

from diffusion.datatypes.exceptions import InvalidDataError
from diffusion.datatypes.foundation.abstract import (
    AbstractDataType,
    Converter,
    ValueType_target,
    ValueType,
    TS_T,
)

from diffusion.features.topics.details.topic_specification import (
    TopicSpecification,
)

JsonTypes = Union[dict, list, str, int, float]


class JsonDataType(
    AbstractDataType[
        TopicSpecification["JsonDataType"],
        "JsonDataType",
        JsonTypes
    ]
):
    """ JSON data type implementation. """

    type_code = 15
    type_name = "json"
    raw_types = JsonTypes.__args__  # type: ignore

    def __init__(self, value: Optional[JsonTypes]) -> None:
        super().__init__(value)

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid.
        """

        if not self.validate_raw_type(type(self.value)):
            raw_types = (t.__name__ for t in self.raw_types if t not in (None, type(None)))
            raise InvalidDataError(
                "The value must be either None, or one of the following types:"
                f" {', '.join(raw_types)};"
                f" got {type(self.value).__name__} instead."
            )

    @classmethod
    def converter_from(
        cls: typing.Type[AbstractDataType[TS_T, ValueType, JsonTypes]],
        entity: typing.Type[ValueType_target],
    ) -> typing.Optional[Converter[ValueType_target, ValueType]]:
        if cls.validate_type(typing.cast(typing.Type[AbstractDataType], entity)):

            def converter(
                value: typing.Optional[ValueType_target],
            ) -> typing.Optional[ValueType]:
                raw_value = (
                    cls(typing.cast(AbstractDataType, value).value) if value else None
                )
                return typing.cast(typing.Optional[ValueType], raw_value)

            return converter
        return None
