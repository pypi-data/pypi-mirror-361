#  Copyright (c) 2025 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

from __future__ import annotations

from typing import Optional

import typing_extensions

import typing

import dataclasses

from diffusion import datatypes as dt, SessionId
from diffusion.datatypes import AbstractDataType
from diffusion.internal.protocol.conversations import (
    ConversationID,
    Conversation,
    LOG,
)
from diffusion.internal.serialisers.base import Serialiser
from diffusion.internal.serialisers.dataclass_model import DataclassConfigMixin
from diffusion.internal.serialisers.specific.exceptions import ErrorReportSerialiser
from diffusion.internal.serialisers.generic_model import (
    GenericModel,
    PreparedModelAndConversation, )
from diffusion.internal.serialisers.generic_model_protocol import (
    ConversationFactory,
    CombinedMapping,
)
from diffusion.internal.validation import StrictStr
from diffusion.internal.validation.pydantic import UnsignedInt32
from diffusion.messaging import MessagingError

if typing.TYPE_CHECKING:
    from diffusion.internal.serialisers.generic_model import Model_Variants


@dataclasses.dataclass(frozen=True)
class MessagingSend(GenericModel):
    path: str
    request: dt.DataType

    @property
    def value_bytes(self):
        return bytes(self.request)

    @property
    def data_type_name(self):
        return self.request.type_name

    class Config(DataclassConfigMixin["MessagingSend"]):
        alias = "messaging-send-request"

        @classmethod
        def attr_mappings_all(
            cls, modelcls: typing.Type[MessagingReceiverServer]
        ):
            return {
                "messaging-send-request": {
                    "message-path": "path",
                    "serialised-value.data-type-name": "data_type_name",
                    "serialised-value.bytes": "value_bytes",
                }
            }

    @classmethod
    def from_fields(
        cls: typing.Type[typing_extensions.Self],
        *,
        data_type_name: str,
        value_bytes: bytes,
        **kwargs,
    ) -> typing_extensions.Self:
        return cls(
            request=typing.cast(
                AbstractDataType, dt.get(data_type_name).from_bytes(value_bytes)
            ),
            **kwargs,
        )


@dataclasses.dataclass(frozen=True)
class MessagingReceiverServer(MessagingSend):
    session_id: Optional[SessionId] = None

    class Config(DataclassConfigMixin["MessagingReceiverServer"]):
        alias = "messaging-client-send-request"

        @classmethod
        def attr_mappings_all(
            cls, modelcls: typing.Type[MessagingReceiverServer]
        ):
            return {
                "messaging-client-send-request": {
                    "session-id": "session_id",
                    "message-path": "path",
                    "serialised-value.data-type-name": "data_type_name",
                    "serialised-value.bytes": "value_bytes",
                }
            }


@dataclasses.dataclass(frozen=True)
class MessagingClientFilterSendRequest(GenericModel):
    session_filter: StrictStr
    path: StrictStr
    request: dt.DataType

    @property
    def value_bytes(self):
        return bytes(self.request)

    @property
    def data_type_name(self):
        return self.request.type_name

    class Config(DataclassConfigMixin["MessagingClientFilterSendRequest"]):
        alias = "messaging-client-filter-send-request"

        @classmethod
        def attr_mappings_combined(cls, modelcls: typing.Type[MessagingReceiverServer]):
            return {
                "messaging-client-filter-send-request": CombinedMapping(
                    {
                        "conversation-id": "conversation_id",
                        "session-filter": "session_filter",
                        "message-path": "path",
                        "serialised-value.data-type-name": "data_type_name",
                        "serialised-value.bytes": "value_bytes",
                    },
                    {"path": "path", "filter": "session_filter", "received": 0},
                )
            }

        @classmethod
        async def prepare_conversation(
            cls,
            item: MessagingClientFilterSendRequest,
            conversation_factory: ConversationFactory
        ) -> PreparedModelAndConversation[MessagingClientFilterSendRequest]:
            conversation = await conversation_factory()
            return PreparedModelAndConversation(
                MessagingClientFilterSendRequestPrepared(
                    **dataclasses.asdict(item), conversation_id=conversation.cid
                ),
                conversation,
            )


