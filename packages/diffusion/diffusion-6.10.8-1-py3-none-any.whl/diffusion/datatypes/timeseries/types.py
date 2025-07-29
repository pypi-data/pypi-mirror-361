#  Copyright (c) 2022 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

import typing
from pydantic import StrictBool

from diffusion.datatypes.complex import ComplexDataTypesClasses, ComplexDataTypes
from diffusion.datatypes.primitives import (
    PrimitiveDataTypesClasses,
    PrimitiveDataTypes,
    RawDataTypes,
)

TimeSeriesValueTypeClasses = typing.Union[
    PrimitiveDataTypesClasses, ComplexDataTypesClasses
]
"""
Possible typing.Type values for a Time Series Value
"""

TimeSeriesValueType = typing.Union[PrimitiveDataTypes, ComplexDataTypes]
"""
Possible types for a Time Series Value
"""

RawComplexDataTypes = typing.Union[
    typing.List[typing.Any], typing.Dict[typing.Any, typing.Any]
]
"""
Types that could be JSON
"""

TimeSeriesValueTypeOrRaw = typing.Optional[typing.Union[
    TimeSeriesValueType,
    RawDataTypes,
    RawComplexDataTypes,
    StrictBool
]]
"""
Time Series Value Type parameter
"""

_TimeSeriesValueTypeOrRaw_New = typing.Union[
    TimeSeriesValueType, RawDataTypes
]
# backport shim

VT_argtype = typing.TypeVar("VT_argtype", bound=TimeSeriesValueTypeOrRaw)
"""
Time Series Value Type parameter (TypeVar)
"""

_VT_argtype_new = typing.TypeVar(
    "_VT_argtype_new", bound=typing.Union[bytes, _TimeSeriesValueTypeOrRaw_New]
)
# backport shim

VT = typing.TypeVar("VT", bound=TimeSeriesValueType)
"""
Possible types for a Time Series Value (TypeVar)
"""

VT_covariant = typing.TypeVar("VT_covariant", bound=TimeSeriesValueType, covariant=True)
"""
Possible types for a Time Series Value (TypeVar, covariant)
"""

VT_other = typing.TypeVar("VT_other", bound=TimeSeriesValueType)
"""
Possible types for a Time Series Value conversion target
"""
