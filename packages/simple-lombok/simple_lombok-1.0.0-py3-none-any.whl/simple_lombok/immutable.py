"""
Immutable data structure functionality for SimpleLombok.
Provides decorators for creating immutable classes and working with immutable objects.

This module contains decorators and utilities for creating and working with immutable
classes, similar to Lombok's @Value annotation in Java or Python's frozen dataclasses.
Immutable objects cannot be modified after initialization, which helps prevent bugs
related to unexpected state changes and makes code more predictable and thread-safe.

Available decorators:
    immutable: Makes a class immutable by preventing attribute modification after initialization.
    frozen_dataclass: Combines data_class and immutable decorators for a complete immutable data class.
    with_method: Adds 'with_*' methods to an immutable class for creating modified copies.

The module also provides an ImmutableError exception that is raised when attempting to
modify an immutable object.
"""
import functools
from typing import Any, Dict, List, Optional, Type, Union


class ImmutableError(Exception):
    """
    Exception raised when attempting to modify an immutable object.

    This exception is raised by the __setattr__ method of classes decorated with
    @immutable or @frozen_dataclass when an attempt is made to modify an attribute
    after the object has been fully initialized.

    Examples
    --------
    >>> @immutable
    ... class Person:
    ...     def __init__(self, name):
    ...         self.name = name
    ...
    >>> person = Person("John")
    >>> try:
    ...     person.name = "Alice"  # This will raise ImmutableError
    ... except ImmutableError as e:
    ...     print(str(e))
    Cannot modify attribute 'name' of immutable object
    """
    pass


def immutable(cls):
    """
    Decorator that makes a class immutable by preventing attribute modification after initialization.
    Similar to @Value in Lombok.

    This decorator modifies the class's __setattr__ and __init__ methods to prevent
    attribute modification after the object has been fully initialized. It also adds
    a __hash__ method if one doesn't already exist, making the immutable objects
    suitable for use as dictionary keys or in sets.

    The immutability is enforced by raising an ImmutableError when an attempt is made
    to modify any attribute after initialization.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with immutability enforcement.

    Examples
    --------
    >>> @immutable
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person = Person("John", 30)
    >>> person.name  # Reading attributes works normally
    'John'
    >>> try:
    ...     person.age = 31  # This will raise ImmutableError
    ... except ImmutableError:
    ...     print("Cannot modify immutable object")
    Cannot modify immutable object
    >>> # Immutable objects can be used as dictionary keys
    >>> data = {person: "Person data"}
    >>> person in data
    True
    """
    # Save the original __setattr__ method
    original_setattr = cls.__setattr__

    # Define a new __setattr__ method that prevents modification after initialization
    def __setattr__(self, name, value):
        if hasattr(self, '_immutable') and self._immutable:
            raise ImmutableError(f"Cannot modify attribute '{name}' of immutable object")
        original_setattr(self, name, value)

    # Save the original __init__ method
    original_init = cls.__init__

    # Define a new __init__ method that marks the object as immutable after initialization
    def __init__(self, *args, **kwargs):
        # Set _immutable to False during initialization
        original_setattr(self, '_immutable', False)
        # Call the original __init__
        original_init(self, *args, **kwargs)
        # Set _immutable to True after initialization
        original_setattr(self, '_immutable', True)

    # Replace the original methods with our new ones
    cls.__setattr__ = __setattr__
    cls.__init__ = __init__

    # Make the class hashable if it's not already
    if not hasattr(cls, '__hash__') or cls.__hash__ is None:
        def __hash__(self):
            return hash(tuple(getattr(self, attr) for attr in sorted(self.__dict__) if not attr.startswith('_')))
        cls.__hash__ = __hash__

    return cls


def frozen_dataclass(cls):
    """
    Decorator that combines data_class and immutable decorators.
    Similar to @Value in Lombok or @dataclass(frozen=True) in Python.

    This decorator applies both the data_class and immutable decorators to a class,
    creating an immutable data class with automatically generated __eq__, __hash__,
    __str__, and __repr__ methods. The resulting class behaves like a frozen dataclass
    in Python's standard library, but with more flexibility in how it's defined.

    The decorator applies data_class first to add the special methods, then applies
    immutable to prevent modification after initialization.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with data class methods and immutability enforcement.

    Examples
    --------
    >>> @frozen_dataclass
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> p1 = Person("John", 30)
    >>> p2 = Person("John", 30)
    >>> p1 == p2  # Equality comparison works
    True
    >>> print(p1)  # String representation is available
    Person(name='John', age=30)
    >>> try:
    ...     p1.name = "Alice"  # This will raise ImmutableError
    ... except ImmutableError:
    ...     print("Cannot modify frozen dataclass")
    Cannot modify frozen dataclass
    """
    from simple_lombok.data_class import data_class

    # Apply data_class decorator first
    cls = data_class(cls)

    # Then apply immutable decorator
    cls = immutable(cls)

    return cls


def with_method(cls):
    """
    Decorator that adds 'with_*' methods to an immutable class for creating modified copies.
    Similar to the 'with' methods in immutable collections or withers in Lombok.

    This decorator adds a 'with_attribute_name' method for each non-private attribute
    in the class. These methods create and return a new instance of the class with the
    specified attribute modified, while leaving the original instance unchanged.

    This pattern is commonly used with immutable objects to provide a way to "modify"
    them by creating new instances with the desired changes, preserving immutability.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with added 'with_*' methods for each non-private attribute.

    Examples
    --------
    >>> @immutable
    ... @with_method
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person1 = Person("John", 30)
    >>> # Create a new instance with modified name
    >>> person2 = person1.with_name("Alice")
    >>> person1.name  # Original instance is unchanged
    'John'
    >>> person2.name  # New instance has the modified value
    'Alice'
    >>> # Create another new instance with modified age
    >>> person3 = person2.with_age(25)
    >>> person3.name
    'Alice'
    >>> person3.age
    25
    """
    # Get instance attributes from __init__ method
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        # Call the original __init__
        original_init(self, *args, **kwargs)

        # After initialization, add with_* methods for each attribute
        for attr_name in self.__dict__:
            if attr_name.startswith('_'):
                continue

            # Define a method that creates a new instance with the modified attribute
            def make_with_method(attr):
                def with_method(instance, value):
                    # Create a new instance
                    new_instance = cls.__new__(cls)

                    # Copy all attributes from the original instance
                    for name, val in instance.__dict__.items():
                        if name != '_immutable':  # Skip the immutability flag
                            setattr(new_instance, name, val)

                    # Set the new value for the specified attribute
                    setattr(new_instance, attr, value)

                    # Mark the new instance as immutable
                    setattr(new_instance, '_immutable', True)

                    return new_instance
                return with_method

            # Add the method to the class if it doesn't exist
            method_name = f'with_{attr_name}'
            if not hasattr(cls, method_name):
                setattr(cls, method_name, make_with_method(attr_name))

    # Replace the original __init__ with our new one
    cls.__init__ = new_init

    return cls
