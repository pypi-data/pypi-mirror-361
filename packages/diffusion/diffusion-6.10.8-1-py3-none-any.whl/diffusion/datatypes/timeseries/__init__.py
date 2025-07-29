#  Copyright (c) 2022 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

from __future__ import annotations

import functools

import diffusion.internal.pydantic_compat.v1 as pydantic
import stringcase  # type: ignore
import typing

try:
    from typing import Literal  # type: ignore  # pragma: no cover
except ImportError:
    from typing_extensions import Literal  # type: ignore  # pragma: no cover

from io import BytesIO

from diffusion.datatypes.foundation.abstract import (
    AbstractDataType,
    Converter,
    TS_T,
    TS_T_target,
    ValueType,
    ValueType_target,
    WithProperties, RealValue, RealValue_target,
)

import diffusion.features.topics.details.topic_specification as topic_specification
from diffusion.features.topics.details.topic_specification import (
    T, T_other, ConflationPolicy
)

from diffusion.internal.utils import validate_member_arguments

from diffusion.datatypes.timeseries.time_series_event import EventTypeFactory, Event
from diffusion.datatypes.timeseries.types import VT, TimeSeriesValueType, \
    TimeSeriesValueTypeClasses, TimeSeriesValueTypeOrRaw
from diffusion.datatypes.timeseries.time_series_event_metadata import (
    EventMetadata,
)

import diffusion.datatypes


class TopicSpecification(
    typing.Generic[T],
    topic_specification.TopicSpecification[T],
):
    """
    Time Series Topic Specification class
    """

    TIME_SERIES_EVENT_VALUE_TYPE: typing.Type[TimeSeriesValueType]
    """
    Specifies the event data type for a time series topic.
    """

    TIME_SERIES_RETAINED_RANGE: typing.Optional[str] = None
    """
    Key of the topic property that specifies the range of events retained by
    a time series topic.

    When a new event is added to the time series, older events that fall
    outside of the range are discarded.

    If the property is not specified, a time series topic will retain the ten
    most recent events.

    ## Time series range expressions

    The property value is a time series <em>range expression</em> string
    composed of one or more constraint clauses. Constraints are combined to
    provide a range of events from the end of the time series.

    ## `limit` constraint
    A limit constraint specifies the maximum number of events from the
    end of the time series.

    ## `last` constraint

    A last constraint specifies the maximum duration of events from the
    end of the time series. The duration is expressed as an integer followed
    by one of the following time units.

    - `ms` - milliseconds
    - `s` - seconds
    - `h` - hours

    If a range expression contains multiple constraints, the constraint that
    selects the smallest range is used.

    | Property value     | Meaning                                                                                    |
    |--------------------|--------------------------------------------------------------------------------------------|
    | `limit 5`          | The five most recent events                                                                |
    | `last 10s`         | All events that are no more than ten seconds older than the latest event                   |
    | `last 10s limit 5` | The five most recent events that are no more than ten seconds older than the latest event  |

    Range expressions are not case sensitive:
    ```
    limit 5 last 10s
    ```
    is equivalent to

    ```
    LIMIT 5 LAST 10S
    ```.

    Since 6.8.3
    """  # NOQA: E501
    TIME_SERIES_SUBSCRIPTION_RANGE: typing.Optional[str] = None
    """
    Key of the topic property that specifies the range of time series topic
    events to send to new subscribers.

    The property value is a time series range expression, following the
    format used for
    [TIME_SERIES_RETAINED_RANGE]
    [diffusion.datatypes.timeseries.TopicSpecification.TIME_SERIES_RETAINED_RANGE].

    If the property is not specified, new subscribers will be sent the latest
    event if delta streams are enabled and no events if delta streams are
    disabled. See the description of <em>Subscription range</em> in the
    {@link TimeSeries time series feature} documentation.

    Since 6.8.3
    """

    CONFLATION: typing.Optional[
        Literal[ConflationPolicy.OFF, ConflationPolicy.UNSUBSCRIBE]
    ] = None
    """
    TimeSeries conflation policy is restricted to the above.

    See Also:
        [diffusion.features.topics.details.topic_specification.TopicSpecification.CONFLATION][]
    """

    @property
    def topic_type(self):
        # noinspection PyProtectedMember
        return TimeSeriesDataType.of(
            typing.cast(typing.Type[T], self.TIME_SERIES_EVENT_VALUE_TYPE)
        )

    # noinspection PyUnusedLocal,PyNestedDecorators
    @pydantic.validator("TIME_SERIES_EVENT_VALUE_TYPE", pre=True)
    @classmethod
    def validate_ts(
        cls,
        field_value: typing.Type[VT],
        values: typing.Dict[str, typing.Any],
        field,
        config,
    ) -> typing.Type[VT]:
        return typing.cast(typing.Type[VT], diffusion.datatypes.get(field_value))

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def _spec_class(
            cls, tp: typing.Type[T_other]
    ) -> typing.Type[topic_specification.TopicSpecification[T_other]]:
        class Result(TopicSpecificationAuto):
            TIME_SERIES_EVENT_VALUE_TYPE: typing.Type[TimeSeriesValueType] = pydantic.Field(
                default=typing.cast(
                    typing.Type[TimeSeriesValueType],
                    typing.cast(TimeSeriesEventDataType, tp).inner_value_type(),
                )
            )

        return typing.cast(
            typing.Type[
                topic_specification.TopicSpecification[T_other]
            ],
            topic_specification.TopicSpecification._spec_class(
                Result, tp
            ),
        )


