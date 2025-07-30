"""
Validation functionality for SimpleLombok.
Provides decorators for validating class attributes.

This module contains decorators for adding validation to class attributes, similar to
validation annotations in Java frameworks like Lombok and Hibernate Validator. These
decorators help ensure data integrity by validating attribute values when they are set.

Available decorators:
    validate_field: Validates a field using a custom validator function.
    not_null: Ensures specified fields are not None.
    range_check: Ensures a numeric field is within a given range.
    string_length: Ensures a string field has a length within a given range.
    pattern: Ensures a string field matches a given regex pattern.

The module also provides a ValidationError exception that is raised when validation fails.

All validation decorators work by overriding the class's __setattr__ method to perform
validation checks before setting attribute values.
"""
import functools
import inspect
from typing import Callable, Any, Dict, List, Optional, Type, Union


class ValidationError(Exception):
    """
    Exception raised when validation fails.

    This exception is raised by the validation decorators when a field value
    does not meet the validation criteria. The exception message typically
    includes information about which field failed validation and why.

    Examples
    --------
    >>> @not_null('name')
    ... class Person:
    ...     def __init__(self, name=None):
    ...         self.name = name
    ...
    >>> try:
    ...     person = Person(None)  # This will raise ValidationError
    ... except ValidationError as e:
    ...     print(str(e))
    Field name cannot be None
    """
    pass


def validate_field(field_name: str, validator: Callable[[Any], bool], error_message: str = None):
    """
    Decorator that validates a specific field using the provided validator function.

    This decorator modifies the class's __setattr__ method to validate the specified
    field whenever it is set. If the validation fails, a ValidationError is raised
    with either the provided error message or a default message.

    Parameters
    ----------
    field_name : str
        The name of the field to validate.
    validator : callable
        A function that takes the field value and returns True if valid, False otherwise.
    error_message : str, optional
        Custom error message to use when validation fails. If not provided, a default
        message will be generated.

    Returns
    -------
    callable
        A decorator function that can be applied to a class.

    Examples
    --------
    >>> def is_positive(value):
    ...     return isinstance(value, (int, float)) and value > 0
    ...
    >>> @validate_field('age', is_positive, "Age must be positive")
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person = Person("John", 30)  # Valid age
    >>> try:
    ...     person.age = -5  # This will raise ValidationError
    ... except ValidationError as e:
    ...     print(str(e))
    Age must be positive
    """
    def decorator(cls):
        # Save the original __setattr__ method
        original_setattr = cls.__setattr__

        # Define a new __setattr__ method that validates the field
        def __setattr__(self, name, value):
            if name == field_name:
                if not validator(value):
                    msg = error_message or f"Validation failed for {field_name}: {value}"
                    raise ValidationError(msg)
            # Call the original __setattr__ method
            original_setattr(self, name, value)

        # Replace the original __setattr__ with our new one
        cls.__setattr__ = __setattr__

        return cls

    return decorator


def not_null(*field_names: str):
    """
    Decorator that ensures the specified fields are not None.

    This decorator modifies the class's __setattr__ method to check that the specified
    fields are not assigned None values. If an attempt is made to set any of these
    fields to None, a ValidationError is raised.

    Parameters
    ----------
    *field_names : str
        Variable number of field names that should not be None.

    Returns
    -------
    callable
        A decorator function that can be applied to a class.

    Examples
    --------
    >>> @not_null('name', 'email')
    ... class User:
    ...     def __init__(self, name, email, age=None):
    ...         self.name = name
    ...         self.email = email
    ...         self.age = age  # age can be None
    ...
    >>> user = User("John", "john@example.com")  # Valid
    >>> try:
    ...     user.name = None  # This will raise ValidationError
    ... except ValidationError as e:
    ...     print(str(e))
    Field name cannot be None
    """
    def decorator(cls):
        # Save the original __setattr__ method
        original_setattr = cls.__setattr__

        # Define a new __setattr__ method that validates the fields
        def __setattr__(self, name, value):
            if name in field_names and value is None:
                raise ValidationError(f"Field {name} cannot be None")
            # Call the original __setattr__ method
            original_setattr(self, name, value)

        # Replace the original __setattr__ with our new one
        cls.__setattr__ = __setattr__

        return cls

    return decorator


