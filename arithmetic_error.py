"""Simple arithmetic program that intentionally fails with an error."""


def calculate(a, b):
    sum_result = a + b
    diff_result = a - b
    product_result = a * b
    quotient_result = a / b  # Fails with ZeroDivisionError when b is 0
    return sum_result, diff_result, product_result, quotient_result


if __name__ == "__main__":
    x = 10
    y = 0
    print(f"Sum: {x + y}")
    print(f"Difference: {x - y}")
    print(f"Product: {x * y}")
    print(f"Quotient: {calculate(x, y)[3]}")
