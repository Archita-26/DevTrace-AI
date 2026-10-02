"""
Sample Calculator module for DevTrace AI benchmarking.
Contains basic arithmetic operations and a deliberate logic bug.
"""

def add(a: float, b: float) -> float:
    return a + b


def subtract(a: float, b: float) -> float:
    return a - b


def multiply(a: float, b: float) -> float:
    return a * b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculates the final payable price after applying discount percentage.
    
    BUG: Currently returns only the discount amount instead of the discounted price!
    Expected: price - (price * (discount_percent / 100))
    """
    return price * (discount_percent / 100)
