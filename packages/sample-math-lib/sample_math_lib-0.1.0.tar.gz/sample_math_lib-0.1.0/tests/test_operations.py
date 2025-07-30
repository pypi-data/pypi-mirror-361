import pytest
from adonitech.sample_math_lib.operations import add, subtract, multiply, divide

@pytest.mark.parametrize(
    "a, b, expected",
    [(1, 2, 3), (-1, 1, 0), (-1, -1, -2), (0, 0, 0)],
    ids=["positive", "positive_and_negative", "negative", "zeros"]
)
def test_add(a, b, expected):
    """Tests the addition function with various parameters."""
    assert add(a, b) == expected

@pytest.mark.parametrize(
    "a, b, expected",
    [(2, 1, 1), (-1, 1, -2), (-1, -1, 0)],
    ids=["positive", "negative_and_positive", "negative"]
)
def test_subtract(a, b, expected):
    """Tests the subtraction function with various parameters."""
    assert subtract(a, b) == expected

@pytest.mark.parametrize(
    "a, b, expected",
    [(3, 2, 6), (-1, 1, -1), (-1, -1, 1), (5, 0, 0)],
    ids=["positive", "negative_and_positive", "negative", "multiply_by_zero"]
)
def test_multiply(a, b, expected):
    """Tests the multiplication function with various parameters."""
    assert multiply(a, b) == expected

@pytest.mark.parametrize(
    "a, b, expected",
    [(6, 3, 2), (-1, 1, -1), (-1, -1, 1), (5, 2, 2.5)],
    ids=["integer_division", "negative_and_positive", "negative", "float_division"]
)
def test_divide(a, b, expected):
    """Tests the division function with various parameters."""
    assert divide(a, b) == expected

def test_divide_by_zero():
    """Tests if division by zero raises a ValueError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)