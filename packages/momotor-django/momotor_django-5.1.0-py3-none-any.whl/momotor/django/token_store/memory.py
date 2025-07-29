from __future__ import annotations

from momotor.django.token_store.base import BaseTokenStore


class InMemoryTokenStore(BaseTokenStore):
    """ Token store that saves tokens in memory
    """
    def __init__(self, settings, *, loop=None, executor=None):
        super().__init__(settings, loop=loop, executor=executor)
        self.__token = None

    async def get(self) -> str | None:
        return self.__token

    async def set(self, token: str):
        self.__token = token

    async def delete(self):
        self.__token = None
