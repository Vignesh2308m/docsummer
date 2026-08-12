from typing import Any, get_args, get_origin, get_type_hints, Union


def validate(obj: Any) -> None:
    hints = get_type_hints(type(obj))

    for field, expected in hints.items():
        value = getattr(obj, field)

        if not _matches(value, expected):
            raise TypeError(
                f"{type(obj).__name__}.{field} "
                f"expected {expected}, "
                f"got {type(value).__name__}"
            )


def _matches(value: Any, expected: Any) -> bool:
    origin = get_origin(expected)
    args = get_args(expected)

    # Normal types: str, int, list, etc.
    if origin is None:
        return isinstance(value, expected)

    # list[str]
    if origin is list:
        if not isinstance(value, list):
            return False

        if not args:
            return True

        return all(
            _matches(item, args[0])
            for item in value
        )

    # dict[str, str]
    if origin is dict:
        if not isinstance(value, dict):
            return False

        if len(args) != 2:
            return True

        key_type, value_type = args

        return all(
            _matches(key, key_type)
            and _matches(item, value_type)
            for key, item in value.items()
        )

    # Optional[T] / Union[T, None]
    if origin is Union:
        return any(
            _matches(value, arg)
            for arg in args
        )

    return isinstance(value, origin)