#  Copyright (c) 2020 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

""" Diffusion data types. """

from __future__ import annotations

import sys
from inspect import isclass
from typing import cast, Mapping, Optional, Type, Union

try:
    from typing import TypeAlias  # type: ignore
except ImportError:
    from typing_extensions import TypeAlias

from . import complex, primitives
from .foundation.abstract import AbstractDataType
from diffusion.features.topics.details.topic_specification import TopicSpecification

from .foundation.datatype import DataType

from .exceptions import (
    DataTypeError,
    IncompatibleDatatypeError,
    InvalidDataError,
    UnknownDataTypeError,
)

from .timeseries import TimeSeriesDataType, TimeSeriesEventDataType

DataTypeArgument = Union[int, str, Type[DataType], TopicSpecification]

# datatype aliases for convenience
BINARY = primitives.BinaryDataType
"""
Binary datatype alias, points to
[BinaryDataType][diffusion.datatypes.primitives.BinaryDataType]
"""
DOUBLE = primitives.DoubleDataType
"""
Double datatype alias, points to
[DoubleDataType][diffusion.datatypes.primitives.DoubleDataType]
"""
INT64 = primitives.Int64DataType
"""
Int64 datatype alias, points to
[Int64DataType][diffusion.datatypes.primitives.Int64DataType]
"""
STRING = primitives.StringDataType
"""
String datatype alias, points to
[StringDataType][diffusion.datatypes.primitives.StringDataType]
"""
JSON = complex.JsonDataType
"""
Json datatype alias, points to
[JsonDataType][diffusion.datatypes.complex.JsonDataType]
"""
RECORD_V2 = complex.RecordDataType
"""
Record V2 datatype alias, points to
[RecordDataType][diffusion.datatypes.complex.RecordDataType]
"""
TIME_SERIES = TimeSeriesEventDataType
"""
TimeSeries datatype alias, points to
[TimeSeriesEventDataType][diffusion.datatypes.timeseries.TimeSeriesEventDataType]
"""
UNKNOWN = complex.UnknownDataType
"""
Unknown datatype alias, points to
[UnknownDataType][diffusion.datatypes.complex.UnknownDataType]
"""

_dt_module = sys.modules[__name__]  # this module

# index and cache the implemented data types by type codes
_indexed_data_types: Mapping[int, Type[AbstractDataType]] = {
    item.type_code: item
    for item in vars(_dt_module).values()
    if isclass(item) and issubclass(item, AbstractDataType) and hasattr(item, 'type_code')
}


def get(data_type: Optional[DataTypeArgument]) -> Type[AbstractDataType]:
    """Helper function to retrieve a datatype based on its name or a `DataTypes` value.

    Args:
        data_type: Either a string that corresponds to the `type_name` attribute
                   of a `DataType` subclass, or an integer that corresponds to the
                   `type_code` of a `DataType` subclass. It also accepts an actual
                   `DataType` subclass, which is returned unchanged.

    Raises:
        `UnknownDataTypeError`: If the corresponding data type was not found.

    Examples:
        >>> get('string')
        <class 'diffusion.datatypes.primitives.stringdatatype.StringDataType'>
        >>> get(INT64)
        <class 'diffusion.datatypes.primitives.int64datatype.Int64DataType'>
        >>> get(15)
        <class 'diffusion.datatypes.complex.jsondatatype.JsonDataType'>
    """
    if isinstance(data_type, str):
        data_type = getattr(_dt_module, data_type.strip().upper(), None)
    if isinstance(data_type, int):
        data_type = _indexed_data_types.get(data_type)
    if isinstance(data_type, TopicSpecification):
        return data_type.topic_type
    if isclass(data_type) and issubclass(data_type, DataType):  # type: ignore
        return cast(Type[AbstractDataType], data_type)
    raise UnknownDataTypeError(f"Unknown data type '{data_type}'.")
