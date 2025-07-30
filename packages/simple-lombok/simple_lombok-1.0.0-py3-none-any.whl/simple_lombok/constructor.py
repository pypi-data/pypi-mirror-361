"""
Constructor functionality for SimpleLombok.
Provides decorators for automatically generating constructors with various configurations.

This module contains decorators that can be applied to classes to automatically generate
constructor methods with different behaviors, similar to Lombok's constructor annotations
in Java. These decorators help reduce boilerplate code by automatically handling the
initialization of class attributes.

Available decorators:
    all_args_constructor: Generates a constructor that accepts all fields as arguments.
    no_args_constructor: Generates a constructor with no arguments.
    required_args_constructor: Generates a constructor accepting only required fields.
    builder: Adds a builder pattern to a class for flexible object creation.
"""
import inspect
from functools import wraps


def all_args_constructor(cls):
    """
    Decorator that generates a constructor accepting all fields as arguments.
    Similar to @AllArgsConstructor in Lombok.

    This decorator modifies the class's __init__ method to accept both positional and
    keyword arguments for all fields defined in the class's type annotations. It preserves
    the original __init__ method's behavior by calling it first, then sets attributes
    based on the provided arguments.

    Positional arguments are assigned to fields in the order they appear in the class's
    annotations. Keyword arguments are assigned to fields with matching names.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with an enhanced constructor.

    Examples
    --------
    >>> @all_args_constructor
    ... class Person:
    ...     name: str
    ...     age: int
    ...
    >>> person = Person("John", 30)
    >>> person.name
    'John'
    >>> person.age
    30
    >>> person = Person(age=25, name="Alice")
    >>> person.name
    'Alice'
    >>> person.age
    25
    """
    # Get the original __init__ method if it exists
    original_init = cls.__init__

    # Define a new __init__ method
    def __init__(self, *args, **kwargs):
        # Call the original __init__ with no arguments
        original_init(self)

        # Get class attributes from annotations if available
        annotations = getattr(cls, '__annotations__', {})
        attr_names = list(annotations.keys())

        # Process positional arguments
        for i, arg in enumerate(args):
            if i < len(attr_names):
                setattr(self, attr_names[i], arg)
            else:
                break

        # Process keyword arguments
        for key, value in kwargs.items():
            if key in annotations or hasattr(cls, key):
                setattr(self, key, value)

    # Replace the original __init__ with our new one
    cls.__init__ = __init__

    return cls


def no_args_constructor(cls):
    """
    Decorator that generates a constructor with no arguments.
    Similar to @NoArgsConstructor in Lombok.

    This decorator modifies the class's __init__ method to initialize all annotated
    fields with None values. It preserves the original __init__ method's behavior
    by calling it first, then initializes all fields defined in the class's type
    annotations.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with a no-args constructor.

    Examples
    --------
    >>> @no_args_constructor
    ... class Person:
    ...     name: str
    ...     age: int
    ...
    >>> person = Person()
    >>> person.name is None
    True
    >>> person.age is None
    True
    """
    # Get the original __init__ method if it exists
    original_init = cls.__init__

    # Define a new __init__ method
    def __init__(self, *args, **kwargs):
        # Call the original __init__ with no arguments
        original_init(self)

        # Get class attributes from annotations if available
        annotations = getattr(cls, '__annotations__', {})

        # Set default values for all attributes
        for attr in annotations:
            setattr(self, attr, None)

    # Replace the original __init__ with our new one
    cls.__init__ = __init__

    return cls


