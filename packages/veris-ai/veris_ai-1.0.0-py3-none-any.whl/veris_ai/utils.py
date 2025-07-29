from contextlib import suppress
from typing import Any, Union, get_args, get_origin


def convert_to_type(value: object, target_type: type) -> object:
    """Convert a value to the specified type."""
    # Special case: Any type returns value as-is
    if target_type is Any:
        return value

    origin = get_origin(target_type)

    # Define conversion strategies for different type origins
    converters = {
        list: _convert_list,
        dict: _convert_dict,
        Union: _convert_union,
    }

    # Use appropriate converter based on origin
    if origin in converters:
        return converters[origin](value, target_type)

    # Handle primitives and custom types
    return _convert_simple_type(value, target_type)


def _convert_list(value: object, target_type: type) -> list:
    """Convert a value to a typed list."""
    if not isinstance(value, list):
        error_msg = f"Expected list but got {type(value)}"
        raise ValueError(error_msg)

    item_type = get_args(target_type)[0]
    return [convert_to_type(item, item_type) for item in value]


def _convert_dict(value: object, target_type: type) -> dict:
    """Convert a value to a typed dict."""
    if not isinstance(value, dict):
        error_msg = f"Expected dict but got {type(value)}"
        raise ValueError(error_msg)

    key_type, value_type = get_args(target_type)
    return {convert_to_type(k, key_type): convert_to_type(v, value_type) for k, v in value.items()}


def _convert_union(value: object, target_type: type) -> object:
    """Try to convert value to one of the union types."""
    union_types = get_args(target_type)

    for possible_type in union_types:
        with suppress(ValueError, TypeError):
            return convert_to_type(value, possible_type)

    error_msg = f"Could not convert {value} to any of the union types {union_types}"
    raise ValueError(error_msg)


def _convert_simple_type(value: object, target_type: type) -> object:
    """Convert to primitive or custom types."""
    # Primitive types
    if target_type in (str, int, float, bool):
        return target_type(value)

    # Custom types - try kwargs for dicts, then direct instantiation
    if isinstance(value, dict):
        with suppress(TypeError):
            return target_type(**value)

    return target_type(value)
