#  Copyright (c) 2021 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

""" Core definitions of data types. """
from __future__ import annotations

import typing
from io import BytesIO
from typing import Any, Optional

try:
    from typing import Protocol  # type: ignore  # pragma: no cover
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # pragma: no cover

from diffusion.datatypes.exceptions import InvalidDataError
from diffusion.internal.encoder import Encoder, DefaultEncoder
from diffusion.internal.encoded_data import Int64

from .datatype import DataType

if typing.TYPE_CHECKING:
    from diffusion.features.topics.details.topic_specification import TopicSpecification

T = typing.TypeVar("T", bound=DataType, covariant=True)
A_T = typing.TypeVar("A_T", bound="AbstractDataType")
A_T_Target = typing.TypeVar("A_T_Target", bound="AbstractDataType")


TS_T = typing.TypeVar("TS_T", bound="TopicSpecification")
TS_T_target = typing.TypeVar("TS_T_target", bound="TopicSpecification")


class ValueTypeProtocol(Protocol):
    @classmethod
    def validate_type(cls, source_type: typing.Type[AbstractDataType]) -> bool:
        pass  # pragma: no cover


ValueType = typing.TypeVar("ValueType", bound=ValueTypeProtocol, contravariant=True)
ValueType_target = typing.TypeVar(
    "ValueType_target", bound=ValueTypeProtocol, covariant=True
)


class Converter(Protocol[ValueType, ValueType_target]):
    def __call__(self, value: ValueType) -> typing.Optional[ValueType_target]:
        pass  # pragma: no cover


class Identity(object):
    def __call__(self, value: ValueType) -> typing.Optional[ValueType]:
        return value


IDENTITY = Identity()


class WithProperties(typing.Generic[TS_T, ValueType]):
    def __get__(
        self,
        instance: typing.Optional[AbstractDataType[TS_T, ValueType, RealValue]],
        owner: typing.Type[AbstractDataType[TS_T, ValueType, RealValue]],
    ) -> typing.Type[TS_T]:
        """
        Return a TopicSpecification class prefilled with `owner`

        Args:
            instance: the instance on which this is called
            owner: the class on which this is called

        Returns:
            Return a TopicSpecification class prefilled with `owner`
        """
        from diffusion.features.topics.details.topic_specification import TopicSpecification
        return typing.cast(typing.Type[TS_T], TopicSpecification.new_topic_specification(owner))


RealValue = typing.TypeVar("RealValue")
RealValue_target = typing.TypeVar("RealValue_target")


class AbstractDataType(DataType, typing.Generic[TS_T, ValueType, RealValue]):
    encoder: Encoder = DefaultEncoder()
    raw_types: typing.Tuple[typing.Type, ...]

    def __init__(self, value: Optional[Any]) -> None:
        super().__init__(value)

    def write_value(self, stream: BytesIO) -> BytesIO:
        """Write the value into a binary stream.

        Args:
            stream: Binary stream to serialise the value into.
        """
        stream.write(self.encode(self.value))
        return stream

    @classmethod
    def codec_read_bytes(cls: typing.Type[T], stream: BytesIO) -> typing.Optional[T]:
        length = Int64.read(stream).value
        return cls.from_bytes(stream.read(length))

    def codec_write_bytes(self, stream: BytesIO) -> BytesIO:
        payload = self.to_bytes()
        Int64(len(payload)).write(stream)
        stream.write(payload)
        return stream

    def to_bytes(self) -> bytes:
        """Convert the value into the binary representation.

        Convenience method, not to be overridden"""

        return self.encoder.dumps(self.value)

    @classmethod
    def read_value(cls, stream: BytesIO) -> Optional[AbstractDataType]:
        """Read the value from a binary stream.

        Args:
            stream: Binary stream containing the serialised data.

        Returns:
            An initialised instance of the DataType.
        """
        return cls.from_bytes(stream.read())

    @property
    def value(self: AbstractDataType[TS_T, ValueType, RealValue]) -> typing.Optional[RealValue]:
        """ Current value of the instance. """
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        if isinstance(value, bytes):
            value = self.decode(value)
        self._value = value

    @classmethod
    def from_bytes(
        cls: typing.Type[A_T], data: bytes
    ) -> Optional[A_T]:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            An initialised instance of the DataType.
        """
        value = cls.decode(data)
        if value is None:
            return None
        return cls(value)

    @property
    def serialised_value(self) -> dict:
        """Return the sequence of values ready to be serialised.

        It is assumed that the serialisation will use the
        `serialised-value` serialiser.
        """
        return {"data-type-name": self.type_name, "bytes": self.encode(self.value)}

    @classmethod
    def encode(cls, value: Any) -> bytes:
        """Convert a value into the corresponding binary representation.

        Args:
            value:
                Native value to be serialised

        Returns:
            Serialised binary representation of the value.
        """
        return cls.encoder.dumps(value)

    @classmethod
    def decode(cls: typing.Type[A_T], data: bytes) -> Any:
        """Convert a binary representation into the corresponding value.

        Args:
            data: Serialised binary representation of the value.

        Returns:
            Deserialised value.
        """
        with BytesIO(data) as fp:
            value = cls.encoder.load(fp)
            if len(fp.read(1)) > 0:
                raise InvalidDataError("Excess CBOR data")
        return value

    def set_from_bytes(self, data: bytes) -> None:
        """ Convert bytes and set the corresponding value on the instance. """
        self.value = self.decode(data)

    def __eq__(self, other) -> bool:
        return (type(self) is type(other) and self.value == other.value) or (
            self.value == other
        )

    def __repr__(self) -> str:
        return f"<{type(self).__name__} value={self.value}>"

    def __str__(self) -> str:
        return str(self.value)

    def __bytes__(self):
        return self.to_bytes()

    @classmethod
    def validate_type(cls, source_type: typing.Type[AbstractDataType]) -> bool:
        return all(cls.validate_raw_type(tp) for tp in source_type.raw_types)

    @classmethod
    def validate_raw_type(cls, source_type: type) -> bool:
        return issubclass(source_type, (*cls.raw_types, type(None)))

    @classmethod
    def converter_to(
        cls: typing.Type[AbstractDataType[TS_T, ValueType, RealValue]],
        entity: typing.Type[
            AbstractDataType[TS_T_target, ValueType_target, RealValue_target]
        ],
    ) -> typing.Optional[Converter[ValueType, ValueType_target]]:
        return entity.converter_from(typing.cast(typing.Type[ValueType], cls))

    @classmethod
    def converter_from(
        cls: typing.Type[AbstractDataType[TS_T, ValueType, RealValue]],
        entity: typing.Type[ValueType_target],
    ) -> typing.Optional[Converter[ValueType_target, ValueType]]:

        if cls == entity:
            return typing.cast(Converter[ValueType_target, ValueType], IDENTITY)
        return None

    with_properties: typing.ClassVar[WithProperties] = WithProperties()
    """
    A class property that returns the type of this class's appropriate TopicSpecification class,
    ready for instantiation with the relevant parameters.

    See Also:
        [WithProperties][diffusion.datatypes.foundation.abstract.WithProperties]
    """