def fake_own_type() -> typing.Type[TimeSeriesValueType]:
    raise NotImplementedError()


class TopicSpecificationAuto(typing.Generic[T], TopicSpecification[T]):
    TIME_SERIES_EVENT_VALUE_TYPE: typing.Type[TimeSeriesValueType] = pydantic.Field(
        const=True, default_factory=fake_own_type
    )
    """
    Specifies the event data type for a time series topic.
    """


class TimeSeriesWithProperties(
    typing.Generic[T], WithProperties[TopicSpecification[T], Event]
):
    def __get__(
        self,
        instance: typing.Optional[
            AbstractDataType[TopicSpecification[T], ValueType, RealValue]
        ],
        owner: typing.Type[
            AbstractDataType[TopicSpecification[T], ValueType, RealValue]
        ],
    ) -> typing.Type[TopicSpecificationAuto[T]]:
        """
        Return a
        [TopicSpecification][diffusion.datatypes.timeseries.TopicSpecification]
        class prefilled with `owner`

        Args:
            instance: the instance on which this is called
            owner: the class on which this is called

        Returns:
            Return a TopicSpecification class prefilled with `owner`
        """
        return typing.cast(
            typing.Type[TopicSpecificationAuto[T]],
            TopicSpecificationAuto.new_topic_specification(
                typing.cast(typing.Type[T], owner)
            ),
        )


class TimeSeriesEventDataType(
    typing.Generic[VT],
    AbstractDataType[TopicSpecification["TimeSeriesEventDataType[VT]"], Event[VT], Event[VT]],
):
    """
    A data type for time series events
    """

    value_type: typing.Type[Event[VT]]
    type_code = 16

    _value: Event[VT]

    def __init__(self, value: Event[VT]):
        """
        Initialise a TimeSeriesEventDataType

        Args:
            value: the Event[VT] to set as the value of this instance
        """

        super(TimeSeriesEventDataType, self).__init__(value)

    def write_value(self, stream: BytesIO) -> BytesIO:
        if self.value is None:
            raise ValueError(f"{repr(self)}.value is None, cannot write")
        return self.value.write_value(stream)

    def to_bytes(self) -> bytes:
        with BytesIO() as stream:
            self.write_value(stream)
            stream.seek(0)
            return stream.read()

    @classmethod
    def from_bytes(cls, input: bytes) -> TimeSeriesEventDataType[VT]:
        return cls(cls.value_type.from_bytes(input))

    @classmethod
    def decode(cls, data: bytes) -> typing.Any:
        return cls.from_bytes(data).value

    def validate(self):
        # no-op: validates on read
        pass

    @classmethod
    def converter_to(
        cls: typing.Type[TimeSeriesEventDataType[VT]],
        entity: typing.Type[AbstractDataType[TS_T_target, ValueType_target, RealValue_target]],
    ) -> typing.Optional[Converter[Event[VT], ValueType_target]]:
        if issubclass(entity, TimeSeriesEventDataType):
            converter = typing.cast(TimeSeriesEventDataType, entity).converter_from(cls)
            return typing.cast(
                typing.Optional[Converter[Event[VT], ValueType_target]], converter
            )
        return cls.value_type.converter_to(entity)

    @classmethod
    def converter_from(
        cls: typing.Type[AbstractDataType[TS_T, Event[VT], Event[VT]]],
        entity: typing.Type[ValueType_target],
    ) -> typing.Optional[Converter[ValueType_target, Event[VT]]]:
        if issubclass(entity, TimeSeriesEventDataType):
            self_cls = typing.cast(typing.Type[TimeSeriesEventDataType[VT]], cls)
            return typing.cast(
                typing.Optional[Converter[ValueType_target, Event[VT]]],
                self_cls.value_type.convert_from(entity.value_type),
            )
        return None

    @classmethod
    def inner_value_type(cls) -> typing.Optional[typing.Type[VT]]:
        vt: typing.Optional[typing.Type[Event[VT]]] = getattr(cls, "value_type", None)
        return vt.value_type_real() if vt else None

    with_properties: typing.ClassVar[TimeSeriesWithProperties] = TimeSeriesWithProperties()
    """
    Returns a Topic Specification class filled with this type
    and accepting the relevant parameters
    """


