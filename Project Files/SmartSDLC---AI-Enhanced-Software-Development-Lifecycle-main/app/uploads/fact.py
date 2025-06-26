# app1.py

def factorial(n):
    """Calculate the factorial of a number."""
    if n == 0:
        return 1
    return n * factorial(n - 1)

class MathUtils:
    def is_even(self, number):
        """Check if a number is even."""
        return number % 2 == 0
