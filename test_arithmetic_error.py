"""Unit tests for arithmetic_error.py covering success and error scenarios."""

import unittest

from arithmetic_error import calculate


class TestCalculate(unittest.TestCase):
    def test_valid_integers(self):
        self.assertEqual(calculate(10, 2), (12, 8, 20, 5))

    def test_valid_floats(self):
        self.assertEqual(calculate(5.0, 2.0), (7.0, 3.0, 10.0, 2.5))

    def test_negative_numbers(self):
        self.assertEqual(calculate(-4, -2), (-6, -2, 8, 2))

    def test_division_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError) as cm:
            calculate(10, 0)
        self.assertEqual(str(cm.exception), "Cannot divide by zero")

    def test_boolean_arg_raises_type_error(self):
        with self.assertRaises(TypeError):
            calculate(True, 2)

    def test_boolean_second_arg_raises_type_error(self):
        with self.assertRaises(TypeError):
            calculate(2, True)

    def test_non_numeric_first_arg_raises_type_error(self):
        with self.assertRaises(TypeError):
            calculate("10", 2)

    def test_non_numeric_second_arg_raises_type_error(self):
        with self.assertRaises(TypeError):
            calculate(10, "2")

    def test_none_arg_raises_type_error(self):
        with self.assertRaises(TypeError):
            calculate(None, 2)


if __name__ == "__main__":
    unittest.main()
