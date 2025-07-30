def add(a, b):
    """Returns the sum of two numbers."""
    return a + b

def subtract(a, b):
    """Returns the subtraction of two numbers."""
    return a - b

def multiply(a, b):
    """Returns the multiplication of two numbers."""
    return a * b

def divide(a, b):
    """
    Returns the division of two numbers.
    Raises a ValueError if division by zero is attempted.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
