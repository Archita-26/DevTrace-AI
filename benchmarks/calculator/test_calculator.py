"""
Test suite for calculator module.
3 tests will pass, 1 test will fail due to the bug in calculate_discount.
"""
import pytest
from benchmarks.calculator.calculator import add, subtract, multiply, divide, calculate_discount


def test_add():
    assert add(10, 5) == 15


def test_subtract():
    assert subtract(10, 5) == 5


def test_divide_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


def test_calculate_discount():
    # If price is 100 and discount is 20%, final payable price should be 80.
    # Because of the bug, calculate_discount returns 20, so this test fails!
    actual_price = calculate_discount(100.0, 20.0)
    assert actual_price == 80.0
