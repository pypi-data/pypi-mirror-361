from __future__ import annotations

import asyncio

from django.core.exceptions import ObjectDoesNotExist

from momotor.django.models import MomotorToken
from momotor.django.token_store.memory import InMemoryTokenStore


class ModelTokenStore(InMemoryTokenStore):
    """ Token store that saves tokens in a model in the database
    """
    def __init__(self, settings, *, loop=None, executor=None, token_model=MomotorToken):
        super().__init__(settings, loop=loop, executor=executor)

        db = token_model.objects
        db_name = settings.get('TOKEN_DATABASE_NAME')
        self.db = db.using(db_name) if db_name else db
        self.api_key = settings['API_KEY']
        self.lock = asyncio.Lock()

    async def get(self) -> str | None:
        async with self.lock:
            token = await super().get()
            if token is None:
                try:
                    obj = await self._run_in_executor(self.db.get, api_key=self.api_key)
                except ObjectDoesNotExist:
                    pass
                else:
                    token = obj.token
                    await super().set(token)

            return token

    async def set(self, token: str):
        async with self.lock:
            old_token = await super().get()
            if token != old_token:
                await super().set(token)
                await self._run_in_executor(self.db.update_or_create, api_key=self.api_key, defaults={'token': token})

    async def delete(self):
        async with self.lock:
            db, api_key = self.db, self.api_key

            def _delete_impl():
                db.filter(api_key=api_key).delete()

            await super().delete()
            await self._run_in_executor(_delete_impl)
