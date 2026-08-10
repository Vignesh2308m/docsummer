from dataclasses import fields
from typing import get_type_hints


def validate(obj):
    hints = get_type_hints(type(obj))

    for field in fields(obj):
        value = getattr(obj, field.name)
        expected = hints[field.name]

        if not isinstance(value, expected):
            raise TypeError(
                f"{field.name} must be "
                f"{expected}, got {type(value)}"
            )