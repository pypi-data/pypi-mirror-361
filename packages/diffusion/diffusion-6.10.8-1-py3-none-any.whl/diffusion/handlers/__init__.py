#  Copyright (c) 2022 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

"""Base module for various event handlers."""
import abc
import typing

import asyncio

import structlog
from typing_extensions import Protocol, runtime_checkable, TypedDict

from diffusion.internal import exceptions
from diffusion.internal.utils import coroutine

LOG: structlog.stdlib.BoundLogger = structlog.get_logger()


@runtime_checkable
class Handler(Protocol):
    """Protocol for event handlers implementation."""

    async def handle(self, event: str, **kwargs: typing.Any) -> typing.Any:
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            **kwargs: Additional arguments.
        """
        ...  # pragma: no cover


HandlersMapping = typing.MutableMapping[typing.Hashable, Handler]


class UnknownHandlerError(exceptions.DiffusionError):
    """ Raised when a requested handler key has not been registered in the session. """


@runtime_checkable
class SubHandlerProtocol(Protocol):
    def __init__(self):
        pass  # pragma: no cover

    async def __call__(
        self,
        *,
        topic_path: str,
        topic_value: typing.Any,
        old_value: typing.Optional[typing.Any] = None,
        **kwargs: typing.Any,
    ) -> typing.Any:
        pass   # pragma: no cover


# fallback for tooling that doesn't support Callable Protocols
SubHandler = typing.Union[
    SubHandlerProtocol, typing.Callable, typing.Callable[[typing.Any], typing.Any]
]


class SimpleHandler(Handler):
    """ Wraps a callable into a Handler protocol instance. """

    def __init__(self, callback: SubHandler):
        self._callback = coroutine(callback)

    async def handle(self, event: str = "", **kwargs: typing.Any) -> typing.Any:
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            **kwargs: Additional arguments.
        """
        return await self._callback(**kwargs)


class AbstractHandlerSet(Handler, typing.Iterable[Handler], abc.ABC):
    async def handle(self, event: str = "", **kwargs: typing.Any) -> typing.Any:
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            **kwargs: Additional arguments.

        Returns:
            Aggregated list of returned values.
        """
        return await asyncio.gather(*[handler.handle(**kwargs) for handler in self])


class HandlerSet(set, AbstractHandlerSet):
    """ A collection of handlers to be invoked together. """


class SubHandlerDict(TypedDict, total=False):
    subscribe: SubHandler


class OptionalDict(SubHandlerDict, total=False):
    pass


class ErrorHandler(Protocol):
    async def __call__(self, code: int, description: str) -> None:
        pass    # pragma: no cover


SubHandlerDictType = typing.TypeVar("SubHandlerDictType", bound=SubHandlerDict)


class EventStreamHandler(Handler):
    """Generic handler of event streams.

    Each keyword argument is a callable which will be converted to coroutine
    and awaited to handle the event matching the argument keyword.
    """
    _handlers: SubHandlerDict

    def __init__(
        self,
        *,
        on_error: typing.Optional[ErrorHandler] = None,
        **kwargs: typing.Optional[SubHandler]
    ):
        all_args = typing.cast(typing.Dict[str, typing.Any], kwargs)
        all_args.update(on_error=on_error)
        self._handlers: SubHandlerDict = typing.cast(
            SubHandlerDict,
            {
                event: coroutine(callback)
                for event, callback in all_args.items()
                if callback
            },
        )

    async def handle(self, event: str, **kwargs: typing.Any) -> typing.Any:
        """Implements handling of the given event.

        Args:
            event: The event identifier.
            **kwargs: Additional arguments.
        """
        try:
            handler = (typing.cast(typing.Mapping[str, typing.Callable], self._handlers))[event]
        except KeyError:
            LOG.debug("No handler registered for event.", stream_event=event, **kwargs)
        else:
            return await handler(**kwargs)

    def __str__(self):
        return f"{type(self)} with handlers {self._handlers}"

    def __repr__(self):
        return str(self)
