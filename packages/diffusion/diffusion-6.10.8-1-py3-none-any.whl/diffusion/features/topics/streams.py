#  Copyright (c) 2022 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

"""Stream handlers for topics."""
from __future__ import annotations
import typing
from typing import Callable, Type

import structlog

if typing.TYPE_CHECKING:
    from diffusion.datatypes import DataType, AbstractDataType
    from diffusion.datatypes.foundation.abstract import Converter, A_T, A_T_Target
from diffusion.handlers import EventStreamHandler, SubHandler

LOG = structlog.get_logger()


class ValueStreamHandler(EventStreamHandler):
    """Stream handler implementation for the value streams of the given type."""

    def __init__(
        self,
        data_type: Type[AbstractDataType],
        *,
        subscribe: typing.Optional[SubHandler] = None,
        update: typing.Optional[SubHandler] = None,
        **kwargs: Callable,
    ):
        self.type: typing.Type[AbstractDataType] = data_type
        self.converter_map = {self.type: self}
        super().__init__(
            subscribe=subscribe,
            update=update,
            **kwargs
        )

    def __str__(self):
        return f"{super().__str__()} with type {self.type}"

    converter_map: typing.Dict[typing.Type[DataType], "ValueStreamHandler"]

    def get_converter(self, source_type: typing.Type[A_T]):
        existing_converter = self.converter_map.get(source_type)
        if existing_converter:
            return existing_converter
        converter = source_type.converter_to(self.type)
        if converter:

            existing_converter = ConversionHandler(source_type, converter, self)
            self.converter_map[source_type] = existing_converter
            return existing_converter
        return None


class ConversionHandler(ValueStreamHandler):
    def __init__(
        self,
        public_type: typing.Type[AbstractDataType],
        converter: Converter[A_T, A_T_Target],
        delegate: ValueStreamHandler,
    ):
        self.converter = converter
        self.delegate = delegate
        super().__init__(public_type)

    async def handle(self, event: str, **kwargs) -> typing.Any:
        converted_kwargs = {**kwargs}
        for k in {"topic_value", "old_value"} & kwargs.keys():
            try:
                converted = self.converter(kwargs[k])
                LOG.debug(f"Converted {k}:{kwargs[k]}->{self.converter}->{converted}")
                converted_kwargs.update({k: converted})
            except Exception as e:
                LOG.error(e)
                raise
        try:
            return await self.delegate.handle(event, **converted_kwargs)
        except Exception as e:
            LOG.exception(f"Failed processing ConversionHandler event {self}", exc_info=e)
            raise e

    def __str__(self):
        return f"ConversionHandler: {self.type}->{self.type}->{self.converter}->{self.delegate}"
