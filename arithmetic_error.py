"""Simple arithmetic program with proper error handling."""


def calculate(a, b):
    """Return (sum, difference, product, quotient) of a and b.

    Raises:
        TypeError: If either a or b is not an int or float.
        ZeroDivisionError: If b is 0, since division by zero is undefined.
    """
    if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both a and b must be int or float")

    sum_result = a + b
    diff_result = a - b
    product_result = a * b

    try:
        quotient_result = a / b
    except ZeroDivisionError as exc:
        raise ZeroDivisionError("Cannot divide by zero") from exc

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
