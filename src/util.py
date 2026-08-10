from dataclasses import dataclass, fields

def validate(obj):
    for field in fields(obj):
        value = getattr(obj, field.name)

        if not isinstance(value, field.type):
            raise TypeError(
                f"{field.name} must be {field.type.__name__}, "
                f"got {type(value).__name__}"
            )