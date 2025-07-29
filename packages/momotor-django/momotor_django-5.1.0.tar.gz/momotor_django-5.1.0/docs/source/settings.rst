.. _settings:

========
Settings
========

.. setting:: MOMOTOR_BROKER

``MOMOTOR_BROKER``
------------------

A dictionary with connection settings for the Momotor_ broker.

Example::

    MOMOTOR_BROKER = {
        'HOST': 'localhost',
        'PORT': 50052,
        'USE_SSL': True,

        'API_KEY': 'momotor-api-key',
        'API_SECRET': 'momotor-api-secret',

        'TOKEN_STORE_CLASS': 'momotor.django.token_store.model.ModelTokenStore',
    }

.. setting:: MOMOTOR_BROKER.HOST

``HOST``
~~~~~~~~

The dns name or ip address of the Momotor broker.

Default: ``localhost``

.. setting:: MOMOTOR_BROKER.PORT

``PORT``
~~~~~~~~

The tcp port the Momotor broker is listening too. If not provided, defaults to ``50051`` if
:setting:`USE_SSL <MOMOTOR_BROKER.USE_SSL>` is False, otherwise ``50052``

.. setting:: MOMOTOR_BROKER.USE_SSL

``USE_SSL``
~~~~~~~~~~~

Indicates whether to use SSL when connecting to the broker. There are three possible values:

* ``yes`` indicates an SSL connection is required. The certificate provided by the broker will be validated.
* ``insecure`` indicates an SSL connection is required, but the certificate will not be validated. Use this when the broker uses a self-signed certificate.
* ``no`` indicates SSL should not be used (not recommended).

.. setting:: MOMOTOR_BROKER.API_KEY
.. setting:: MOMOTOR_BROKER.API_SECRET

``API_KEY`` and ``API_SECRET``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The key and secret to use to authenticate to the broker with.

.. setting:: MOMOTOR_BROKER.TOKEN_STORE_CLASS

``TOKEN_STORE_CLASS``
~~~~~~~~~~~~~~~~~~~~~

The token store class to use. See the :ref:`token_store` section for more information.

Available token stores classes are:

* :py:class:`momotor.django.token_store.dummy.DummyTokenStore`
* :py:class:`momotor.django.token_store.memory.InMemoryTokenStore`
* :py:class:`momotor.django.token_store.cache.CachedTokenStore`
* :py:class:`momotor.django.token_store.model.ModelTokenStore`

Default: ``momotor.django.token_store.model.ModelTokenStore``

.. setting:: MOMOTOR_BROKER.INFO_MAX_AGE

``INFO_MAX_AGE``
~~~~~~~~~~~~~~~~

Server info is cached for this time.

Default: ``30``

.. setting:: MOMOTOR_BROKER.TOKEN_CACHE_NAME

``TOKEN_DATABASE_NAME``
~~~~~~~~~~~~~~~~~~~~~~~

Only used when the :setting:`TOKEN_STORE_CLASS <MOMOTOR_BROKER.TOKEN_STORE_CLASS>` setting is set to
:py:class:`momotor.django.token_store.model.ModelTokenStore`.

Name of the database where the model to store the Momotor tokens is created. This refers to the name of the
database as defined in the default :setting:`DATABASES <django:DATABASES>` Django setting.

Default: ``default``

``TOKEN_CACHE_NAME``
~~~~~~~~~~~~~~~~~~~~

Only used when the :setting:`TOKEN_STORE_CLASS <MOMOTOR_BROKER.TOKEN_STORE_CLASS>` setting is set to
:py:class:`momotor.django.token_store.cache.CachedTokenStore`.

Name of the cache where tokens are stored. This refers to the name of the
cache as defined in the default :setting:`CACHES <django:CACHES>` Django setting.

Default: ``default``

.. setting:: MOMOTOR_BROKER.TOKEN_KEY

``TOKEN_KEY``
~~~~~~~~~~~~~

Only used when the :setting:`TOKEN_STORE_CLASS <MOMOTOR_BROKER.TOKEN_STORE_CLASS>` setting is set to
:py:class:`momotor.django.token_store.cache.CachedTokenStore`.

Cache key for the tokens.

The key is formatted using the :setting:`MOMOTOR_BROKER` dictionary, so any
value in the settings dictionary can be used to make the key unique.

Default: ``momotor-broker-auth-token-{[API_KEY]}``

.. setting:: MOMOTOR_BROKER.TOKEN_DATABASE_NAME
