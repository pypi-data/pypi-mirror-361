from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured

from momotor.django.defaults import DEFAULT_TOKEN_STORE_CLASS
from momotor.django.models import MomotorToken


class MomotorTokenAdmin(admin.ModelAdmin):
    list_display = ('api_key', 'created')
    readonly_fields = ('api_key', 'token', 'created')


# Only register admin for the token store model if it is used
MOMOTOR_BROKER_SETTINGS = getattr(settings, 'MOMOTOR_BROKER', {})

if 'TOKEN_POOL_CLASS' in MOMOTOR_BROKER_SETTINGS:
    raise ImproperlyConfigured("MOMOTOR_BROKER.TOKEN_POOL_CLASS has been replaced by TOKEN_STORE_CLASS")

TOKEN_STORE_CLASS = MOMOTOR_BROKER_SETTINGS.get('TOKEN_STORE_CLASS', DEFAULT_TOKEN_STORE_CLASS)

if TOKEN_STORE_CLASS == DEFAULT_TOKEN_STORE_CLASS:
    admin.register(MomotorToken)(MomotorTokenAdmin)
