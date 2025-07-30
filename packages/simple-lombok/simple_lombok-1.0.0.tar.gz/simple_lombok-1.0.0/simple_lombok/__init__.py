"""
SimpleLombok - A Python library inspired by Java's Lombok.

This library provides decorators and utilities to reduce boilerplate code in Python classes.
It includes functionality for automatically generating getters, setters, constructors, equality methods, string representations, and more.

Modules:
- `decorators`: Implements getter and setter decorators.
- `data_class`: Provides enhanced dataclass-like functionality.
- `constructor`: Includes utilities for generating constructors.
- `validation`: Offers field validation mechanisms.
- `immutable`: Enables immutable class creation.
- `logger`: Provides a simple logger for custom output

Usage Example:
    from simple_lombok import getter_and_setter

    @getter_and_setter
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    person = Person("John", 30)
    print(person.get_name())  # John
    person.set_age(35)
    print(person.get_age())  # 35
"""


# Import decorators for getters and setters
from simple_lombok.decorators import getter, setter, getter_and_setter

# Import data class functionality
from simple_lombok.data_class import data_class, equals_and_hash_code, to_string

# Import constructor functionality
from simple_lombok.constructor import (
    all_args_constructor,
    no_args_constructor,
    required_args_constructor,
    builder
)

# Import validation functionality
from simple_lombok.validation import (
    validate_field,
    not_null,
    range_check,
    string_length,
    pattern,
    ValidationError
)

# Import immutable functionality
from simple_lombok.immutable import (
    immutable,
    frozen_dataclass,
    with_method,
    ImmutableError
)

# Import class Logger
from simple_lombok.logger import Logger

__all__ = [
    # Decorators
    'getter',
    'setter',
    'getter_and_setter',

    # Data class
    'data_class',
    'equals_and_hash_code',
    'to_string',

    # Constructor
    'all_args_constructor',
    'no_args_constructor',
    'required_args_constructor',
    'builder',

    # Validation
    'validate_field',
    'not_null',
    'range_check',
    'string_length',
    'pattern',
    'ValidationError',

    # Immutable
    'immutable',
    'frozen_dataclass',
    'with_method',
    'ImmutableError',

    # Logger
    'Logger'
]
