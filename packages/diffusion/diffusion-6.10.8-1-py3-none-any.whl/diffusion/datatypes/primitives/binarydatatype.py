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

from .primitivedatatype import PrimitiveDataType
from ..foundation.abstract import ValueType, RealValue, TS_T, TS_T_target, ValueType_target, \
    RealValue_target, Converter, AbstractDataType


class BinaryDataType(PrimitiveDataType[bytes]):
    """ Data type that supports arbitrary binary data. """

    type_code = 14
    type_name = "binary"

    @classmethod
    def encode(cls, value) -> bytes:
        """ Convert the value into the binary representation. """
        return value

    def to_bytes(self) -> bytes:
        return self.encode(self.value)

    @classmethod
    def decode(cls, data: bytes) -> bytes:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            Deserialised value.
        """
        return data

    def __str__(self):
        return self.value.decode()

    @classmethod
    def converter_from(
            cls: typing.Type[AbstractDataType[TS_T, ValueType, RealValue]],
            entity: typing.Type[ValueType_target],
    ) -> typing.Optional[Converter[ValueType_target, ValueType]]:
        def to_binary(input: AbstractDataType) -> typing.Optional[ValueType]:
            if input.value:
                return typing.cast(ValueType, cls(input.to_bytes()))
            return None
        return typing.cast(Converter[ValueType_target, ValueType], to_binary)

    @classmethod
    def converter_to(
            cls: typing.Type[AbstractDataType[TS_T, ValueType, RealValue]],
            entity: typing.Type[
                AbstractDataType[TS_T_target, ValueType_target, RealValue_target]
            ],
    ) -> typing.Optional[Converter[ValueType, ValueType_target]]:
        def from_binary(input: BinaryDataType) -> typing.Optional[ValueType_target]:
            if input.value:
                return typing.cast(ValueType_target, entity.from_bytes(input.value))
            return None
        return typing.cast(Converter[ValueType, ValueType_target], from_binary)