@dataclasses.dataclass(frozen=True)
class MessagingClientFilterSendRequestPrepared(
    MessagingClientFilterSendRequest
):
    conversation_id: ConversationID


@dataclasses.dataclass(frozen=True)
class Count(GenericModel):
    count: UnsignedInt32

    class Config(DataclassConfigMixin["Count"]):
        @classmethod
        def attr_mappings_combined(
            cls, modelcls
        ) -> typing.Mapping[str, CombinedMapping]:
            return {
                "count": CombinedMapping(
                    {"count": "count"}, {"expected": "count"}
                )
            }

        @classmethod
        async def respond_to_conversation(
            cls,
            item: Count,
            conversation: typing.Optional[Conversation],
            serialiser: Serialiser,
        ) -> Count:
            LOG.debug(
                "Expecting responses from filter.",
                expected_responses=item.count,
            )
            return await super().respond_to_conversation(item, conversation, serialiser)


class InvalidFilterErrorReportSerialiser(ErrorReportSerialiser):
    class Config(ErrorReportSerialiser.Config[MessagingError]):
        exception_type = MessagingError

        @classmethod
        async def respond_to_conversation(
            cls,
            item: ErrorReportSerialiser,
            conversation: typing.Optional[Conversation],
            serialiser: Serialiser,
        ) -> ErrorReportSerialiser:
            LOG.debug(
                "Received error report from the server.",
                message=item.message,
                line=item.line,
                column=item.column,
            )
            return await super().respond_to_conversation(
                item, conversation, serialiser
            )

        @classmethod
        async def exception_to_raise(
                cls, item: ErrorReportSerialiser
        ) -> MessagingError:
            return MessagingError(item.message)


@dataclasses.dataclass(frozen=True)
class MessagingClientFilterSendResult(GenericModel):
    content: typing.Union[Count, InvalidFilterErrorReportSerialiser]

    class Config(DataclassConfigMixin["MessagingClientFilterSendResult"]):
        @classmethod
        def decode(
            cls,
            item,
            modelcls: typing.Type[Model_Variants],
            model_key: str,
            serialiser: Optional[Serialiser] = None,
        ):
            serialiser = cls.check_serialiser(serialiser)
            return super().decode_complex(item, modelcls, model_key, serialiser)

        @classmethod
        def attr_mappings_combined(cls, modelcls):
            return {
                "count-or-parser-errors2": CombinedMapping(
                    {"count-or-parser-errors2": "content"}
                )
            }

@dataclasses.dataclass(frozen=True)
class MessagingReceiverControlRegistration(GenericModel):
    service_id: int
    control_group: StrictStr
    path: StrictStr
    session_properties: typing.Collection[str]

    class Config(DataclassConfigMixin["MessagingReceiverControlRegistration"]):
        @classmethod
        def attr_mappings_all(cls, modelcls):
            return {
                "message-receiver-control-registration-request": {
                    "message-receiver-control-registration-parameters.service-id": "service_id",
                    "message-receiver-control-registration-parameters.control-group": "control_group",  # noqa: E501
                    "message-receiver-control-registration-parameters.topic-path": "path",
                    "message-receiver-control-registration-parameters.session-property-keys": "session_properties",  # noqa: E501
                    "conversation-id": "conversation_id",
                }
            }

        @classmethod
        async def prepare_conversation(
            cls,
            item: MessagingReceiverControlRegistration,
            conversation_factory: ConversationFactory,
        ) -> PreparedModelAndConversation[
            MessagingReceiverControlRegistrationPrepared
        ]:
            conversation = await conversation_factory()
            return PreparedModelAndConversation(
                MessagingReceiverControlRegistrationPrepared(
                    conversation_id=conversation.cid, **dataclasses.asdict(item)
                ),
                conversation,
            )


@dataclasses.dataclass(frozen=True)
class MessagingReceiverControlRegistrationPrepared(
    MessagingReceiverControlRegistration
):
    conversation_id: ConversationID
