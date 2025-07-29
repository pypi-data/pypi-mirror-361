#  Copyright (c) 2022 - 2024 DiffusionData Ltd., All Rights Reserved.
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

import attr

from diffusion.internal.pydantic_compat.v1 import StrictInt

import diffusion.datatypes
from diffusion.datatypes.primitives import StringDataType, Int64DataType
from diffusion.datatypes.timeseries import (
    Event,
    VT,
    TimeSeriesValueType,
)
from diffusion.datatypes.timeseries.time_series_event import (
    EventType,
    Offsets,
    AuthorEncoding,
    EventTypeFactory,
    OriginalEvent,
    EditEvent,
)
from diffusion.features.timeseries.query.range_query import QueryResult
from diffusion.features.timeseries.query.range_query_parameters import StreamStructure
from diffusion.handlers import LOG
from diffusion.internal.serialisers.attrs import MarshalledModel
from diffusion.internal.serialisers.base import Serialiser
from diffusion.internal.serialisers.generic_model import (
    GenericConfig,
)
from diffusion.internal.services import ServiceValue
from diffusion.internal.utils import validate_member_arguments
from diffusion.internal.validation import StrictNonNegativeInt
from diffusion.session.exceptions import IncompatibleTopicError
from typing import Optional


@attr.s(auto_attribs=True, eq=True, hash=True, repr=True, str=True)
class RangeQueryEventData(MarshalledModel):
    tp: EventType
    data: typing.Union[Event, Offsets, AuthorEncoding]


