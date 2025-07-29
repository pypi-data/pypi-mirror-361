import asyncio
import collections.abc
import importlib.metadata
import logging
import typing
import warnings
from contextlib import asynccontextmanager
from functools import lru_cache
from importlib import import_module

import backoff
import sys
import time
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from google.protobuf.empty_pb2 import Empty
from google.protobuf.message import Message
from grpclib.exceptions import StreamTerminatedError, GRPCError

from momotor.django.defaults import *
from momotor.rpc.asset.exceptions import UnexpectedEndOfStream
from momotor.rpc.auth.client import get_authenticated_channel
from momotor.rpc.exception import raise_message_exception, RPCException, AuthException
from momotor.rpc.proto.auth_pb2 import ServerInfoResponse
from momotor.rpc.proto.client_grpc import ClientStub
from momotor.rpc.proto.job_pb2 import JobStatusStream
from momotor.rpc.utils import format_msg
from momotor.shared.doc import annotate_docstring
from momotor.shared.log import AsyncLogWrapper

try:
    import ssl
except ImportError:
    ssl = None

if typing.TYPE_CHECKING:
    from concurrent.futures import Executor

logger = logging.getLogger(__package__)
async_logger = AsyncLogWrapper(logger)

retry_exceptions = (ConnectionError, StreamTerminatedError, UnexpectedEndOfStream, GRPCError)
if ssl:
    retry_exceptions += (ssl.SSLError, ssl.CertificateError, ssl.SSLEOFError)

retry_connection = backoff.on_exception(
    backoff.expo,
    retry_exceptions,
    max_value=10,
    logger=logger
)

retry_connection.__doc__ = f"""
    A decorator to retry a function when a transient connection error occurs.
    
    Catches the exception and retries the function several times whenever one of the following exceptions is raised:
    
    * :py:class:`ConnectionError`
    * :py:class:`grpclib.exceptions.GRPCError`
    * :py:class:`grpclib.exceptions.StreamTerminatedError`
    * :py:class:`momotor.rpc.asset.exceptions.UnexpectedEndOfStream`
    * :py:class:`ssl.CertificateError`
    * :py:class:`ssl.SSLEOFError`
    * :py:class:`ssl.SSLError`
    
    Produces log messages on the ``{logger.name}`` logger.
"""


def consume_task_result(task: asyncio.Task):
    try:
        task.result()
    except:
        pass


@lru_cache(maxsize=1)
def get_protocol_version():
    return importlib.metadata.version('momotor-engine-proto')


async def version_check(server_info: "ServerInfoResponse"):
    if (local_version := get_protocol_version()) != (remote_version := server_info.protoVersion):
        msg = f"protocol version mismatch: client has {local_version}, broker has {remote_version}"
        await async_logger.warning(msg)


