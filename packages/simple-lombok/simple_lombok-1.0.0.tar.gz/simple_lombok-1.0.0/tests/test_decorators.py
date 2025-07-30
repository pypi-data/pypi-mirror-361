# Tests for the decorators module
from simple_lombok.decorators import getter, setter, getter_and_setter

# Test class for getter decorator
def test_getter_decorator():
    @getter
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Create an instance
    person = Person("John", 30)
    
    # Test that getter methods were created
    assert hasattr(person, 'get_name')
    assert hasattr(person, 'get_age')
    
    # Test that getter methods return correct values
    assert person.get_name() == "John"
    assert person.get_age() == 30
    
    # Test that setter methods were not created
    assert not hasattr(person, 'set_name')
    assert not hasattr(person, 'set_age')
    
    # Test that changing attributes directly works
    person.name = "Alice"
    person.age = 25
    assert person.get_name() == "Alice"
    assert person.get_age() == 25

# Test class for setter decorator
def test_setter_decorator():
    @setter
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Create an instance
    person = Person("John", 30)
    
    # Test that setter methods were created
    assert hasattr(person, 'set_name')
    assert hasattr(person, 'set_age')
    
    # Test that getter methods were not created
    assert not hasattr(person, 'get_name')
    assert not hasattr(person, 'get_age')
    
    # Test that setter methods work correctly
    person.set_name("Alice")
    person.set_age(25)
    assert person.name == "Alice"
    assert person.age == 25

# Test class for getter_and_setter decorator
def test_getter_and_setter_decorator():
    @getter_and_setter
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Create an instance
    person = Person("John", 30)
    
    # Test that both getter and setter methods were created
    assert hasattr(person, 'get_name')
    assert hasattr(person, 'get_age')
    assert hasattr(person, 'set_name')
    assert hasattr(person, 'set_age')
    
    # Test that getter methods return correct values
    assert person.get_name() == "John"
    assert person.get_age() == 30
    
    # Test that setter methods work correctly
    person.set_name("Alice")
    person.set_age(25)
    assert person.get_name() == "Alice"
    assert person.get_age() == 25
    assert person.name == "Alice"
    assert person.age == 25

# Test for attributes added after initialization
def test_attributes_added_after_init():
    @getter_and_setter
    class DynamicPerson:
        def __init__(self):
            pass
    
    person = DynamicPerson()
    
    # Add attributes after initialization
    person.name = "John"
    person.age = 30
    
    # Test that getter and setter methods were created for new attributes
    assert hasattr(person, 'get_name')
    assert hasattr(person, 'get_age')
    assert hasattr(person, 'set_name')
    assert hasattr(person, 'set_age')
    
    # Test that getter methods return correct values
    assert person.get_name() == "John"
    assert person.get_age() == 30
    
    # Test that setter methods work correctly
    person.set_name("Alice")
    person.set_age(25)
    assert person.get_name() == "Alice"
    assert person.get_age() == 25

# Test for special attributes (those starting with '__')
def test_special_attributes_skipped():
    @getter_and_setter
    class SpecialPerson:
        def __init__(self):
            self.name = "John"
            self.__private = "Private"
    
    person = SpecialPerson()
    
    # Test that getter and setter methods were created for normal attributes
    assert hasattr(person, 'get_name')
    assert hasattr(person, 'set_name')
    
    # Test that getter and setter methods were not created for special attributes
    assert not hasattr(person, 'get___private')
    assert not hasattr(person, 'set___private')