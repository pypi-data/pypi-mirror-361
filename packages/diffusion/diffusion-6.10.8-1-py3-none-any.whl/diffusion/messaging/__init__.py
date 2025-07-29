#  Copyright (c) 2020 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

""" Request-response messaging functionality. """
from __future__ import annotations
from typing import Collection, Optional, Callable

import typing
import structlog

from diffusion import datatypes as dt
from diffusion.handlers import Handler
from diffusion.internal import utils
from diffusion.internal.components import Component
from diffusion.internal.exceptions import DiffusionError
from diffusion.internal.protocol import SessionId
from diffusion.internal.validation import StrictStr

LOG = structlog.get_logger()


class Messaging(Component):
    """Messaging component.

    It is not supposed to be instantiated independently; an instance is available
    on each `Session` instance as `session.messaging`.
    """

    def add_stream_handler(
        self,
        path: str,
        handler: RequestHandler,
        addressed: bool = False,
    ) -> None:
        """Registers a request stream handler.

        The handler is invoked when the session receives a request sent
        to the given path or session filter.

        Args:
            path: The handler will respond to the requests to this path.
            handler: A Handler instance to handle the request.
            addressed: `True` to handle the requests addressed to the session's ID or
                       using a session filter; `False` for unaddressed requests.
        """
        service_type_name = "MESSAGING_SEND" if addressed else "MESSAGING_RECEIVER_CLIENT"
        service_type = type(self.services[service_type_name])
        self.session.handlers[(service_type, path)] = handler

    def add_filter_response_handler(self, session_filter: str, handler: Handler) -> None:
        """Registers a session filter response handler.

        The handler is invoked when the session receives a response
        to a request sent to the session filter.

        Args:
            session_filter: A session filtering query.
            handler: A Handler instance to handle the request.
        """
        service_type = type(self.services.FILTER_RESPONSE)
        self.session.handlers[(service_type, session_filter)] = handler

    async def _send_request(
        self,
        path: str,
        request: dt.DataType,
        response_type: Optional[dt.DataTypeArgument] = None,
        session_id: Optional[SessionId] = None,
    ) -> Optional[dt.DataType]:
        """Common functionality to send a request to one or more sessions.

        Args:
            path: The path to send a request to.
            request: The request to be sent, wrapped into the required `DataType` class.
            response_type: The type to convert the response to. If omitted, it will be
                           the same as the `request`'s data type.
            session_id: If specified, the request will only be sent to the session with
                        that ID. If omitted, the server will forward the request to one
                        of the sessions registered as handlers for the given `path`.

        Returns:
            The response value of the provided `response_type`.
        """
        from diffusion.internal.serialisers.specific.messaging import (
            MessagingSend,
            MessagingReceiverServer,
        )

        if session_id is not None:
            response = await self.services.MESSAGING_RECEIVER_SERVER.invoke(
                self.session, MessagingReceiverServer(path, request, session_id)
            )
        else:
            response = await self.services.MESSAGING_SEND.invoke(
                self.session, MessagingSend(path, request)
            )
        if response is None:
            return None
        if response_type is None:
            response_type = type(request)
        response_type = dt.get(response_type)
        if response.serialised_value.type_name != response_type.type_name:
            raise dt.InvalidDataError
        return response_type.from_bytes(response.serialised_value.to_bytes())  # type: ignore

    async def send_request_to_path(
        self,
        path: str,
        request: dt.DataType,
        response_type: Optional[dt.DataTypeArgument] = None,
    ) -> Optional[dt.DataType]:
        """Send a request to sessions based on a path.

        Args:
            path: The path to send a request to.
            request: The request to be sent, wrapped into the required `DataType` class.
            response_type: The type to convert the response to. If omitted, it will be
                           the same as the `request`'s data type.

        Returns:
            The response value of the provided `response_type`.
        """
        return await self._send_request(path=path, request=request, response_type=response_type)

    async def add_request_handler(
        self,
        path: str,
        handler: RequestHandler,
        session_properties: Collection[str] = (),
    ) -> None:
        """Register the session as the handler for requests to a given path.

        This method is used to inform the server that any unaddressed requests to the
        given path should be forwarded to the active session. The handler to
        these requests is added at the same time, using `add_stream_handler` internally.

        Args:
            path: The handler will respond to the requests to this path.
            handler: A callable to handle the request.
            session_properties: A list of keys of session properties that should be
                                supplied with each request. To request all fixed
                                properties include `ALL_FIXED_PROPERTIES` as a key; any
                                other fixed property keys will be ignored. To request
                                all user properties include `ALL_USER_PROPERTIES` as a
                                key; any other user properties will be ignored.
        """
        from diffusion.internal.serialisers.specific.messaging import (
            MessagingReceiverControlRegistration,
        )
        self.add_stream_handler(path, handler)

        return await self.services.MESSAGING_RECEIVER_CONTROL_REGISTRATION.invoke(
            self.session,
            MessagingReceiverControlRegistration(
                self.services.MESSAGING_RECEIVER_CLIENT.service_id,
                control_group=typing.cast(StrictStr, ""),
                path=typing.cast(StrictStr, path),
                session_properties=session_properties,
            ),
        )

    async def send_request_to_filter(
        self,
        session_filter: StrictStr,
        path: StrictStr,
        request: dt.DataType,
    ) -> int:
        """Send a request to other sessions, specified by the filter.

        Args:
            session_filter: A session filtering query.
            path: The path to send a request to.
            request: The request to be sent, wrapped into the required `DataType` class.

        Returns:
            The number of sessions that correspond to the filter, which is the number of
            responses that can be expected. When each of the responses is received, the
            handler registered for the filter will be executed.
        """
        from diffusion.internal.serialisers.specific.messaging import (
            MessagingClientFilterSendRequest,
            MessagingClientFilterSendResult, Count
        )

        raw_result = (
            await self.services.MESSAGING_FILTER_SENDER.invoke(
                self.session,
                request=MessagingClientFilterSendRequest(
                    session_filter, path, request
                ),
                response_type=MessagingClientFilterSendResult,
            )
        )
        # the other possibility raises an exception
        assert isinstance(raw_result.content, Count)
        return raw_result.content.count


    async def send_request_to_session(
        self,
        path: str,
        session_id: SessionId,
        request: dt.DataType,
        response_type: Optional[dt.DataTypeArgument] = None,
    ) -> Optional[dt.DataType]:
        """Send a request to a single session.

        Args:
            path: The path to send a request to.
            session_id: The ID of the session to send the request to.
            request: The request to be sent, wrapped into the required `DataType` class.
            response_type: The type to convert the response to. If omitted, it will be
                           the same as the `request`'s data type.

        Returns:
            The response value of the provided `response_type`.
        """
        return await self._send_request(
            path=path, request=request, response_type=response_type, session_id=session_id
        )

    class RequestHandler(Handler):
        """ Handler for messaging requests. """

        def __init__(
                self,
                callback: Callable,
                request_type: dt.DataTypeArgument,
                response_type: dt.DataTypeArgument,
        ):
            self.request_type = dt.get(request_type)
            self.response_type = dt.get(response_type)
            self.callback = utils.coroutine(callback)

        async def handle(self, event: str = "request", **kwargs) -> dt.DataType:
            """Execute the callback."""
            request: dt.DataType = kwargs.pop("request")
            if not isinstance(request, self.request_type):
                raise dt.IncompatibleDatatypeError(
                    "Incompatible request data type: "
                    f"required: {self.request_type.__name__}; \
                    submitted: {type(request).__name__}"
                )
            response_raw = await self.callback(request.value, **kwargs)
            try:
                response = self.response_type(response_raw)
            except dt.DataTypeError as ex:
                error_message = self._get_response_error(response_raw, request, **kwargs)
                raise dt.IncompatibleDatatypeError(error_message) from ex

            return response

        def _get_response_error(
            self, response_raw: typing.Any, request: dt.DataType, **kwargs
        ) -> str:
            return (
                f"{self}: {self._get_function_desc(request, **kwargs)} returned "
                f"{repr(response_raw)}: This could not be materialised into the response type "
                f"'{self._get_type_name(self.response_type)}'"
            )

        def _get_function_desc(self, request: dt.DataType, **kwargs):
            function_name = getattr(
                self.callback,
                "__qualname__",
                getattr(self.callback, "__name__", repr(self.callback)),
            )
            extra_args = f", **{kwargs}" if kwargs else ""
            function_desc = f"({function_name})({repr(request.value)}{extra_args})"
            return function_desc

        @staticmethod
        def _get_type_name(response_type: typing.Type[dt.DataType]):
            return getattr(
                response_type,
                "__qualname__",
                getattr(response_type, "__name__", repr(response_type)),
            )


class MessagingError(DiffusionError):
    """ The generic messaging error. """


RequestHandler = Messaging.RequestHandler
