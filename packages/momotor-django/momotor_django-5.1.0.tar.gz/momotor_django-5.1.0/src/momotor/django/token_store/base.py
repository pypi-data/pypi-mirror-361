from __future__ import annotations

import asyncio
import collections.abc
import typing
from abc import ABC
from functools import partial

if typing.TYPE_CHECKING:
    from concurrent.futures import Executor


class BaseTokenStore(ABC):
    """ Abstract base class for token stores. The store is provided with the :setting:`MOMOTOR_BROKER` settings
    and an :std:doc:`asyncio loop <python:library/asyncio-eventloop>` and
    :py:class:`executor <python:concurrent.futures.Executor>`.

    :py:class:`~momotor.django.connection.BrokerConnection` uses this token store. Any additional keyword arguments
    provided to :py:class:`~momotor.django.connection.BrokerConnection` at creation are passed on to the token store
    to allow for addition parameters to custom token stores.

    :param settings: The :setting:`MOMOTOR_BROKER` dictionary from the settings
    :param loop: The :std:doc:`asyncio loop <python:library/asyncio-eventloop>` to use the `executor` with.
                 If `None`, uses the current active event loop.
    :param executor: An executor to run I/O blocking tasks on. If `None`, uses the current loop's default executor.
    :param kwargs: The additional token store arguments passed to
                   :py:class:`~momotor.django.connection.BrokerConnection`
    """

    def __init__(self, settings: dict, *, loop=None, executor: "Executor | None" = None, **kwargs):
        self.loop = loop or asyncio.get_running_loop()  #: The `loop` argument as provided to the constructor
        self.executor = executor  #: The `executor` argument as provided to the constructor
        self.settings = settings  #: The `settings` argument as provided to the constructor

    def _run_in_executor(self, func: collections.abc.Callable, *args, **kwargs):
        """ Run a function in the executor provided to __init__

        :param func: function to run
        :param args: arguments to the function
        :param kwargs: keyword arguments to the function
        :return: return value of the function
        """
        callback = partial(func, *args, **kwargs)
        return self.loop.run_in_executor(self.executor, callback)

    async def get(self) -> str | None:
        """ Get the current token from the store

        :return: The token. Or `None` if not currently authorized
        """
        raise NotImplementedError

    async def set(self, token: str):
        """ Set the token

        :param token: The token to save
        """
        raise NotImplementedError

    async def delete(self):
        """ Delete the token
        """
        raise NotImplementedError
