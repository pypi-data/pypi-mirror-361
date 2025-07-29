.. _token_store:

===========
Token Store
===========

A token store is required to save the session token received from the Momotor broker.

The token store to use is configured using the :setting:`MOMOTOR_BROKER.TOKEN_STORE_CLASS` settings.

Provided classes
================

There are four token store implementations provided:

* .. py:class:: momotor.django.token_store.dummy.DummyTokenStore

  Does not store the token.
  A new session to the broker is created every time.

  Useful for testing.

* .. py:class:: momotor.django.token_store.memory.InMemoryTokenStore

  Stores the token in memory for the current thread.
  A separate session to Momotor is created for each thread and process.

  Not very useful in itself, but used as base class for more complex token stores, where the in-memory token is used
  to reduce the number of times an external resource needs to be accessed. Only when the token does not exist
  in-memory, the external resource is accessed.

* .. py:class:: momotor.django.token_store.cache.CachedTokenStore

  Stores the token in Django's :doc:`cache <django:topics/cache>`.
  This store adds two more settings to the :setting:`MOMOTOR_BROKER` dictionary:
  :setting:`TOKEN_CACHE_NAME <MOMOTOR_BROKER.TOKEN_CACHE_NAME>` and :setting:`TOKEN_KEY <MOMOTOR_BROKER.TOKEN_KEY>`.

* .. py:class:: momotor.django.token_store.model.ModelTokenStore

  Stores the token in a Django :doc:`database model <django:topics/db/models>`.
  This store adds one more setting to the :setting:`MOMOTOR_BROKER` dictionary:
  :setting:`TOKEN_DATABASE_NAME <MOMOTOR_BROKER.TOKEN_CACHE_NAME>`

Providing a custom token store
==============================

A custom token store can be provided, for example when the Django app is not using Django's default database and cache
mechanisms.

The custom token store should subclass from the abstract base class
:py:class:`~momotor.django.token_store.base.BaseTokenStore`

.. autoclass:: momotor.django.token_store.base.BaseTokenStore
   :members:
   :private-members:
