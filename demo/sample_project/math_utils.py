"""
Math utilities for basic calculations.
"""

def add_numbers(a, b):
    return a + b

def calculate_area(radius):
    return 3.14159 * radius * radius

class Calculator:
    def __init__(self):
        self.history = []
    
    def divide(self, x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        result = x / y
        self.history.append(f"{x} / {y} = {result}")
        return result
    
    def get_history(self):
        return self.history