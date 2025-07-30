# SimpleLombok

SimpleLombok is a Python library inspired by Java's Lombok, designed to reduce boilerplate code in Python classes. It provides decorators and utilities for automatically generating getters, setters, constructors, equality methods, string representations, and more.

## Installation

```bash
# Coming soon to PyPI
pip install simple-lombok
```

For now, you can clone the repository and install it locally:

```bash
git clone https://github.com/yourusername/SimpleLombok.git
cd SimpleLombok
pip install -e .
```

## Features

SimpleLombok provides the following features:

### Accessor Methods
- `@getter`: Automatically generates getter methods for all instance attributes
- `@setter`: Automatically generates setter methods for all instance attributes
- `@getter_and_setter`: Generates both getter and setter methods

### Data Class Functionality
- `@data_class`: Adds `__eq__`, `__hash__`, `__str__`, and `__repr__` methods
- `@equals_and_hash_code`: Adds `__eq__` and `__hash__` methods
- `@to_string`: Adds `__str__` and `__repr__` methods

### Constructor Generation
- `@all_args_constructor`: Generates a constructor that accepts all fields as arguments
- `@no_args_constructor`: Generates a constructor with no arguments
- `@required_args_constructor`: Generates a constructor accepting only required fields
- `@builder`: Adds a builder pattern to a class for flexible object creation

### Validation
- `@validate_field`: Validates a field using a custom validator function
- `@not_null`: Ensures specified fields are not None
- `@range_check`: Ensures a numeric field is within a given range
- `@string_length`: Ensures a string field has a length within a given range
- `@pattern`: Ensures a string field matches a given regex pattern

### Immutability
- `@immutable`: Makes a class immutable by preventing attribute modification after initialization
- `@frozen_dataclass`: Combines `data_class` and `immutable` decorators
- `@with_method`: Adds 'with_*' methods to an immutable class for creating modified copies

### Logging
- `Logger`: A simple colored console logging utility

## Usage Examples

### Accessor Methods

```python
from simple_lombok import getter_and_setter

@getter_and_setter
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("John", 30)
print(person.get_name())  # John
person.set_age(31)
print(person.get_age())  # 31
```

### Data Class Functionality

```python
from simple_lombok import data_class

@data_class
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

p1 = Person("John", 30)
p2 = Person("John", 30)
print(p1 == p2)  # True
print(p1)  # Person(name='John', age=30)
```

### Constructor Generation

```python
from simple_lombok import all_args_constructor, builder

@all_args_constructor
class Person:
    name: str
    age: int

person = Person("John", 30)
print(person.name)  # John

@builder
class Address:
    street: str
    city: str
    zip_code: str

address = Address.builder().street("123 Main St").city("Anytown").zip_code("12345").build()
print(address.city)  # Anytown
```

### Validation

```python
from simple_lombok import not_null, range_check, string_length

@not_null('name')
@range_check('age', min_value=0, max_value=120)
@string_length('name', min_length=2, max_length=50)
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# This will raise ValidationError if name is None, age is outside 0-120, or name length is invalid
person = Person("John", 30)
```

### Immutability

```python
from simple_lombok import immutable, with_method

@immutable
@with_method
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person1 = Person("John", 30)
# person1.age = 31  # This would raise ImmutableError

# Create a new instance with modified age
person2 = person1.with_age(31)
print(person1.age)  # 30 (original instance is unchanged)
print(person2.age)  # 31
```

### Logging

```python
from simple_lombok import Logger

Logger.info("This is an info message")
Logger.error("This is an error message")
Logger.debug("This is a debug message")
Logger.warn("This is a warning message")
Logger.success("This is a success message")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.