class TimeSeriesDataType(AbstractDataType):
    """ Time series data type implementation. """

    type_name = "time_series"
    ts_datatypes: typing.Dict[
        str, typing.Type[TimeSeriesEventDataType[typing.Any]]
    ] = {}

    @classmethod
    @validate_member_arguments
    def of(cls, val_type: typing.Type[VT]) -> typing.Type[TimeSeriesEventDataType[VT]]:
        """
        Provide a Time Series datatype with the given Event[VT] value type.

        Please use [TimeSeries.of][diffusion.features.timeseries.TimeSeries.of] rather
        than this function to obtain Time Series datatypes.

        Args:
            val_type: the type of value that events will contain.

        Returns:
            The relevant Time Series data type.
        """
        type_name = typing.cast(AbstractDataType, val_type).type_name
        if type_name not in cls.ts_datatypes:
            cls.ts_datatypes[type_name] = typing.cast(
                typing.Type[TimeSeriesEventDataType[VT]],
                type(
                    f"TimeSeriesEventDataType_{stringcase.pascalcase(type_name)}",
                    (TimeSeriesEventDataType,),
                    {
                        "value_type": EventTypeFactory.of(Event, val_type),
                        "type_name": f"timeseriesevent-{type_name}",
                    },
                ),
            )
        return typing.cast(
            typing.Type[TimeSeriesEventDataType[VT]],
            cls.ts_datatypes[type_name],
        )



class TimeSeriesValidator(object):
    def validate_ts(
            self, field_value: TimeSeriesValueType
    ) -> TimeSeriesValueType:
        return typing.cast(TimeSeriesValueType, self.validate_ts_typed(
            field_value,
            typing.cast(typing.Type[TimeSeriesValueType], type(field_value)),
        ))

    def validate_ts_typed(
            self,
            field_value: TimeSeriesValueTypeOrRaw,
            field_value_type: typing.Type[TimeSeriesValueType],
    ) -> TimeSeriesValueType:
        field_type: typing.Type[TimeSeriesValueType] = self.validate_ts_type(
            field_value_type
        )
        field_value_candidate = self.ensure_type(field_type, field_value)

        assert isinstance(field_value_candidate, field_type)
        return field_value_candidate

    # noinspection PyMethodMayBeStatic
    def ensure_type(
            self,
            field_type: typing.Type[TimeSeriesValueType],
            field_value: TimeSeriesValueTypeOrRaw,
    ) -> TimeSeriesValueType:

        field_value_candidate: TimeSeriesValueType

        self.ensure_ts(field_type)
        if isinstance(field_value, field_type):
            field_value_candidate = typing.cast(TimeSeriesValueType, field_value)
        else:
            constructed = field_type(field_value)  # type: ignore
            field_value_candidate = typing.cast(TimeSeriesValueType, constructed)

        @validate_member_arguments
        def ensure_ts_value(val: TimeSeriesValueType) -> TimeSeriesValueType:
            return val

        ensure_ts_value(field_value_candidate)
        return field_value_candidate

    @validate_member_arguments
    def ensure_ts(
            self,
            val: TimeSeriesValueTypeClasses
    ) -> TimeSeriesValueTypeClasses:
        return val

    def validate_ts_type(
            self, field_value_type
    ) -> typing.Type[TimeSeriesValueType]:
        field_type_final = self.ensure_ts(
            typing.cast(typing.Type[TimeSeriesValueType], field_value_type)
        )
        return field_type_final


TIME_SERIES_VALIDATOR = TimeSeriesValidator()

validate_ts = TIME_SERIES_VALIDATOR.validate_ts
validate_ts_type = TIME_SERIES_VALIDATOR.validate_ts_type
validate_ts_typed = TIME_SERIES_VALIDATOR.validate_ts_typed
