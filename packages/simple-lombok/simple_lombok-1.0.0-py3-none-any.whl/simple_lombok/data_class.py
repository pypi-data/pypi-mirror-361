"""
Data class functionality for SimpleLombok.
Provides decorators for automatically generating common methods like __eq__, __hash__, __str__, and __repr__.

This module contains decorators that can be applied to classes to automatically generate
common special methods, similar to Lombok's data class annotations in Java or Python's
built-in dataclasses. These decorators help reduce boilerplate code by automatically
implementing methods that are typically repetitive and follow a standard pattern.

Available decorators:
    data_class: Adds __eq__, __hash__, __str__, and __repr__ methods to a class.
    equals_and_hash_code: Adds __eq__ and __hash__ methods to a class.
    to_string: Adds __str__ and __repr__ methods to a class.

The generated methods operate on all non-private attributes (those not starting with '_')
of the class instances, making the classes behave like proper data containers.
"""
import inspect
from functools import wraps


def data_class(cls):
    """
    Decorator that adds __eq__, __hash__, __str__, and __repr__ methods to a class.
    Similar to @Data in Lombok or @dataclass in Python.

    This decorator adds four special methods to the decorated class:
    - __eq__: Enables equality comparison between instances based on their attributes
    - __hash__: Makes instances hashable, allowing them to be used as dictionary keys
    - __str__: Provides a human-readable string representation
    - __repr__: Provides a developer-friendly string representation

    All methods operate on non-private attributes (those not starting with '_').
    The decorator only adds methods that don't already exist in the class or that
    are inherited directly from object without overriding.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with added special methods.

    Examples
    --------
    >>> @data_class
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> p1 = Person("John", 30)
    >>> p2 = Person("John", 30)
    >>> p3 = Person("Alice", 25)
    >>> p1 == p2  # True, same attribute values
    True
    >>> p1 == p3  # False, different attribute values
    False
    >>> print(p1)  # Person(name='John', age=30)
    Person(name='John', age=30)
    >>> {p1: "Person 1"}  # Can be used as a dictionary key
    {Person(name='John', age=30): 'Person 1'}
    """
    # Define __eq__ method
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        # Compare all non-private attributes
        for attr in self.__dict__:
            if not attr.startswith('_'):
                if getattr(self, attr) != getattr(other, attr):
                    return False
        return True

    # Define __hash__ method
    def __hash__(self):
        # Hash all non-private attributes
        attrs = tuple(getattr(self, attr) for attr in sorted(
            attr for attr in self.__dict__ if not attr.startswith('_')
        ))
        return hash(attrs)

    # Define __str__ method
    def __str__(self):
        # Format all non-private attributes
        attrs = ', '.join(
            f"{attr}={getattr(self, attr)!r}" 
            for attr in self.__dict__ if not attr.startswith('_')
        )
        return f"{self.__class__.__name__}({attrs})"

    # Define __repr__ method
    def __repr__(self):
        # Format all non-private attributes
        attrs = ', '.join(
            f"{attr}={getattr(self, attr)!r}" 
            for attr in self.__dict__ if not attr.startswith('_')
        )
        return f"{self.__class__.__name__}({attrs})"

    # Add methods to the class if they don't already exist
    if not hasattr(cls, '__eq__') or cls.__eq__ is object.__eq__:
        cls.__eq__ = __eq__

    if not hasattr(cls, '__hash__') or cls.__hash__ is object.__hash__:
        cls.__hash__ = __hash__

    if not hasattr(cls, '__str__') or cls.__str__ is object.__str__:
        cls.__str__ = __str__

    if not hasattr(cls, '__repr__') or cls.__repr__ is object.__repr__:
        cls.__repr__ = __repr__

    return cls


def equals_and_hash_code(cls):
    """
    Decorator that adds __eq__ and __hash__ methods to a class.
    Similar to @EqualsAndHashCode in Lombok.

    This decorator adds two special methods to the decorated class:
    - __eq__: Enables equality comparison between instances based on their attributes
    - __hash__: Makes instances hashable, allowing them to be used as dictionary keys

    Both methods operate on non-private attributes (those not starting with '_').
    The decorator only adds methods that don't already exist in the class or that
    are inherited directly from object without overriding.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with added __eq__ and __hash__ methods.

    Examples
    --------
    >>> @equals_and_hash_code
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> p1 = Person("John", 30)
    >>> p2 = Person("John", 30)
    >>> p3 = Person("Alice", 25)
    >>> p1 == p2  # True, same attribute values
    True
    >>> p1 == p3  # False, different attribute values
    False
    >>> {p1: "Person 1"}  # Can be used as a dictionary key
    {Person("John", 30): 'Person 1'}
    """
    # Define __eq__ method
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        # Compare all non-private attributes
        for attr in self.__dict__:
            if not attr.startswith('_'):
                if getattr(self, attr) != getattr(other, attr):
                    return False
        return True

    # Define __hash__ method
    def __hash__(self):
        # Hash all non-private attributes
        attrs = tuple(getattr(self, attr) for attr in sorted(
            attr for attr in self.__dict__ if not attr.startswith('_')
        ))
        return hash(attrs)

    # Add methods to the class if they don't already exist
    if not hasattr(cls, '__eq__') or cls.__eq__ is object.__eq__:
        cls.__eq__ = __eq__

    if not hasattr(cls, '__hash__') or cls.__hash__ is object.__hash__:
        cls.__hash__ = __hash__

    return cls


def to_string(cls):
    """
    Decorator that adds __str__ and __repr__ methods to a class.
    Similar to @ToString in Lombok.

    This decorator adds two special methods to the decorated class:
    - __str__: Provides a human-readable string representation
    - __repr__: Provides a developer-friendly string representation

    Both methods format the class name followed by all non-private attributes
    (those not starting with '_') and their values in a readable format.
    The decorator only adds methods that don't already exist in the class or that
    are inherited directly from object without overriding.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with added __str__ and __repr__ methods.

    Examples
    --------
    >>> @to_string
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person = Person("John", 30)
    >>> print(person)  # Human-readable string representation
    Person(name='John', age=30)
    >>> person  # Developer-friendly representation in interactive console
    Person(name='John', age=30)
    """
    # Define __str__ method
    def __str__(self):
        # Format all non-private attributes
        attrs = ', '.join(
            f"{attr}={getattr(self, attr)!r}" 
            for attr in self.__dict__ if not attr.startswith('_')
        )
        return f"{self.__class__.__name__}({attrs})"

    # Define __repr__ method
    def __repr__(self):
        # Format all non-private attributes
        attrs = ', '.join(
            f"{attr}={getattr(self, attr)!r}" 
            for attr in self.__dict__ if not attr.startswith('_')
        )
        return f"{self.__class__.__name__}({attrs})"

    # Add methods to the class if they don't already exist
    if not hasattr(cls, '__str__') or cls.__str__ is object.__str__:
        cls.__str__ = __str__

    if not hasattr(cls, '__repr__') or cls.__repr__ is object.__repr__:
        cls.__repr__ = __repr__

    return cls