class AuthorCodeMapping(typing.Dict[bytes, str]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rmap: typing.Dict[str, bytes] = dict()
        self.count = 0

    def extract_author_name(self, author_code: bytes) -> typing.Optional[str]:
        return self.get(author_code) or StringDataType.decode(author_code)

    def __setitem__(self, key: bytes, value: str):
        super().__setitem__(key, value)
        self.rmap[value] = key

    def encode(self, author) -> bytes:
        entry = self.rmap.get(author)
        if not entry:
            encoding = Int64DataType.encode(self.count)
            self.count += 1
            self[encoding] = author
            return encoding
        else:
            return entry


RangeQueryResult_T = typing.TypeVar("RangeQueryResult_T", bound="RangeQueryResult")

EncodingType = typing.List[typing.Tuple[EventType, ...]]


@attr.s(auto_attribs=True, eq=True, hash=True)
class RangeQueryResult(MarshalledModel):
    """
    The range query result.
    """

    events: typing.Tuple[Event, ...]
    """
    The collection of events.
    """
    selected_count: StrictNonNegativeInt
    """
    The selected count.
    """

    value_data_type: typing.Type[diffusion.datatypes.AbstractDataType] = attr.field(
        converter=diffusion.datatypes.get
    )
    """
    The value data type.
    """

    offsets: Offsets = Offsets()
    """
    The initial offsets of this range query result
    """

    def __attrs_post_init__(self):
        @validate_member_arguments
        def setup(events: typing.Iterable[Event], selected_count: StrictInt):
            self.events = tuple(events)
            self.selected_count = selected_count

        setup(self.events, self.selected_count)

    def to_query_result(
        self, tp: typing.Type[VT], stream_structure: StreamStructure
    ) -> QueryResult[VT]:
        if not self.value_data_type.validate_type(tp):
            raise IncompatibleTopicError(
                "Time series topic has an incompatible event data type: "
                f"{self.value_data_type}."
            )

        def callback(raw_event: Event[VT]) -> typing.Optional[Event[VT]]:
            converter = raw_event.converter_to(tp)
            if converter:
                return (
                    typing.cast(Event[VT], raw_event)
                    .with_value(converter(raw_event), tp)
                    .offset(self.offsets)
                )
            return None

        return QueryResult.from_events(
            self.selected_count, stream_structure, self.events, callback
        )

    def __str__(self):
        return (
            f"{type(self).__name__} event data type={self.value_data_type} "
            f"selected count={self.selected_count} event count={len(self.events)}"
        )

    class Config(MarshalledModel.Config):
        alias = "range-query-result"

        @classmethod
        def attr_mappings_all(cls, modelcls) -> typing.Dict[str, typing.Any]:
            return {
                "range-query-result": {
                    "range-query-result.data-type-name": "value_data_type",
                    "range-query-result.selected-count": "selected_count",
                    "range-query-result.selected-events": "events",
                }
            }

        @classmethod
        def _as_service_value(
            cls, item: RangeQueryResult, serialiser: Optional[Serialiser] = None
        ) -> ServiceValue:
            return super().as_service_value(item, serialiser)

        @classmethod
        def as_service_value(
            cls: typing.Type[GenericConfig[RangeQueryResult_T]],
            item: RangeQueryResult_T,
            serialiser: Optional[Serialiser] = None,
        ) -> ServiceValue:
            # noinspection PyProtectedMember
            result = RangeQueryResult.Config._as_service_value(item, serialiser)
            offsets: EncodingType = [
                (
                    EventType.METADATA_OFFSETS,
                    *item.offsets.Config.as_tuple(item.offsets),
                )
            ]
            author_encodings = AuthorCodeMapping()
            try:
                real_events: EncodingType = [
                    (
                        EventType.from_type(
                            typing.cast(
                                typing.Type[typing.Union[OriginalEvent, EditEvent]],
                                type(x),
                            )
                        ),
                        *RangeQueryResult.Config.as_range_query_tuple(
                            type(item),
                            typing.cast(typing.Union[OriginalEvent, EditEvent], x),
                            author_encodings,
                            serialiser,
                        ),
                    )
                    for x in item.events
                ]
            except Exception as e:  # pragma: no cover
                LOG.error(f"Got exception {e}")
                raise
            author_encoding: EncodingType = [
                (
                    EventType.AUTHOR_ENCODING,
                    *AuthorEncoding.Config.as_tuple(
                        AuthorEncoding(author_code=author_code, author=author)
                    ),
                )
                for author_code, author in author_encodings.items()
            ]
            result["range-query-result.selected-events"] = list(
                map(lambda x: [x], (author_encoding + offsets + real_events))
            )
            return result

        @classmethod
        def as_range_query_tuple(
            cls,
            modelcls: typing.Type[RangeQueryResult],
            event: typing.Union[OriginalEvent, EditEvent],
            author_encodings: AuthorCodeMapping,
            serialiser: Optional[Serialiser] = None,
        ):
            serialiser = cls.check_serialiser(serialiser)
            if event.metadata:
                author: bytes = author_encodings.encode(event.metadata.author)
                event = event.copy(
                    update={"metadata": event.metadata.copy(update={"author": author})}
                )
            if event.original_event:
                orig_author: bytes = author_encodings.encode(event.original_event.author)
                event = event.copy(
                    update={
                        "original_event": event.original_event.copy(
                            update={"author": orig_author}
                        )
                    }
                )

            selected_events_serialiser = cls.get_model_to_serialiser_mapping(
                modelcls, serialiser
            ).get("events")
            assert selected_events_serialiser is not None
            result = cls.entry_from_list_of_choices_as_tuple(event, selected_events_serialiser)
            return result

    @classmethod
    def from_fields(
        cls: typing.Type[RangeQueryResult_T],
        events: typing.List[typing.Any],
        value_data_type: typing.Type[TimeSeriesValueType],
        **kwargs,
    ) -> RangeQueryResult_T:
        author_mapping_global = AuthorCodeMapping()
        offsets: Offsets = Offsets()

        def process_author_encoding(tp: typing.Tuple):
            encoding = AuthorEncoding.from_tuple(tp)
            author_mapping_global[encoding.author_code] = encoding.author
            return []

        def process_offset(tp: typing.Tuple):
            nonlocal offsets
            offsets = Offsets.from_tuple(tp)
            return []

        def process_event(cls: typing.Type[Event], tp: typing.Tuple, author_mapping):
            fields = {**cls.Config.fields_from_tuple(cls, tp)}
            original_author_code = fields.pop("original_author_code")
            edit_author_code = fields.pop("edit_author_code", None)
            if edit_author_code is not None:
                fields["edit_author"] = author_mapping.extract_author_name(edit_author_code)
            return [
                cls.from_fields(
                    original_author=author_mapping.extract_author_name(original_author_code),
                    **fields,
                )
            ]

        processed_events: typing.List[Event] = []
        for raw_event in events:
            event = raw_event[0]
            ev_code = EventType(event[0])
            mapping = {
                EventType.METADATA_OFFSETS: process_offset,
                EventType.AUTHOR_ENCODING: process_author_encoding,
            }
            action = mapping.get(
                ev_code,
                lambda x: process_event(
                    EventTypeFactory.of(ev_code.get_type(), value_data_type),
                    x,
                    author_mapping_global,
                ),
            )
            processed_events.extend(action(event[1:]))
        return cls(
            events=tuple(processed_events),
            offsets=offsets,
            value_data_type=value_data_type,
            **kwargs,
        )
