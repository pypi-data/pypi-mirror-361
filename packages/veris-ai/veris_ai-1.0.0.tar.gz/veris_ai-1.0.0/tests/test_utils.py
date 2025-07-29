"""Tests for the utils module."""

from typing import Any, Union

import pytest

from veris_ai.utils import convert_to_type


class TestConvertToType:
    """Test the convert_to_type function."""

    @pytest.mark.parametrize(
        "value,target_type,expected",
        [
            # Primitive types
            ("42", int, 42),
            (42, str, "42"),
            ("3.14", float, 3.14),
            ("true", bool, True),
            ("false", bool, True),  # Non-empty strings are truthy
            ("", bool, False),
            (0, bool, False),
            (1, bool, True),
            # Any type
            ("test", Any, "test"),
            (42, Any, 42),
            ([1, 2, 3], Any, [1, 2, 3]),
            # List types
            ([1, 2, 3], list[int], [1, 2, 3]),
            (["1", "2"], list[int], [1, 2]),
            ([1.0, 2.5], list[float], [1.0, 2.5]),
            (["true", "false"], list[bool], [True, True]),  # Non-empty strings are truthy
            # Dict types
            ({"a": 1}, dict[str, int], {"a": 1}),
            ({"1": "2"}, dict[int, int], {1: 2}),
            ({"a": "1", "b": "2"}, dict[str, int], {"a": 1, "b": 2}),
            # Union types
            ("42", Union[int, str], 42),  # Tries int first
            ("abc", Union[int, str], "abc"),  # Falls back to str
            (42, Union[str, int], "42"),  # Tries str first
            ([1, 2], Union[list[int], str], [1, 2]),
            ("test", Union[list[int], str], "test"),
        ],
    )
    def test_convert_to_type_success(self, value, target_type, expected):
        """Test successful type conversions."""
        result = convert_to_type(value, target_type)
        assert result == expected
        assert isinstance(result, type(expected))

    def test_convert_to_type_list_invalid(self):
        """Test that non-list values raise ValueError for list types."""
        with pytest.raises(ValueError, match="Expected list but got <class 'str'>"):
            convert_to_type("not a list", list[int])

    def test_convert_to_type_dict_invalid(self):
        """Test that non-dict values raise ValueError for dict types."""
        with pytest.raises(ValueError, match="Expected dict but got <class 'str'>"):
            convert_to_type("not a dict", dict[str, int])

    def test_convert_to_type_union_all_fail(self):
        """Test that Union conversion raises ValueError when all types fail."""
        with pytest.raises(ValueError, match="Could not convert abc to any of the union types"):
            convert_to_type("abc", Union[int, float])

    def test_convert_to_type_custom_class(self):
        """Test conversion to custom classes."""

        class CustomClass:
            def __init__(self, value):
                self.value = value

        result = convert_to_type("test", CustomClass)
        assert isinstance(result, CustomClass)
        assert result.value == "test"

    def test_convert_to_type_custom_class_with_kwargs(self):
        """Test conversion to custom classes using kwargs."""

        class CustomClass:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

        data = {"name": "John", "age": 30}
        result = convert_to_type(data, CustomClass)
        assert isinstance(result, CustomClass)
        assert result.name == "John"
        assert result.age == 30

    def test_convert_to_type_nested_structures(self):
        """Test conversion of nested data structures."""
        # Nested list
        value = [["1", "2"], ["3", "4"]]
        result = convert_to_type(value, list[list[int]])
        assert result == [[1, 2], [3, 4]]

        # Dict with list values
        value = {"a": ["1", "2"], "b": ["3", "4"]}
        result = convert_to_type(value, dict[str, list[int]])
        assert result == {"a": [1, 2], "b": [3, 4]}

        # List of dicts
        value = [{"a": "1"}, {"b": "2"}]
        result = convert_to_type(value, list[dict[str, int]])
        assert result == [{"a": 1}, {"b": 2}]
