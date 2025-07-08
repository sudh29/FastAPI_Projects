"""
Unit tests for basic Python assertions and a simple Student class using pytest.
"""

import pytest


def test_equal_or_not_equal() -> None:
    """Test equality and inequality assertions."""
    assert 3 == 3
    assert 3 != 1


def test_is_instance() -> None:
    """Test isinstance checks for string and int types."""
    assert isinstance("this is a string", str)
    assert not isinstance("10", int)


def test_boolean() -> None:
    """Test boolean assertions and string comparison."""
    validated = True
    assert validated is True
    assert ("hello" == "world") is False


def test_type() -> None:
    """Test type checks for string and int expressions."""
    assert isinstance("Hello", str)
    assert not isinstance("World", int)


def test_greater_and_less_than() -> None:
    """Test greater than and less than comparisons."""
    assert 7 > 3
    assert 4 < 10


def test_list() -> None:
    """Test list membership and boolean functions all/any."""
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)


class Student:
    """
    Simple Student class for testing purposes.

    Attributes:
        first_name: Student's first name.
        last_name: Student's last name.
        major: Student's major field of study.
        years: Number of years in the program.
    """

    def __init__(self, first_name: str, last_name: str, major: str, years: int) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def default_employee() -> Student:
    """Fixture that returns a default Student instance."""
    return Student("John", "Doe", "Computer Science", 3)


def test_person_initialization(default_employee: Student) -> None:
    """Test initialization of Student attributes."""
    assert default_employee.first_name == "John", "First name should be John"
    assert default_employee.last_name == "Doe", "Last name should be Doe"
    assert default_employee.major == "Computer Science"
    assert default_employee.years == 3
