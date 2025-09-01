# Original Code (Before Documentation)

```python
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
```

**Issues with original code:**
- No docstrings
- Unclear parameter types
- No usage examples
- No error handling documentation