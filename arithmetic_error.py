"""Simple arithmetic program with proper error handling."""


def _is_valid_number(value):
    """Return True if value is an int or float, excluding bool."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def calculate(a, b):
    """Return (sum, difference, product, quotient) of a and b.

    Raises:
        TypeError: If either a or b is not an int or float.
        ZeroDivisionError: If b is 0, since division by zero is undefined.
    """
    if not _is_valid_number(a):
        raise TypeError(f"Expected a to be int or float, got {type(a).__name__}")
    if not _is_valid_number(b):
        raise TypeError(f"Expected b to be int or float, got {type(b).__name__}")
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")

    sum_result = a + b
    diff_result = a - b
    product_result = a * b
    quotient_result = a / b

    return sum_result, diff_result, product_result, quotient_result


if __name__ == "__main__":
    x = 10
    y = 0
    try:
        sum_result, diff_result, product_result, quotient_result = calculate(x, y)
    except ZeroDivisionError as error:
        print(f"Error: {error}")
    except TypeError as error:
        print(f"Error: {error}")
    else:
        print(f"Sum: {sum_result}")
        print(f"Difference: {diff_result}")
        print(f"Product: {product_result}")
        print(f"Quotient: {quotient_result}")
