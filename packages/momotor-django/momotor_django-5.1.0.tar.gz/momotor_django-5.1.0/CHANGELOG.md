# CHANGELOG


## v5.1.0 (2025-07-10)

### Chores

- Small typing annotation fix
  ([`5322604`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/532260448235f73ad9914a8e950fa7364d354afe))

- Update pytest options
  ([`1e98c91`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/1e98c913e7e9ad860098570f022a27e23da7b574))

### Features

- Update to Django 5.2
  ([`aec7355`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/aec7355beb4b77797c37987c04e21f43949689df))


## v5.0.0 (2024-04-16)


## v5.0.0-rc.3 (2024-04-04)

### Features

- Mark Django 5.0 as supported version and remove support for versions older than 4.2
  ([`23af47a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/23af47ab39559c78a4bbd97bc765d00fa0589273))

BREAKING CHANGE: Dropped support for Django < 4.2

### Breaking Changes

- Dropped support for Django < 4.2


## v5.0.0-rc.2 (2024-03-21)

### Bug Fixes

- Get local protocol library version using importlib.metadata
  ([`d0b8981`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/d0b89812b9cc501b65a61eeabbbce0b473923b16))

### Chores

- Update dependencies
  ([`db0d5ed`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/db0d5edd30968d7d0def9d97d7198b860f85ab50))

### Features

- Convert to PEP420 namespace packages
  ([`78378e7`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/78378e7fe7289c5a42cf61c603bcea09c2273226))

requires all other momotor.* packages to be PEP420 too

BREAKING CHANGE: convert to PEP420 namespace packages

### Refactoring

- Replace all deprecated uses from typing (PEP-0585)
  ([`2ab5026`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/2ab50260fc3fb4b4841edbd9448d998e5249748c))

### Breaking Changes

- Convert to PEP420 namespace packages


## v5.0.0-rc.1 (2024-02-05)

### Chores

- Update project
  ([`b16d268`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/b16d2686cdfdd4cd59f4b9f83cd21747bb322913))

- Update setup.py
  ([`7fb8246`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/7fb8246d41fbe038cc45c02bbc0715d985a5ace7))

### Features

- Drop Python 3.8 support, test with Python 3.12
  ([`fc3763f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/fc3763f339af6edace5d91fbb0f3a2421e64069e))

BREAKING CHANGE: Requires Python 3.9+

### Refactoring

- Update type hints for Python 3.9
  ([`c5102e5`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/c5102e5b8c46d93449fbdd1fa571a5b1d3a50752))

### Breaking Changes

- Requires Python 3.9+


## v4.1.0 (2023-06-09)

### Features

