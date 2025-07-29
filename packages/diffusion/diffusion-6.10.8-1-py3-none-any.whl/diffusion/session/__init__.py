#  Copyright (c) 2022 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

"""
Public session for end users.
"""
from __future__ import annotations

import typing
from typing import cast, Hashable, Optional, TYPE_CHECKING

import structlog

import diffusion.exceptions
from diffusion.handlers import Handler, EventStreamHandler
from diffusion.internal.exceptions import DiffusionError
from diffusion.session.locks.session_lock_acquisition import SessionLockScope
from diffusion.session.locks.session_locks import SessionLocks, SessionLock
from diffusion.session.retry_strategy import RetryStrategy
from diffusion.session.session_factory import SessionEstablishmentException, SessionProperties

if TYPE_CHECKING:
    from diffusion.features.control.metrics import Metrics
    from diffusion.messaging import Messaging
    from diffusion.features.topics import Topics
    from diffusion.features.control.session_trees import SessionTrees
    from diffusion.features.timeseries import TimeSeries
    from diffusion.internal.session import (
        State,
        InternalSession,
        InternalSessionListener,
        ConnectionFactory, AbstractConnection
    )
    from diffusion.internal.session import Credentials
    from diffusion.internal.session.session_attributes_core import SessionAttributes

if not structlog.is_configured():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


ANONYMOUS_PRINCIPAL = ""
"""
Anonymous principal username
"""


