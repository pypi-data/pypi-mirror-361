"""
Accessor method functionality for SimpleLombok.
Provides decorators for automatically generating getter and setter methods.

This module contains decorators that can be applied to classes to automatically generate
getter and setter methods for instance attributes. These decorators help reduce boilerplate
code by automatically implementing accessor methods that follow a standard naming convention.

Available decorators:
    getter_and_setter: Generates both getter and setter methods for all instance attributes.
    getter: Generates only getter methods for all instance attributes.
    setter: Generates only setter methods for all instance attributes.

The generated methods follow the naming convention get_attribute_name() and set_attribute_name()
and operate on all non-special attributes (those not starting with '__').
"""


def getter_and_setter(cls):
    """
    Decorator that automatically generates getter and setter methods for all instance attributes.
    Similar to @Getter and @Setter in Lombok when applied together.

    This decorator modifies the class's __init__ method to inspect the instance after
    initialization and dynamically create getter and setter methods for all non-special
    attributes (those not starting with '__'). The generated methods follow the naming
    convention get_attribute_name() and set_attribute_name().

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with added getter and setter methods for all instance attributes.

    Examples
    --------
    >>> @getter_and_setter
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person = Person("John", 30)
    >>> person.get_name()  # Automatically generated getter
    'John'
    >>> person.set_age(31)  # Automatically generated setter
    >>> person.get_age()
    31
    """
    # Save the original __init__
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        # Call the original __init__
        original_init(self, *args, **kwargs)

        # Create getters and setters for all instance attributes
        for attr_name in self.__dict__:
            if attr_name.startswith("__"):  # Skip special attributes
                continue

            # Create and bind getter
            def make_getter(attr):
                def getter(self):
                    return getattr(self, attr)
                return getter

            # Create and bind setter
            def make_setter(attr):
                def setter(self, value):
                    setattr(self, attr, value)
                return setter

            # Add methods to the instance if they don't already exist
            if not hasattr(self, f'get_{attr_name}'):
                setattr(self.__class__, f'get_{attr_name}', make_getter(attr_name))
            if not hasattr(self, f'set_{attr_name}'):
                setattr(self.__class__, f'set_{attr_name}', make_setter(attr_name))

    # Replace __init__ with our new version
    cls.__init__ = new_init

    return cls


def getter(cls):
    """
    Decorator that automatically generates getter methods for all instance attributes.
    Similar to @Getter in Lombok.

    This decorator modifies the class's __init__ method to inspect the instance after
    initialization and dynamically create getter methods for all non-special attributes
    (those not starting with '__'). The generated methods follow the naming convention
    get_attribute_name().

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with added getter methods for all instance attributes.

    Examples
    --------
    >>> @getter
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person = Person("John", 30)
    >>> person.get_name()  # Automatically generated getter
    'John'
    >>> person.get_age()
    30
    """
    # Save the original __init__
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        for attr_name in self.__dict__:
            if attr_name.startswith("__"):  # Skip special attributes
                continue

            # Create and bind getter
            def make_getter(attr):
                def getter(self):
                    return getattr(self, attr)

                return getter

            # Add methods to the instance if they don't already exist
            if not hasattr(self, f'get_{attr_name}'):
                setattr(self.__class__, f'get_{attr_name}', make_getter(attr_name))

    cls.__init__ = new_init

    return cls


def setter(cls):
    """
    Decorator that automatically generates setter methods for all instance attributes.
    Similar to @Setter in Lombok.

    This decorator modifies the class's __init__ method to inspect the instance after
    initialization and dynamically create setter methods for all non-special attributes
    (those not starting with '__'). The generated methods follow the naming convention
    set_attribute_name().

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with added setter methods for all instance attributes.

    Examples
    --------
    >>> @setter
    ... class Person:
    ...     def __init__(self, name, age):
    ...         self.name = name
    ...         self.age = age
    ...
    >>> person = Person("John", 30)
    >>> person.set_name("Alice")  # Automatically generated setter
    >>> person.name
    'Alice'
    >>> person.set_age(25)
    >>> person.age
    25
    """
    # Save the original __init__
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        for attr_name in self.__dict__:
            if attr_name.startswith("__"):  # Skip special attributes
                continue

            # Create and bind setter
            def make_setter(attr):
                def setter(self, value):
                    setattr(self, attr, value)

                return setter

            # Add methods to the instance if they don't already exist
            if not hasattr(self, f'set_{attr_name}'):
                setattr(self.__class__, f'set_{attr_name}', make_setter(attr_name))

    cls.__init__ = new_init

    return cls
