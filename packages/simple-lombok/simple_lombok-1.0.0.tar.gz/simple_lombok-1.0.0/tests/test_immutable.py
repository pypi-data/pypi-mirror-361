# Tests for the immutable module
import pytest
from simple_lombok.immutable import immutable, frozen_dataclass, with_method, ImmutableError

# Test for immutable decorator
def test_immutable_decorator():
    @immutable
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Test that attributes can be set during initialization
    person = Person("John", 30)
    assert person.name == "John"
    assert person.age == 30
    
    # Test that attributes cannot be modified after initialization
    with pytest.raises(ImmutableError) as excinfo:
        person.name = "Alice"
    assert "Cannot modify attribute 'name' of immutable object" in str(excinfo.value)
    
    with pytest.raises(ImmutableError) as excinfo:
        person.age = 25
    assert "Cannot modify attribute 'age' of immutable object" in str(excinfo.value)
    
    # Test that new attributes cannot be added after initialization
    with pytest.raises(ImmutableError) as excinfo:
        person.address = "123 Main St"
    assert "Cannot modify attribute 'address' of immutable object" in str(excinfo.value)

# Test for frozen_dataclass decorator
def test_frozen_dataclass_decorator():
    @frozen_dataclass
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Test that attributes can be set during initialization
    person1 = Person("John", 30)
    person2 = Person("John", 30)
    person3 = Person("Alice", 25)
    
    # Test that __eq__ method works correctly
    assert person1 == person2  # Same attribute values
    assert person1 != person3  # Different attribute values
    
    # Test that __hash__ method works correctly
    person_dict = {person1: "Person 1"}
    assert person_dict[person2] == "Person 1"  # person1 and person2 should have the same hash
    
    # Test that __str__ method works correctly
    assert str(person1) == "Person(name='John', age=30)"
    
    # Test that __repr__ method works correctly
    assert repr(person1) == "Person(name='John', age=30)"
    
    # Test that attributes cannot be modified after initialization
    with pytest.raises(ImmutableError) as excinfo:
        person1.name = "Alice"
    assert "Cannot modify attribute 'name' of immutable object" in str(excinfo.value)

# Test for with_method decorator
def test_with_method_decorator():
    @immutable
    @with_method
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Test that attributes can be set during initialization
    person1 = Person("John", 30)
    assert person1.name == "John"
    assert person1.age == 30
    
    # Test that with_* methods are created
    assert hasattr(person1, 'with_name')
    assert hasattr(person1, 'with_age')
    
    # Test that with_* methods create new instances with modified attributes
    person2 = person1.with_name("Alice")
    assert person1.name == "John"  # Original instance is unchanged
    assert person2.name == "Alice"  # New instance has the modified value
    assert person2.age == 30  # Other attributes are copied
    
    person3 = person2.with_age(25)
    assert person2.age == 30  # Original instance is unchanged
    assert person3.age == 25  # New instance has the modified value
    assert person3.name == "Alice"  # Other attributes are copied
    
    # Test that the new instances are also immutable
    with pytest.raises(ImmutableError) as excinfo:
        person2.name = "Bob"
    assert "Cannot modify attribute 'name' of immutable object" in str(excinfo.value)

# Test for immutable with inheritance
def test_immutable_inheritance():
    @immutable
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    class Employee(Person):
        def __init__(self, name, age, employee_id):
            super().__init__(name, age)
            self.employee_id = employee_id
    
    # Test that attributes can be set during initialization
    employee = Employee("John", 30, "E123")
    assert employee.name == "John"
    assert employee.age == 30
    assert employee.employee_id == "E123"
    
    # Test that attributes cannot be modified after initialization
    with pytest.raises(ImmutableError) as excinfo:
        employee.name = "Alice"
    assert "Cannot modify attribute 'name' of immutable object" in str(excinfo.value)
    
    with pytest.raises(ImmutableError) as excinfo:
        employee.employee_id = "E456"
    assert "Cannot modify attribute 'employee_id' of immutable object" in str(excinfo.value)

# Test for immutable with custom methods
def test_immutable_with_custom_methods():
    @immutable
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
        
        def get_description(self):
            return f"{self.name}, {self.age} years old"
        
        def have_birthday(self):
            # This should fail because it tries to modify an immutable object
            self.age += 1
    
    # Test that custom methods work correctly
    person = Person("John", 30)
    assert person.get_description() == "John, 30 years old"
    
    # Test that methods that try to modify attributes fail
    with pytest.raises(ImmutableError) as excinfo:
        person.have_birthday()
    assert "Cannot modify attribute 'age' of immutable object" in str(excinfo.value)

# Test for frozen_dataclass with private attributes
def test_frozen_dataclass_with_private_attributes():
    @frozen_dataclass
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
            self._private = "Private data"
    
    # Test that private attributes are not included in string representation
    person = Person("John", 30)
    assert "_private" not in str(person)
    assert "_private" not in repr(person)
    
    # Test that private attributes are still immutable
    with pytest.raises(ImmutableError) as excinfo:
        person._private = "New private data"
    assert "Cannot modify attribute '_private' of immutable object" in str(excinfo.value)

# Test for with_method with complex objects
def test_with_method_with_complex_objects():
    @immutable
    @with_method
    class Department:
        def __init__(self, name, employees):
            self.name = name
            self.employees = employees
    
    # Test with a list
    department1 = Department("Engineering", ["John", "Alice", "Bob"])
    assert department1.name == "Engineering"
    assert department1.employees == ["John", "Alice", "Bob"]
    
    # Test with_* method with a different list
    department2 = department1.with_employees(["Charlie", "Dave"])
    assert department1.employees == ["John", "Alice", "Bob"]  # Original instance is unchanged
    assert department2.employees == ["Charlie", "Dave"]  # New instance has the modified value
    
    # Test with a dictionary
    @immutable
    @with_method
    class Company:
        def __init__(self, name, departments):
            self.name = name
            self.departments = departments
    
    company1 = Company("Acme Inc", {"Engineering": 50, "Marketing": 30})
    assert company1.name == "Acme Inc"
    assert company1.departments == {"Engineering": 50, "Marketing": 30}
    
    # Test with_* method with a different dictionary
    company2 = company1.with_departments({"Sales": 20, "HR": 10})
    assert company1.departments == {"Engineering": 50, "Marketing": 30}  # Original instance is unchanged
    assert company2.departments == {"Sales": 20, "HR": 10}  # New instance has the modified value