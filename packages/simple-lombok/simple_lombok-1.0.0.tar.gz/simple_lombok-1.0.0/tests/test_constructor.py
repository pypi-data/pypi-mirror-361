# Tests for the constructor module
from simple_lombok.constructor import all_args_constructor, no_args_constructor, required_args_constructor, builder

# Test for all_args_constructor decorator
def test_all_args_constructor():
    @all_args_constructor
    class Person:
        name: str
        age: int
        address: str
    
    # Test positional arguments
    person1 = Person("John", 30, "123 Main St")
    assert person1.name == "John"
    assert person1.age == 30
    assert person1.address == "123 Main St"
    
    # Test keyword arguments
    person2 = Person(age=25, name="Alice", address="456 Oak Ave")
    assert person2.name == "Alice"
    assert person2.age == 25
    assert person2.address == "456 Oak Ave"
    
    # Test mixed positional and keyword arguments
    person3 = Person("Bob", address="789 Pine Rd", age=35)
    assert person3.name == "Bob"
    assert person3.age == 35
    assert person3.address == "789 Pine Rd"

# Test for no_args_constructor decorator
def test_no_args_constructor():
    @no_args_constructor
    class Person:
        name: str
        age: int
        address: str
    
    # Test constructor with no arguments
    person = Person()
    assert person.name is None
    assert person.age is None
    assert person.address is None
    
    # Test setting attributes after initialization
    person.name = "John"
    person.age = 30
    person.address = "123 Main St"
    assert person.name == "John"
    assert person.age == 30
    assert person.address == "123 Main St"

# Test for required_args_constructor decorator
def test_required_args_constructor():
    @required_args_constructor
    class Person:
        name: str  # Required (no default value)
        age: int = 0  # Optional (has default value)
        address: str  # Required (no default value)
    
    # Test with positional arguments for required fields
    person1 = Person("John", "123 Main St")
    assert person1.name == "John"
    assert person1.address == "123 Main St"
    assert not hasattr(person1, "age")  # age is not set by constructor
    
    # Test with keyword arguments for required fields
    person2 = Person(address="456 Oak Ave", name="Alice")
    assert person2.name == "Alice"
    assert person2.address == "456 Oak Ave"
    assert not hasattr(person2, "age")  # age is not set by constructor
    
    # Test setting optional field manually
    person1.age = 30
    assert person1.age == 30

# Test for builder decorator
def test_builder():
    @builder
    class Person:
        name: str
        age: int
        address: str
    
    # Test building an object with all fields
    person1 = Person.builder().name("John").age(30).address("123 Main St").build()
    assert person1.name == "John"
    assert person1.age == 30
    assert person1.address == "123 Main St"
    
    # Test building an object with fields in different order
    person2 = Person.builder().address("456 Oak Ave").name("Alice").age(25).build()
    assert person2.name == "Alice"
    assert person2.age == 25
    assert person2.address == "456 Oak Ave"
    
    # Test building an object with missing fields (they should be None)
    person3 = Person.builder().name("Bob").build()
    assert person3.name == "Bob"
    assert not hasattr(person3, "age")
    assert not hasattr(person3, "address")

# Test for combining constructors with other decorators
def test_constructor_with_other_decorators():
    from simple_lombok.decorators import getter_and_setter
    
    @getter_and_setter
    @all_args_constructor
    class Person:
        name: str
        age: int
    
    # Test constructor
    person = Person("John", 30)
    assert person.name == "John"
    assert person.age == 30
    
    # Test getter methods
    assert person.get_name() == "John"
    assert person.get_age() == 30
    
    # Test setter methods
    person.set_name("Alice")
    person.set_age(25)
    assert person.name == "Alice"
    assert person.age == 25

# Test for inheritance with constructors
def test_constructor_inheritance():
    @all_args_constructor
    class Person:
        name: str
        age: int
    
    class Employee(Person):
        employee_id: str
        
        def __init__(self, name, age, employee_id):
            super().__init__(name, age)
            self.employee_id = employee_id
    
    # Test constructor in derived class
    employee = Employee("John", 30, "E123")
    assert employee.name == "John"
    assert employee.age == 30
    assert employee.employee_id == "E123"

# Test for builder with complex types
def test_builder_with_complex_types():
    @builder
    class Department:
        name: str
        employees: list
    
    # Test building with a list
    department = Department.builder().name("Engineering").employees(["John", "Alice", "Bob"]).build()
    assert department.name == "Engineering"
    assert department.employees == ["John", "Alice", "Bob"]
    
    # Test building with a dictionary
    @builder
    class Company:
        name: str
        departments: dict
    
    company = Company.builder().name("Acme Inc").departments({"Engineering": 50, "Marketing": 30}).build()
    assert company.name == "Acme Inc"
    assert company.departments == {"Engineering": 50, "Marketing": 30}