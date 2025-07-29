from __future__ import annotations

import asyncio

from django.core.cache import caches
from django.utils.encoding import smart_str

from momotor.django.defaults import DEFAULT_CACHE_KEY
from momotor.django.token_store.memory import InMemoryTokenStore


class CachedTokenStore(InMemoryTokenStore):
    """ Token store that saves tokens in the cache
    """
    def __init__(self, settings, *, loop=None, executor=None):
        super().__init__(settings, loop=loop, executor=executor)
        self.key = settings.get('TOKEN_KEY', DEFAULT_CACHE_KEY).format(settings)
        self.cache = caches[settings.get('TOKEN_CACHE_NAME', 'default')]
        self.lock = asyncio.Lock()

    async def get(self) -> str | None:
        async with self.lock:
            token = await super().get()
            if token is None:
                token = await self._run_in_executor(self.cache.get, self.key)
                if token:
                    await super().set(token)

            return smart_str(token, strings_only=True)

    async def set(self, token: str):
        async with self.lock:
            await super().set(token)
            await self._run_in_executor(self.cache.set, self.key, token)

    async def delete(self):
        async with self.lock:
            await super().delete()
            await self._run_in_executor(self.cache.delete, self.key)
