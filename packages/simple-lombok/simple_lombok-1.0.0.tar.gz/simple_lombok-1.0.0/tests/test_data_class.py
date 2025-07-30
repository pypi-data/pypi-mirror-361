# Tests for the data_class module
from simple_lombok.data_class import data_class, equals_and_hash_code, to_string

# Test for data_class decorator
def test_data_class_decorator():
    @data_class
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Create instances
    person1 = Person("John", 30)
    person2 = Person("John", 30)
    person3 = Person("Alice", 25)
    
    # Test __eq__ method
    assert person1 == person2  # Same attribute values
    assert person1 != person3  # Different attribute values
    
    # Test __hash__ method
    person_dict = {person1: "Person 1"}
    assert person_dict[person2] == "Person 1"  # person1 and person2 should have the same hash
    
    # Test __str__ method
    assert str(person1) == "Person(name='John', age=30)"
    
    # Test __repr__ method
    assert repr(person1) == "Person(name='John', age=30)"

# Test for equals_and_hash_code decorator
def test_equals_and_hash_code_decorator():
    @equals_and_hash_code
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Create instances
    person1 = Person("John", 30)
    person2 = Person("John", 30)
    person3 = Person("Alice", 25)
    
    # Test __eq__ method
    assert person1 == person2  # Same attribute values
    assert person1 != person3  # Different attribute values
    
    # Test __hash__ method
    person_dict = {person1: "Person 1"}
    assert person_dict[person2] == "Person 1"  # person1 and person2 should have the same hash
    
    # Test that __str__ and __repr__ were not added
    assert str(person1) != "Person(name='John', age=30)"
    assert repr(person1) != "Person(name='John', age=30)"

# Test for to_string decorator
def test_to_string_decorator():
    @to_string
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Create instance
    person = Person("John", 30)
    
    # Test __str__ method
    assert str(person) == "Person(name='John', age=30)"
    
    # Test __repr__ method
    assert repr(person) == "Person(name='John', age=30)"
    
    # Create another instance with different values
    person2 = Person("Alice", 25)
    assert str(person2) == "Person(name='Alice', age=25)"
    assert repr(person2) == "Person(name='Alice', age=25)"

# Test for private attributes
def test_private_attributes_in_string_representation():
    @to_string
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
            self._private = "Private data"
    
    # Create instance
    person = Person("John", 30)
    
    # Test that private attributes are not included in string representation
    assert "_private" not in str(person)
    assert "_private" not in repr(person)

# Test for custom __eq__ and __hash__ methods
def test_custom_methods_not_overridden():
    @data_class
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
        
        def __eq__(self, other):
            # Custom equality that only checks name
            if not isinstance(other, Person):
                return False
            return self.name == other.name
        
        def __hash__(self):
            # Custom hash that only uses name
            return hash(self.name)
    
    # Create instances
    person1 = Person("John", 30)
    person2 = Person("John", 25)  # Different age, same name
    person3 = Person("Alice", 30)  # Same age, different name
    
    # Test that custom __eq__ is used
    assert person1 == person2  # Same name, different age
    assert person1 != person3  # Different name
    
    # Test that custom __hash__ is used
    person_dict = {person1: "Person 1"}
    assert person_dict[person2] == "Person 1"  # person1 and person2 should have the same hash
    
    # Test that person3 has a different hash
    assert hash(person1) != hash(person3)

# Test for inheritance
def test_data_class_with_inheritance():
    @data_class
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    class Employee(Person):
        def __init__(self, name, age, employee_id):
            super().__init__(name, age)
            self.employee_id = employee_id
    
    # Create instances
    employee1 = Employee("John", 30, "E123")
    employee2 = Employee("John", 30, "E123")
    employee3 = Employee("John", 30, "E456")
    
    # Test __eq__ method
    assert employee1 == employee2  # Same attribute values
    assert employee1 != employee3  # Different employee_id
    
    # Test __str__ method
    assert str(employee1) == "Employee(name='John', age=30, employee_id='E123')"