class Session:
    """A client session connected to a Diffusion server or a cluster of servers.

    Args:
        url: WebSockets URL of the Diffusion server to connect to.
        principal: The name of the security principal associated with the session.
        credentials: Security information required to authenticate the connection.

    The recommended method is to instantiate this class as an async context manager.
    Here is a minimal example:

    ```pycon
    >>> async with diffusion.Session("ws://diffusion.server:8080") as session:
    ...     # do some work with the session
    ...     pass
    ```

    The context manager will make sure that the connection is properly closed at
    the end of the program. Alternatively, it is possible to open the connection
    explicitly, which can be useful if the session needs to be passed around, in
    this case the connection needs to be explicitly closed as well:

    ```pycon
    >>> session = diffusion.Session("ws://diffusion.server:8080")
    >>> await session.connect()
    >>> # do some work with the session
    >>> await session.close()

    ```
    """

    def __init__(
        self,
        url: str,
        principal: Optional[str] = None,
        credentials: Optional[Credentials] = None,
        properties: Optional[typing.Mapping[str, str]] = None,
        connection_factory: Optional[ConnectionFactory] = None,
        internal_session_factory: Optional[
            typing.Callable[
                [typing.Union[AbstractConnection, ConnectionFactory]], InternalSession
            ]
        ] = None,
        attributes: typing.Optional[SessionAttributes] = None
    ):
        from diffusion.internal.session.session_attributes_core import SessionAttributes

        self.attributes = attributes or SessionAttributes()
        from diffusion.internal.session import (
            InternalSession,
            Credentials,
            DefaultConnectionFactory,
        )

        internal_session_factory = internal_session_factory or InternalSession
        principal = principal or ANONYMOUS_PRINCIPAL
        if credentials is None:
            credentials = Credentials()

        self._internal = internal_session_factory(
          connection_factory
          or DefaultConnectionFactory(url, principal, credentials, attributes)
        )
        if properties is None:
            properties = {}
        self.properties = {**properties}
        self._messaging: Optional[Messaging] = None
        self._topics: Optional[Topics] = None
        self._session_trees: Optional[SessionTrees] = None
        self._metrics: Optional[Metrics] = None
        self._time_series: Optional[TimeSeries] = None
        self._listener_mappings: typing.Dict[SessionListener, InternalSessionListener] = {}
        self._session_locks: Optional[SessionLocks] = None

    async def __aenter__(self):
        try:
            await self.connect()
            return self
        except DiffusionError as ex:
            await self.close()
            raise ex

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self, properties: Optional[SessionProperties] = None):
        """Connect to the server.

        Args:
            properties: A dict of Diffusion session properties to set and/or
                        update at connection.
        """
        if properties is not None:
            self.properties.update(properties)
        await self._internal.connect(self.properties)

    async def close(self):
        """ Closes the session. """
        await self._internal.close()

    @property
    def state(self):
        """ Returns the current connection state of the session. """
        return self._internal.connection.state

    @property
    def session_id(self):
        """ The current session ID. """
        return self._internal.session_id

    @property
    def services(self):
        """ The ServiceLocator instance responsible for retrieving services. """
        return self._internal.services

    @property
    def handlers(self):
        """ The collection of registered handlers. """
        return self._internal.handlers

    @property
    def data(self) -> dict:
        """ Internal data storage. """
        return self._internal.data

    async def ping_server(self):
        """ Send the user ping to the server. """
        return await self.services.USER_PING.invoke(self._internal)

    def _add_ping_handler(self, handler: Handler) -> None:
        """Register a new handler for system pings.

        Args:
            handler: The Handler instance to be invoked when a system ping
                     message is received by the session.
        """
        service_type = cast(Hashable, type(self.services.SYSTEM_PING))
        self._internal.handlers[service_type] = handler

    async def lock(
            self,
            lock_name: str,
            scope: SessionLockScope = SessionLockScope.UNLOCK_ON_SESSION_LOSS,
    ) -> SessionLock:
        """
        Attempts to acquire a [SessionLock][diffusion.session.locks.session_locks.SessionLock] with a given scope.

        Notes:
            If the operation completes successfully,
            the result will be the requested [SessionLock][diffusion.session.locks.session_locks.SessionLock]
            assigned to the calling session by the server.
            The session owns the returned lock
            and is responsible for unlocking it.

            Acquiring the lock can take an arbitrarily long time
            if other sessions are competing for the lock.
            The server will retain the session's request for the lock
            until it is assigned to the session,
            the session is closed.

            A session can call this method multiple times.
            If the lock is acquired,
            all calls will complete successfully with equal [SessionLock][diffusion.session.locks.session_locks.SessionLock].

            A session that acquires a lock will remain its owner until it is unlocked
            (via [SessionLock.unlock][diffusion.session.locks.session_locks.SessionLock.unlock])
            or the session closes.

            If called with a `scope` of
            [SessionLockScope.UNLOCK_ON_SESSION_LOSS][diffusion.session.locks.session_lock_acquisition.SessionLockScope.UNLOCK_ON_SESSION_LOSS],
            this method behaves exactly like [SessionLocks.lock][diffusion.session.locks.session_locks.SessionLocks.lock].

            If called with a `scope` of
            [SessionLockScope.UNLOCK_ON_CONNECTION_LOSS][diffusion.session.locks.session_lock_acquisition.SessionLockScope.UNLOCK_ON_CONNECTION_LOSS],
            any lock that is returned will be unlocked
            if the session loses its connection to the server.
            This is useful to allow another session to take ownership of the lock
            while this session is reconnecting.

            If a session makes multiple requests for a lock using different scopes,
            and the server assigns the lock to the session fulfilling the requests,
            the lock will be given the weakest scope
            ([SessionLockScope.UNLOCK_ON_CONNECTION_LOSS][diffusion.session.locks.session_lock_acquisition.SessionLockScope.UNLOCK_ON_CONNECTION_LOSS]).

            # Access control

            To allow fine-grained access control,
            lock names are interpreted as path names,
            controlled with the update-topic/b,
            for example.

        Since:
            6.10.

        Args:
            lock_name: The name of the session lock.
            scope: The scope of the session lock.
        Returns:    
            A session lock object.

        """  # noqa: E501, W291
        self._session_locks = self._session_locks or SessionLocks(self._internal)
        return await self._session_locks.lock(lock_name, scope)

    @property
    def messaging(self) -> Messaging:
        """ Request-response messaging component. """
        from diffusion.messaging import Messaging
        if self._messaging is None:
            self._messaging = Messaging(self)
        return self._messaging

    @property
    def topics(self) -> Topics:
        """ Topics component. """
        from diffusion.features.topics import Topics
        if self._topics is None:
            self._topics = Topics(self)
        return self._topics

    @property
    def session_trees(self) -> SessionTrees:
        """ Session Trees component. """
        from diffusion.features.control.session_trees import SessionTrees
        self._session_trees = (self._session_trees or SessionTrees(self))
        return self._session_trees

    @property
    def metrics(self) -> Metrics:
        """ Metrics component. """
        from diffusion.features.control.metrics import Metrics
        self._metrics = self._metrics or Metrics(self)
        return self._metrics

    @property
    def time_series(self) -> TimeSeries:
        """ Time Series component. """
        from diffusion.features.timeseries import TimeSeries
        self._time_series = self._time_series or TimeSeries(self)
        return self._time_series

    async def on_state_changed(self, old_state: State, new_state: State):
        """
        Raises the StateChanged event from session.
        Bound as a handler on the InternalSession.on_state_changed event.
        """
        await self._internal.on_session_event(
            session=self._internal, old_state=old_state, new_state=new_state
        )

    def add_listener(self, listener: SessionListener):
        from diffusion.internal.session import InternalSession

        class InternalWrapper(object):
            def __init__(self, parent: Session):
                super().__init__()
                self.parent = parent

            # noinspection PyUnusedLocal
            async def on_session_event(
                self,
                *,
                session: InternalSession,
                old_state: typing.Optional[State],
                new_state: State
            ):
                """
                Called when a session changed state.

                Args:
                    session: The session that sent this event.
                    old_state: The old session state.
                    new_state: The session state.
                """

                await listener.on_session_event(
                    session=self.parent, old_state=old_state, new_state=new_state
                )

        wrapped = InternalWrapper(self)
        self._internal.add_listener(wrapped)
        self._listener_mappings[listener] = wrapped

    def remove_listener(self, listener: SessionListener):
        """
        Remove a given session state listener from the session
        Args:
            listener: the listener to remove

        Raises:
            InvalidOperationError: if no such listener is present

        """
        wrapped = self._listener_mappings.get(listener)
        if not wrapped:
            raise diffusion.exceptions.InvalidOperationError(
                f"No such listener {listener} present"
            )

        self._internal.remove_listener(wrapped)


class SessionListener(EventStreamHandler):
    """
    The session listener.

    """

    async def on_session_event(
        self, *, session: Session, old_state: typing.Optional[State], new_state: State
    ):
        """
        Called when a session changed state.

        Args:
            session: The session that sent this event.
            old_state: The old session state.
            new_state: The session state.
        """
        pass