@retry_connection
async def _retry_message(method, request, timeout=None):
    try:
        await async_logger.debug(f"RPC call {method.name} {format_msg(request)}")
        response = await asyncio.wait_for(method(request), timeout=timeout)
        await async_logger.debug(f"RPC call {method.name} {format_msg(request)} response: {format_msg(response)}")
        raise_message_exception(response)
        return response

    except (ConnectionError, StreamTerminatedError, UnexpectedEndOfStream):
        raise

    except asyncio.TimeoutError:
        await async_logger.error(f"RPC call {method.name} {format_msg(request)} timeout")
        raise

    except AuthException:
        await async_logger.error(f"RPC call {method.name} {format_msg(request)} authentication error")
        raise

    except RPCException as exc:
        await async_logger.error(f"RPC call {method.name} {format_msg(request)} failed: {exc}")
        raise

    except (ConnectionError, StreamTerminatedError, UnexpectedEndOfStream) as exc:
        await async_logger.error(f"RPC call {method.name} {format_msg(request)} connection interrupted: {exc}")
        raise

    except Exception:
        await async_logger.exception(f"RPC call {method.name} {format_msg(request)} failed")
        raise


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    Copied from rest_framework.settings
    """
    try:
        # Nod to tastypie's use of importlib.
        module_path, class_name = val.rsplit('.', 1)
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


@annotate_docstring(logger=logger)
class BrokerConnection:
    """ Connection class to Momotor broker.

    Provides methods to connect to the Momotor broker and send and receive messages to and from the
    :py:class:`~momotor.rpc.proto.client_grpc.ClientStub`

    Is configured through the :setting:`MOMOTOR_BROKER` setting.

    Produces log messages on the ``{logger.name}`` logger.

    :param loop: The :std:doc:`asyncio loop <python:library/asyncio-eventloop>` to use the `executor` with.
                 If `None`, uses the current active event loop. (Deprecated on Python 3.8)
    :param executor: An executor to run I/O blocking tasks on. If `None`, uses the current loop's default executor.
    :param token_pool_kwargs: Any additional keyword arguments are passed on to the :ref:`token store <token_store>`
    """
    def __init__(self, *, loop=None, executor: "Executor" = None, **token_pool_kwargs):
        if loop is not None and sys.version_info >= (3, 8):
            warnings.warn("The loop argument is deprecated since Python 3.8+", DeprecationWarning)

        self.loop = loop

        broker_settings = getattr(settings, 'MOMOTOR_BROKER')
        assert broker_settings is not None, 'MOMOTOR_BROKER missing from settings'
        for key in ['API_KEY', 'API_SECRET']:
            assert key in broker_settings, f'{key} missing from MOMOTOR_BROKER settings'
            
        use_ssl = broker_settings.get('USE_SSL')
        if use_ssl not in ('no', 'yes', 'insecure', None):
            raise ImproperlyConfigured(
                f"'{use_ssl}' is not a valid value for MOMOTOR_BROKER.USE_SSL settings. "
                f"Valid options are 'no', 'yes' and 'insecure'"
            )

        port = broker_settings.get('PORT')
        if port is not None:
            try:
                port = int(port)
            except (ValueError, TypeError):
                raise ImproperlyConfigured('MOMOTOR_BROKER.PORT should be None or an integer value')

        # Get defaults for USE_SSL and PORT if either or both are None
        if use_ssl is None:
            if port is None:
                if ssl:
                    use_ssl, port = 'yes', DEFAULT_BROKER_SSL_PORT
                else:
                    use_ssl, port = 'no', DEFAULT_BROKER_PORT
            elif port == DEFAULT_BROKER_SSL_PORT:
                use_ssl = 'yes'
            else:
                use_ssl = 'no'
        elif port is None:
            port = DEFAULT_BROKER_PORT if use_ssl == 'no' else DEFAULT_BROKER_SSL_PORT

        if use_ssl == 'no':
            ssl_context = None
            logger.warning('not using SSL for broker connection')
        elif not ssl:
            raise ImproperlyConfigured("SSL support requires the openssl package to be installed")
        else:
            ssl_context = ssl.create_default_context()
            if use_ssl == 'insecure':
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                logger.warning('using SSL for broker connection in "insecure" mode')

        self.__broker_settings = {
            'host': broker_settings.get('HOST') or DEFAULT_BROKER_HOST,
            'port': port,
            'ssl_context': ssl_context,
            'api_key': broker_settings['API_KEY'],
            'api_secret': broker_settings['API_SECRET'],
        }

        token_store_setting_name = 'TOKEN_POOL_CLASS'
        if token_store_setting_name in broker_settings:
            logger.warning('MOMOTOR_BROKER.TOKEN_POOL_CLASS is deprecated. Use TOKEN_STORE_CLASS')
        else:
            token_store_setting_name = 'TOKEN_STORE_CLASS'

        token_store_class_name = broker_settings.get(token_store_setting_name, DEFAULT_TOKEN_STORE_CLASS)
        token_store_class = import_from_string(token_store_class_name, f'MOMOTOR_BROKER.{token_store_setting_name}')
        self.__token_store = token_store_class(broker_settings, loop=loop, executor=executor, **token_pool_kwargs)

        self._server_info = None
        self._server_info_timestamp = None
        self._server_info_max_age = broker_settings.get('INFO_MAX_AGE', DEFAULT_INFO_MAX_AGE)
        self._server_info_lock = asyncio.Lock()

        self._connect_lock = asyncio.Lock()

        self._channel = None
        self._auth_stub = None
        self._client_stub = None

    @retry_connection
    async def __get_authenticated_stub(self, private):
        auth_token = await self.__token_store.get()

        if private:
            assert self._channel, "Connect to a normal channel before attempting to connect to a private channel"
            assert auth_token, "Auth token missing"

        try:
            auth_channel, auth_stub = await get_authenticated_channel(
                **self.__broker_settings,
                auth_token=auth_token,
                loop=self.loop,
                log_h2=settings.DEBUG,
            )

        except RPCException:
            await self._disconnect(True)
            await asyncio.sleep(5)
            return None, None

        # noinspection PyTypeChecker
        client_stub = ClientStub(auth_channel)
        if not private:
            self._channel = auth_channel
            self._auth_stub = auth_stub
            self._client_stub = client_stub
            await self.__token_store.set(auth_channel.auth_token)

        return auth_channel, client_stub

    async def _connect(self):
        async with self._connect_lock:
            while not self._channel:
                await async_logger.debug("connecting to broker for shared channel")

                client_stub = await self.__get_authenticated_stub(False)
                if client_stub:
                    try:
                        await self._get_server_info()
                    except:
                        await self._disconnect(False)

    async def _disconnect(self, reset):
        if self._channel:
            try:
                self._channel.close()
            except:
                pass

        if reset:
            await async_logger.debug('deleting cached auth-token')
            await self.__token_store.delete()

        self._channel = None
        self._auth_stub = None
        self._client_stub = None

    async def disconnect(self, reset=False):
        """ Disconnect from the broker.

        If `reset` is `True`, resets the authentication state by deleting the token.

        :param reset: Reset authentication state
        """
        await async_logger.debug("disconnecting from broker")

        async with self._connect_lock:
            await self._disconnect(reset)

    @asynccontextmanager
    async def get_stub(self, private_channel=False):
        """ Context manager to get an authenticated :py:class:`~momotor.rpc.proto.client_grpc.ClientStub`

        :param private_channel: If `True`, creates a new single-use channel to the broker that will be closed when
                                the context exits. If `False`, uses a shared channel.
        """
        await self._connect()

        if not private_channel:
            yield self._client_stub

        else:
            await async_logger.debug("connecting to broker for private channel")

            async with self._connect_lock:
                channel, client_stub = await self.__get_authenticated_stub(True)

            try:
                yield client_stub

            except AuthException:
                await self.disconnect(True)
                raise

            finally:
                try:
                    channel.close()
                except:
                    pass

    async def _get_server_info(self) -> "ServerInfoResponse":
        await async_logger.debug("retrieving serverInfo")

        self._server_info_timestamp = time.monotonic()
        self._server_info = server_info = await _retry_message(self._auth_stub.serverInfo, Empty())
        await version_check(server_info)

        if self.__broker_settings['ssl_context']:
            ssl_info = f'using {ssl.OPENSSL_VERSION}'
        else:
            ssl_info = 'no SSL'

        connection_banner = (
            f"connected to Momotor broker version {server_info.version} "
            f"at {self.__broker_settings['host']}:{self.__broker_settings['port']}, "
            f"remote protocol version {server_info.protoVersion}, {ssl_info}"
        )

        await async_logger.info(connection_banner)

    async def server_info(self) -> "ServerInfoResponse":
        """ Get the server info.

        A cached version of the server info is returned if the server info was retrieved less than
        :setting:`MOMOTOR_BROKER.INFO_MAX_AGE` seconds ago.

        :return: The server info response
        """
        async with self._server_info_lock:
            if not self._server_info or time.monotonic() - self._server_info_timestamp > self._server_info_max_age:
                await self._connect()
                await self._get_server_info()

        return self._server_info

    async def send_message(self, method_name: str, request: Message,
                           *, private_channel: bool = False, timeout: float = None) -> Message:
        """ Send a message to the broker's :py:class:`~momotor.rpc.proto.client_grpc.ClientStub` and await the response

        If authentication fails, tries to send the message again after a delay.

        :param method_name: Name of the gRPC method on the :py:class:`~momotor.rpc.proto.client_grpc.ClientStub` to call
        :param request: gRPC request message to send
        :param private_channel: `True` to use a private channel
        :param timeout: Timeout in seconds. `None` for no timeout
        :return: The response message
        """
        loop = self.loop or asyncio.get_running_loop()
        while loop.is_running():
            try:
                async with self.get_stub(private_channel) as stub:
                    method = getattr(stub, method_name)
                    return await _retry_message(method, request, timeout)

            except AuthException:
                await self.disconnect(True)
                await asyncio.sleep(5)

    def fire_message(self, method_name: str, request: Message,
                     *, private_channel: bool = False, timeout: float = None):
        """ Fire a message to the broker: send the message and don't wait for the RPC completion

        :param method_name: Name of the gRPC method on the :py:class:`~momotor.rpc.proto.client_grpc.ClientStub` to call
        :param request: gRPC request message to send
        :param private_channel: `True` to use a private channel
        :param timeout: Timeout in seconds. `None` for no timeout
        """
        asyncio.ensure_future(self.send_message(method_name, request, private_channel=private_channel, timeout=timeout))\
            .add_done_callback(consume_task_result)

    async def multi_job_status_stream(self, *,
                                      private_channel: bool = False,
                                      connect_timeout: float = None,
                                      status_timeout: float = None) \
            -> collections.abc.AsyncIterable[JobStatusStream]:

        """ Async generator that connects to the
        :py:func:`~momotor.rpc.proto.client_grpc.ClientBase.multiJobStatusStream` client endpoint and yields the
        :py:class:`~momotor.rpc.proto.job_pb2.JobStatusStream` status messages

        :param private_channel: `True` to use a private channel
        :param connect_timeout: timeout (in seconds) to wait until connected. `None` for no timeout
        :param status_timeout: timeout (in seconds) to wait for next status message. `None` for no timeout
        """

        async with self.get_stub(private_channel) as stub:
            await async_logger.debug("RPC call multiJobStatusStream")
            async with stub.multiJobStatusStream.open(timeout=connect_timeout) as stream:
                try:
                    await asyncio.wait_for(stream.send_message(Empty(), end=True), timeout=connect_timeout)

                except (ConnectionError, StreamTerminatedError, UnexpectedEndOfStream) as exc:
                    await async_logger.error(f"RPC call multiJobStatusStream (send) connection interrupted: {exc}")
                    connected = False

                else:
                    connected = True

                while connected and stub == self._client_stub:
                    try:
                        try:
                            message = typing.cast(
                                JobStatusStream | None,
                                await asyncio.wait_for(stream.recv_message(), timeout=status_timeout)
                            )

                        except asyncio.TimeoutError:
                            await async_logger.debug(f"RPC call multiJobStatusStream recv timeout")
                            connected = False

                        else:
                            if message:
                                yield message

                    except AuthException:
                        await async_logger.error(f"RPC call multiJobStatusStream authentication error")
                        await self.disconnect(True)
                        connected = False

                    except asyncio.CancelledError:
                        await async_logger.debug(f"RPC call multiJobStatusStream cancelled")
                        connected = False

                    except (ConnectionError, StreamTerminatedError, UnexpectedEndOfStream) as exc:
                        await async_logger.error(f"RPC call multiJobStatusStream (recv) connection interrupted: {exc}")
                        connected = False

                try:
                    await async_logger.debug(f"RPC call multiJobStatusStream cancel stream")
                    await stream.cancel()
                    await async_logger.debug(f"RPC call multiJobStatusStream cancel stream done")
                except Exception as exc:
                    await async_logger.debug(f"RPC call multiJobStatusStream cancel stream failed: {exc}")

            await async_logger.debug("RPC call multiJobStatusStream done")