def range_check(field_name: str, min_value: Optional[Union[int, float]] = None, max_value: Optional[Union[int, float]] = None):
    """
    Decorator that ensures the specified numeric field is within the given range.

    This decorator validates that the specified field is a numeric value (int or float)
    and falls within the specified range. If either min_value or max_value is None,
    that bound is not checked. The validation is performed whenever the field is set,
    and a ValidationError is raised if the value is invalid.

    Parameters
    ----------
    field_name : str
        Name of the field to validate.
    min_value : int or float, optional
        Minimum allowed value (inclusive). If None, no minimum check is performed.
    max_value : int or float, optional
        Maximum allowed value (inclusive). If None, no maximum check is performed.

    Returns
    -------
    callable
        A decorator function that can be applied to a class.

    Examples
    --------
    >>> @range_check('age', min_value=0, max_value=120)
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person = Person("John", 30)  # Valid age
    >>> try:
    ...     person.age = 150  # This will raise ValidationError
    ... except ValidationError as e:
    ...     print(str(e))
    Field age must be between 0 and 120

    >>> @range_check('temperature', min_value=-273.15)  # Only minimum check
    ... class Thermometer:
    ...     def __init__(self, temperature):
    ...         self.temperature = temperature
    """
    def validator(value):
        if not isinstance(value, (int, float)):
            return False
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        return True

    error_message = f"Field {field_name} must be"
    if min_value is not None and max_value is not None:
        error_message += f" between {min_value} and {max_value}"
    elif min_value is not None:
        error_message += f" greater than or equal to {min_value}"
    elif max_value is not None:
        error_message += f" less than or equal to {max_value}"

    return validate_field(field_name, validator, error_message)


def string_length(field_name: str, min_length: Optional[int] = None, max_length: Optional[int] = None):
    """
    Decorator that ensures the specified string field has a length within the given range.

    This decorator validates that the specified field is a string and its length falls
    within the specified range. If either min_length or max_length is None, that bound
    is not checked. The validation is performed whenever the field is set, and a
    ValidationError is raised if the value is invalid.

    Parameters
    ----------
    field_name : str
        Name of the field to validate.
    min_length : int, optional
        Minimum allowed length (inclusive). If None, no minimum check is performed.
    max_length : int, optional
        Maximum allowed length (inclusive). If None, no maximum check is performed.

    Returns
    -------
    callable
        A decorator function that can be applied to a class.

    Examples
    --------
    >>> @string_length('username', min_length=3, max_length=20)
    ... class User:
    ...     def __init__(self, username):
    ...         self.username = username
    ...
    >>> user = User("john_doe")  # Valid username
    >>> try:
    ...     user.username = "a"  # This will raise ValidationError
    ... except ValidationError as e:
    ...     print(str(e))
    Field username must have a length between 3 and 20

    >>> @string_length('description', max_length=100)  # Only maximum check
    ... class Product:
    ...     def __init__(self, name, description=""):
    ...         self.name = name
    ...         self.description = description
    """
    def validator(value):
        if not isinstance(value, str):
            return False
        if min_length is not None and len(value) < min_length:
            return False
        if max_length is not None and len(value) > max_length:
            return False
        return True

    error_message = f"Field {field_name} must have a length"
    if min_length is not None and max_length is not None:
        error_message += f" between {min_length} and {max_length}"
    elif min_length is not None:
        error_message += f" greater than or equal to {min_length}"
    elif max_length is not None:
        error_message += f" less than or equal to {max_length}"

    return validate_field(field_name, validator, error_message)


def pattern(field_name: str, regex_pattern: str):
    """
    Decorator that ensures the specified string field matches the given regex pattern.

    This decorator validates that the specified field is a string and matches the
    provided regular expression pattern. The validation is performed whenever the
    field is set, and a ValidationError is raised if the value is invalid.

    The pattern is compiled once when the decorator is applied, improving performance
    when the validation is performed multiple times.

    Parameters
    ----------
    field_name : str
        Name of the field to validate.
    regex_pattern : str
        Regular expression pattern to match. This pattern is passed to re.compile().

    Returns
    -------
    callable
        A decorator function that can be applied to a class.

    Examples
    --------
    >>> @pattern('email', r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    ... class User:
    ...     def __init__(self, email):
    ...         self.email = email
    ...
    >>> user = User("john@example.com")  # Valid email
    >>> try:
    ...     user.email = "invalid-email"  # This will raise ValidationError
    ... except ValidationError as e:
    ...     print(str(e))
    Field email must match pattern ^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$

    >>> @pattern('phone', r'^\d{3}-\d{3}-\d{4}$')
    ... class Contact:
    ...     def __init__(self, name, phone=None):
    ...         self.name = name
    ...         if phone:
    ...             self.phone = phone  # Will be validated
    """
    import re
    compiled_pattern = re.compile(regex_pattern)

    def validator(value):
        if not isinstance(value, str):
            return False
        return bool(compiled_pattern.match(value))

    error_message = f"Field {field_name} must match pattern {regex_pattern}"

    return validate_field(field_name, validator, error_message)
