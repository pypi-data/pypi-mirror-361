# Tests for the validation module
import pytest
from simple_lombok.validation import (
    validate_field, not_null, range_check, string_length, pattern, ValidationError
)

# Test for validate_field decorator
def test_validate_field():
    # Define a validator function
    def is_positive(value):
        return isinstance(value, (int, float)) and value > 0
    
    # Create a class with validation
    @validate_field('age', is_positive, "Age must be positive")
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Test valid value
    person = Person("John", 30)
    assert person.age == 30
    
    # Test invalid value in constructor
    with pytest.raises(ValidationError) as excinfo:
        Person("John", -5)
    assert "Age must be positive" in str(excinfo.value)
    
    # Test invalid value in assignment
    person = Person("John", 30)
    with pytest.raises(ValidationError) as excinfo:
        person.age = -5
    assert "Age must be positive" in str(excinfo.value)
    
    # Test that other attributes are not validated
    person.name = None  # Should not raise an error

# Test for not_null decorator
def test_not_null():
    @not_null('name', 'email')
    class User:
        def __init__(self, name, email, age=None):
            self.name = name
            self.email = email
            self.age = age
    
    # Test valid values
    user = User("John", "john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"
    
    # Test None value for non-validated field
    user.age = None
    assert user.age is None
    
    # Test None value for name in constructor
    with pytest.raises(ValidationError) as excinfo:
        User(None, "john@example.com")
    assert "Field name cannot be None" in str(excinfo.value)
    
    # Test None value for email in constructor
    with pytest.raises(ValidationError) as excinfo:
        User("John", None)
    assert "Field email cannot be None" in str(excinfo.value)
    
    # Test None value for name in assignment
    user = User("John", "john@example.com")
    with pytest.raises(ValidationError) as excinfo:
        user.name = None
    assert "Field name cannot be None" in str(excinfo.value)
    
    # Test None value for email in assignment
    with pytest.raises(ValidationError) as excinfo:
        user.email = None
    assert "Field email cannot be None" in str(excinfo.value)

# Test for range_check decorator
def test_range_check():
    # Test with both min and max
    @range_check('age', min_value=0, max_value=120)
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Test valid value
    person = Person("John", 30)
    assert person.age == 30
    
    # Test value at min boundary
    person.age = 0
    assert person.age == 0
    
    # Test value at max boundary
    person.age = 120
    assert person.age == 120
    
    # Test value below min
    with pytest.raises(ValidationError) as excinfo:
        person.age = -1
    assert "Field age must be between 0 and 120" in str(excinfo.value)
    
    # Test value above max
    with pytest.raises(ValidationError) as excinfo:
        person.age = 121
    assert "Field age must be between 0 and 120" in str(excinfo.value)
    
    # Test with only min
    @range_check('temperature', min_value=-273.15)
    class Thermometer:
        def __init__(self, temperature):
            self.temperature = temperature
    
    # Test valid value
    thermometer = Thermometer(0)
    assert thermometer.temperature == 0
    
    # Test value at min boundary
    thermometer.temperature = -273.15
    assert thermometer.temperature == -273.15
    
    # Test value below min
    with pytest.raises(ValidationError) as excinfo:
        thermometer.temperature = -274
    assert "Field temperature must be greater than or equal to -273.15" in str(excinfo.value)
    
    # Test with only max
    @range_check('percentage', max_value=100)
    class Progress:
        def __init__(self, percentage):
            self.percentage = percentage
    
    # Test valid value
    progress = Progress(50)
    assert progress.percentage == 50
    
    # Test value at max boundary
    progress.percentage = 100
    assert progress.percentage == 100
    
    # Test value above max
    with pytest.raises(ValidationError) as excinfo:
        progress.percentage = 101
    assert "Field percentage must be less than or equal to 100" in str(excinfo.value)
    
    # Test non-numeric value
    with pytest.raises(ValidationError) as excinfo:
        progress.percentage = "50%"
    assert "Field percentage must be less than or equal to 100" in str(excinfo.value)

# Test for string_length decorator
def test_string_length():
    # Test with both min and max
    @string_length('username', min_length=3, max_length=20)
    class User:
        def __init__(self, username):
            self.username = username
    
    # Test valid value
    user = User("john_doe")
    assert user.username == "john_doe"
    
    # Test value at min boundary
    user.username = "abc"
    assert user.username == "abc"
    
    # Test value at max boundary
    user.username = "a" * 20
    assert user.username == "a" * 20
    
    # Test value below min
    with pytest.raises(ValidationError) as excinfo:
        user.username = "ab"
    assert "Field username must have a length between 3 and 20" in str(excinfo.value)
    
    # Test value above max
    with pytest.raises(ValidationError) as excinfo:
        user.username = "a" * 21
    assert "Field username must have a length between 3 and 20" in str(excinfo.value)
    
    # Test with only min
    @string_length('name', min_length=1)
    class Person:
        def __init__(self, name):
            self.name = name
    
    # Test valid value
    person = Person("John")
    assert person.name == "John"
    
    # Test value at min boundary
    person.name = "J"
    assert person.name == "J"
    
    # Test empty string
    with pytest.raises(ValidationError) as excinfo:
        person.name = ""
    assert "Field name must have a length greater than or equal to 1" in str(excinfo.value)
    
    # Test with only max
    @string_length('description', max_length=100)
    class Product:
        def __init__(self, description=""):
            self.description = description
    
    # Test valid value
    product = Product("A great product")
    assert product.description == "A great product"
    
    # Test empty string
    product.description = ""
    assert product.description == ""
    
    # Test value at max boundary
    product.description = "a" * 100
    assert product.description == "a" * 100
    
    # Test value above max
    with pytest.raises(ValidationError) as excinfo:
        product.description = "a" * 101
    assert "Field description must have a length less than or equal to 100" in str(excinfo.value)
    
    # Test non-string value
    with pytest.raises(ValidationError) as excinfo:
        product.description = 12345
    assert "Field description must have a length less than or equal to 100" in str(excinfo.value)

# Test for pattern decorator
def test_pattern():
    # Test email pattern
    @pattern('email', r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    class User:
        def __init__(self, email):
            self.email = email
    
    # Test valid value
    user = User("john@example.com")
    assert user.email == "john@example.com"
    
    # Test invalid value in constructor
    with pytest.raises(ValidationError) as excinfo:
        User("invalid-email")
    assert "Field email must match pattern" in str(excinfo.value)
    
    # Test invalid value in assignment
    user = User("john@example.com")
    with pytest.raises(ValidationError) as excinfo:
        user.email = "invalid-email"
    assert "Field email must match pattern" in str(excinfo.value)
    
    # Test phone pattern
    @pattern('phone', r'^\d{3}-\d{3}-\d{4}$')
    class Contact:
        def __init__(self, name, phone=None):
            self.name = name
            if phone:
                self.phone = phone
    
    # Test valid value
    contact = Contact("John", "123-456-7890")
    assert contact.phone == "123-456-7890"
    
    # Test invalid value
    with pytest.raises(ValidationError) as excinfo:
        contact.phone = "1234567890"
    assert "Field phone must match pattern" in str(excinfo.value)
    
    # Test non-string value
    with pytest.raises(ValidationError) as excinfo:
        contact.phone = 1234567890
    assert "Field phone must match pattern" in str(excinfo.value)

# Test for multiple validations on the same field
def test_multiple_validations():
    @not_null('name')
    @string_length('name', min_length=2, max_length=50)
    @pattern('name', r'^[a-zA-Z\s]+$')  # Only letters and spaces
    class Person:
        def __init__(self, name):
            self.name = name
    
    # Test valid value
    person = Person("John Doe")
    assert person.name == "John Doe"
    
    # Test None value (should fail not_null)
    with pytest.raises(ValidationError) as excinfo:
        person.name = None
    assert "Field name cannot be None" in str(excinfo.value)
    
    # Test too short value (should fail string_length)
    with pytest.raises(ValidationError) as excinfo:
        person.name = "J"
    assert "Field name must have a length between 2 and 50" in str(excinfo.value)
    
    # Test invalid pattern (should fail pattern)
    with pytest.raises(ValidationError) as excinfo:
        person.name = "John123"
    assert "Field name must match pattern" in str(excinfo.value)

# Test for validation with inheritance
def test_validation_inheritance():
    @not_null('name')
    class Person:
        def __init__(self, name):
            self.name = name
    
    @not_null('email')
    class Employee(Person):
        def __init__(self, name, email):
            super().__init__(name)
            self.email = email
    
    # Test valid values
    employee = Employee("John", "john@example.com")
    assert employee.name == "John"
    assert employee.email == "john@example.com"
    
    # Test None value for name
    with pytest.raises(ValidationError) as excinfo:
        Employee(None, "john@example.com")
    assert "Field name cannot be None" in str(excinfo.value)
    
    # Test None value for email
    with pytest.raises(ValidationError) as excinfo:
        employee = Employee("John", "john@example.com")
        employee.email = None
    assert "Field email cannot be None" in str(excinfo.value)