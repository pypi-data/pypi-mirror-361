from django.db import models
from django.forms import Textarea

from momotor.django.forms import ResourcesFormField
from momotor.shared.resources import Resources

__all__ = ['ResourcesField']


class ResourcesField(models.Field):
    def get_internal_type(self):
        return "TextField"

    def __init__(self, *args, **kwargs):
        defaults = {'blank': True}
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

    def to_python(self, value):
        if value is None:
            return Resources()
        elif isinstance(value, Resources):
            return value

        return Resources.from_string(str(value))

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_db_prep_value(self, value, connection, **kwargs):
        if value is None:
            return None
        elif isinstance(value, Resources):
            return value.as_str(compact=True)

        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': ResourcesFormField, 'widget': Textarea}
        defaults.update(**kwargs)
        return super().formfield(**defaults)