- Update Django version pin (closes #8)
  ([`326a37e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/326a37e2bef639c72166c273039a4766397c9200))


## v4.0.0 (2022-12-09)

### Bug Fixes

- Replace use of `asyncio.get_event_loop`
  ([`2df42b9`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/2df42b97f3115968eb3ae7ebf7fd2acba09f6aa8))

### Chores

- Clean up project file
  ([`b7d8403`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/b7d8403c8e424f6e692a25e33e9cc7412e0b9972))

- Default_app_config is removed
  ([`61d6783`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/61d6783dd39f1b3e8f3994e0521c00bf200f824f))

- Link to documentation with the correct version number
  ([`a7d3c12`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/a7d3c124f4004e5479f5f38e7e29cca12a755f68))

- Remove inactive debugging print statements
  ([`556c53c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/556c53c6714e92e5e57aa8ce6771d9b71349b3cd))

- Sync requirements.txt with setup.py
  ([`e595fe3`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/e595fe3d249c47386fe7eb1f0b3ef9f8618231cb))

### Features

- Drop deprecated features
  ([`b029869`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/b02986919a701444cb34d12328e6fee2984cb1d6))

BREAKING CHANGE: drop deprecated features

- Update versions pins
  ([`ee022f0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/ee022f0de6e836d447d97459877f423ca1c51df4))

* Add Django 4.0, 4.1 * Drop Django <3.2 * Drop Python 3.7

BREAKING CHANGE: Requires Django >=3.2, Python>=3.8

### Refactoring

- Specify return type of `BrokerConnection.multi_job_status_stream`
  ([`0be85e8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/0be85e8da1d5b1cd3e784ae1dca6ad1a91000920))

### Breaking Changes

- Drop deprecated features


## v3.2.1 (2021-10-01)

### Bug Fixes

- Mark momotor.django.log as deprecated
  ([`dfa36b0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/dfa36b09bf3937233d5bb3a97242f6375a420a52))

### Chores

- Update project files
  ([`8ea8cbc`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/8ea8cbccaa32cfd85696cdc7bad0bee02377708f))

- Update project files
  ([`c191715`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/c1917155588bfa54fb95e0420218738dfd280a02))

- Update project files
  ([`a5a33e3`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/a5a33e3e783362242abf7f6ed8462b1c614279ee))


## v3.2.0 (2021-05-20)

### Chores

- Add "Framework :: Django" classifiers [skip-ci]
  ([`02e4d2b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/02e4d2b6be1d44d714801f4d55bdd831dde3e00d))

- Update/move PyCharm module files
  ([`2993c6d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/2993c6db1a1e197f601fdc20f19216f1dbcf21a3))

### Features

- Support Django 3.2
  ([`3e49813`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/3e49813de1dd0a1f60bd161e8b20ddf33132981e))


## v3.1.1 (2020-10-23)

### Bug Fixes

- The loop parameter is deprecated
  ([`fa88665`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/fa8866535bb415a74f46c9c8a5d4ca556bb06b6d))


## v3.1.0 (2020-10-23)

### Chores

- Update Python SDK
  ([`8df6964`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/8df696425f58dd717bb3c19599989924d743cd13))

- Update Python version classifiers
  ([`346b098`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/346b0982976e07c16d89fb4cb61f87008519208a))

### Features

- Bump supported Django versions
  ([`0ca5a8f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/0ca5a8f330473a4351dab8349f5387f0eb77add6))


## v3.0.0 (2020-08-17)

### Features

- Changed minimum Python requirement to 3.7
  ([`33d150e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/33d150eef73e8047b83a96dadf842c1498a3d4aa))

BREAKING CHANGE: Requires Python 3.7 or higher

### Breaking Changes

- Requires Python 3.7 or higher


## v2.0.0 (2020-08-07)


## v1.4.2 (2020-06-30)

### Bug Fixes

- Python 3.6 compatibility
  ([`4ccc57c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/4ccc57c168f117501aac389d7393b9738b672223))

- Remove imports from `__init__.py` to prevent an "import storm" at load time
  ([`329e64f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/329e64f8d2cbd469a532f9be82f2992967fb5687))

BREAKING CHANGE: Moves `BrokerConnection` and `retry_connection` to `momotor.django.connection`.
  Update import statements

### Chores

- Update project
  ([`8ba1c40`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/8ba1c407fce80225ebf93be130f60e3c5882c09a))

### Breaking Changes

- Moves `BrokerConnection` and `retry_connection` to `momotor.django.connection`. Update import
  statements


## v1.4.1 (2020-06-08)

### Bug Fixes

- Add asgiref requirement to setup.py
  ([`15b17d6`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/15b17d68e357ab36d1d5307ac307645dbb86e42a))


## v1.4.0 (2020-06-08)

### Bug Fixes

- Typing of log_exception
  ([`67cc988`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/67cc988b5547d76e58736c7c7a6920a47a043b62))

- Use async logging where possible
  ([`5860355`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/58603552d010946318bddd8ed86d7f10912209ba))

### Features

- Add logging utils
  ([`d81a9a9`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/d81a9a995430aae49c11ddba887a0f1ff8c6b2cd))


## v1.3.2 (2020-06-05)

### Bug Fixes

- Correct Django version pin in setup.py
  ([`5fdd3c4`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/5fdd3c4847e9ad405ec8061c2164c9ffac0c6d90))


## v1.3.1 (2020-06-04)

### Bug Fixes

- Update Django version pin
  ([`67522c8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/67522c8b836a7f8568d1ec88065f95de02481322))

### Refactoring

- Correct imports for StreamTerminatedError and GRPCError
  ([`127c7ba`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/127c7bafff4d65354052140c56b3f186d39f7d0b))


## v1.3.0 (2020-04-17)

### Bug Fixes

- Lock external store to prevent race conditions
  ([`2f57a08`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/2f57a08a6a731d07260ee8aa665b347644d0c15e))

- Rename TOKEN_POOL_CLASS to TOKEN_STORE_CLASS. Still accepting old name with deprecation warning
  ([`57eab1a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/57eab1a9f0a9345299471b7241f755b9a05414f5))

- Set in-memory token when retrieved from external source
  ([`cfcf54f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/cfcf54f256e2065b36518a8da38cdce501239151))

### Features

- Allow model to be overridden in the model token store
  ([`01e77a0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/01e77a021b8fa9db347fadceb294e5e2c94af675))


## v1.2.0 (2019-10-15)

### Bug Fixes

- Add SSL exceptions to list of exceptions to retry
  ([`f1236ed`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/f1236ed646450b8f68c98cbce8c973a4ccff9798))

- Retry getting stub on connection errors
  ([`d58f7f4`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/d58f7f4e2dc69ce36a44d354d1a151d29f5194bb))

### Features

- Add SSL connection support
  ([`8c7cb4a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/8c7cb4a72114653cf6d8c8a88cf11bef0ab74c83))

### Refactoring

- Use contextlib.asynccontextmanager on Python>=3.7
  ([`a18ed12`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/a18ed12541d1c0c8873dcade50a89697a562afb0))


## v1.1.1 (2019-10-04)

### Bug Fixes

- Correct import for Message type
  ([`fc4ec2c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/fc4ec2ce7b6f21046935f02e372d54a7fc3c457a))


## v1.1.0 (2019-09-27)

### Features

- Add Django model field for Resources
  ([`1ecafaa`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/1ecafaafbe331c115ad92f593501fb455801851d))

### Refactoring

- Logging changes
  ([`dc59dd7`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/dc59dd75028dd9a301cd76ef1106d858b28bb68b))

* no uppercase initial characters

- **conn**: Use `momotor.rpc.auth.client.get_authenticated_channel`
  ([`99665c1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/99665c1cec928d40e6874e34719660136e80bff5))


## v1.0.0 (2019-05-23)

### Features

- Turn into a full Django app
  ([`f8908dd`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/f8908dd87d91c9895e7ffc3932ae762a468bde15))

* Configurable through settings * Multiple storage classes for the authentication tokens

BREAKING CHANGE: requires `MOMOTOR_BROKER` settings to be added

Example of a minimal `MOMOTOR_BROKER` configuration:

```python MOMOTOR_BROKER = { 'HOST': 'broker.example.org', 'PORT': 12345, 'API_KEY':
  '8w45teiutngewrgn3498eytjh3e', 'API_SECRET': '...', } ```

Existing `MOMOTOR_GEN2` setting can be renamed to `MOMOTOR_BROKER` and will work

### Breaking Changes

- Requires `MOMOTOR_BROKER` settings to be added


## v0.1.0 (2019-05-20)

### Features

- Export retry_connection
  ([`9865e37`](https://gitlab.tue.nl/momotor/engine-py3/momotor-django/-/commit/9865e37baa7d7282e33fe3450fc9408eed6151eb))


## v0.0.0 (2019-05-20)
