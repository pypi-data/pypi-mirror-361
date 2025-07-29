from django.core.exceptions import ValidationError
from django.forms import CharField

from momotor.shared.resources import Resources


class ResourcesFormField(CharField):
    def to_python(self, value):
        if isinstance(value, Resources):
            return value

        value = super().to_python(value)

        try:
            return Resources.from_string(value)
        except ValueError as e:
            raise ValidationError(str(e))

    def prepare_value(self, value):
        if isinstance(value, Resources):
            value = value.as_str(multiline=True)

        return super().prepare_value(value)