def required_args_constructor(cls):
    """
    Decorator that generates a constructor accepting required fields as arguments.
    Similar to @RequiredArgsConstructor in Lombok.

    This decorator modifies the class's __init__ method to accept arguments only for
    fields that don't have default values (required fields). It preserves the original
    __init__ method's behavior by calling it first, then sets attributes based on the
    provided arguments.

    Required fields are identified as those that are defined in the class's type
    annotations but don't have default values assigned at the class level.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with a constructor that accepts only required fields.

    Examples
    --------
    >>> @required_args_constructor
    ... class Person:
    ...     name: str  # Required field (no default value)
    ...     age: int = 0  # Optional field (has default value)
    ...
    >>> person = Person("John")
    >>> person.name
    'John'
    >>> # age is not set by the constructor since it has a default value
    >>> person = Person(name="Alice")
    >>> person.name
    'Alice'
    """
    # Get the original __init__ method if it exists
    original_init = cls.__init__

    # Define a new __init__ method
    def __init__(self, *args, **kwargs):
        # Call the original __init__ with no arguments
        original_init(self)

        # Get class attributes from annotations if available
        annotations = getattr(cls, '__annotations__', {})

        # Identify required fields (those without default values)
        required_fields = []
        for attr in annotations:
            if not hasattr(cls, attr):
                required_fields.append(attr)

        # Process positional arguments for required fields
        for i, arg in enumerate(args):
            if i < len(required_fields):
                setattr(self, required_fields[i], arg)
            else:
                break

        # Process keyword arguments for required fields
        for key, value in kwargs.items():
            if key in required_fields:
                setattr(self, key, value)

    # Replace the original __init__ with our new one
    cls.__init__ = __init__

    return cls


def builder(cls):
    """
    Decorator that adds a builder pattern to a class.
    Similar to @Builder in Lombok.

    This decorator adds a builder() class method to the decorated class, which returns
    a Builder instance. The Builder class provides fluent setter methods for each field
    defined in the class's type annotations, allowing for a more readable and flexible
    way to create instances of the class.

    The builder pattern is particularly useful when a class has many fields, some of
    which might be optional, making constructor calls with many parameters hard to read.

    Parameters
    ----------
    cls : type
        The class to be decorated.

    Returns
    -------
    type
        The decorated class with a builder() method that returns a Builder instance.

    Examples
    --------
    >>> @builder
    ... class Person:
    ...     name: str
    ...     age: int
    ...     address: str
    ...
    >>> person = Person.builder().name("John").age(30).address("123 Main St").build()
    >>> person.name
    'John'
    >>> person.age
    30
    >>> person.address
    '123 Main St'
    """
    # Get class attributes from annotations if available
    annotations = getattr(cls, '__annotations__', {})

    # Create a builder class
    class Builder:
        """
        Builder class for creating instances of the decorated class.

        This class provides a fluent interface for setting field values and
        finally building an instance of the decorated class.
        """
        def __init__(self):
            """
            Initialize a new Builder instance.

            Creates an empty dictionary to store attribute values.
            """
            self._attrs = {}

        def __getattr__(self, name):
            """
            Dynamically create setter methods for each field in the decorated class.

            This method is called when an attribute is not found on the Builder instance.
            If the attribute name matches a field in the decorated class, it returns a
            setter method for that field.

            Parameters
            ----------
            name : str
                The name of the attribute being accessed.

            Returns
            -------
            callable
                A setter method for the field if it exists in the decorated class.

            Raises
            ------
            AttributeError
                If the attribute name does not match any field in the decorated class.
            """
            if name in annotations:
                def setter(value):
                    self._attrs[name] = value
                    return self
                return setter
            raise AttributeError(f"Builder has no attribute {name}")

        def build(self):
            """
            Build and return an instance of the decorated class.

            Creates a new instance of the decorated class and sets all the attributes
            that were configured through the builder.

            Returns
            -------
            object
                An instance of the decorated class with the configured attributes.
            """
            instance = cls()
            for name, value in self._attrs.items():
                setattr(instance, name, value)
            return instance

    # Add a builder method to the class
    @classmethod
    def builder(cls):
        """
        Create a new Builder instance for this class.

        This class method provides access to the Builder pattern for creating
        instances of this class in a fluent, readable way.

        Returns
        -------
        Builder
            A new Builder instance that can be used to create instances of this class.

        Examples
        --------
        >>> instance = MyClass.builder().field1(value1).field2(value2).build()
        """
        return Builder()

    cls.builder = builder

    return cls
