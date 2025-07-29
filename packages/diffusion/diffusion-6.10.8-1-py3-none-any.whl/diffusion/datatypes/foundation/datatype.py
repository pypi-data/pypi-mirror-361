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
import io
import typing
from abc import abstractmethod, ABCMeta
from typing import Optional

T = typing.TypeVar('T')


class DataTypeMeta(ABCMeta):
    def __str__(self):
        return getattr(self, "type_name", self.__name__)

    def __int__(self):
        return getattr(self, "type_code")


class DataType(metaclass=DataTypeMeta):
    """ Generic parent class for all data types implementations. """

    def __init__(self, value: typing.Optional[typing.Any]) -> None:
        """
        Initialise the datatype value

        Args:
            value: the value to initialise the datatype with
        """
        self._value = value
        self.validate()

    type_code: int
    """ Globally unique numeric identifier for the data type. """
    type_name: str
    """ Globally unique identifier for the data type."""

    @property
    @abstractmethod
    def value(self):
        """ Current value of the instance. """

    @value.setter
    def value(self, value) -> None:
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def read_value(cls, stream: io.BytesIO) -> Optional['DataType']:
        """Read the value from a binary stream.

        Args:
            stream: Binary stream containing the serialised data.

        Returns:
            An initialised instance of the DataType.
        """
        raise NotImplementedError()  # pragma: no cover

    def validate(self) -> None:
        """Check the current value for correctness.

        Raises:
            `InvalidDataError`: If the value is invalid. By default there is no validation.
        """

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __bytes__(self) -> bytes:
        pass

    @classmethod
    def from_bytes(cls: typing.Type[T], data: bytes) -> Optional[T]:
        raise NotImplementedError()  # pragma: no cover
