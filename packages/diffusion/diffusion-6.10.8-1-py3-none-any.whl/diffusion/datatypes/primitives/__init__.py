#  Copyright (c) 2021 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

import typing

from diffusion.internal.pydantic_compat.v1 import StrictFloat, StrictInt, StrictStr, StrictBytes

from .doubledatatype import DoubleDataType
from .binarydatatype import BinaryDataType
from .int64datatype import Int64DataType
from .stringdatatype import StringDataType
from .primitivedatatype import PrimitiveDataType

try:
    from typing_extensions import TypeAlias  # type: ignore   # pragma: no cover
except ImportError:
    from typing import TypeAlias  # type: ignore  # pragma: no cover

# datatype aliases for convenience

BINARY: TypeAlias = BinaryDataType
DOUBLE: TypeAlias = DoubleDataType
INT64: TypeAlias = Int64DataType
STRING: TypeAlias = StringDataType

RawDataTypes = typing.Union[StrictFloat, StrictInt, StrictStr, StrictBytes]
"""
Raw data types that are used to populate Diffusion datatypes
"""

PrimitiveDataTypes = typing.Union[BINARY, DOUBLE, INT64, STRING]
"""
Primitive diffusion data types.
"""

PrimitiveDataTypesClasses = typing.Union[
    typing.Type[BINARY], typing.Type[DOUBLE], typing.Type[INT64], typing.Type[STRING]
]
"""
Classes of primitive Diffusion data types.
"""
