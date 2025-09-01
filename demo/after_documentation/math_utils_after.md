# Generated Documentation (After AI Processing)

## API Reference - math_utils.py

*Auto-generated documentation for math_utils.py*

## Module Information

Math utilities for basic calculations.

## Functions

### `add_numbers(a, b)`

Adds two numbers together and returns the result.

**Signature:**
```python
def add_numbers(a, b)
```

**Parameters:**
- `a`: Union[int, float] - First number to add
- `b`: Union[int, float] - Second number to add

**Returns:** Union[int, float] - Sum of the two input numbers

**Examples:**
```python
result = add_numbers(5, 3)  # Returns 8
result = add_numbers(2.5, 1.5)  # Returns 4.0
```

### `calculate_area(radius)`

Calculates the area of a circle given its radius.

**Signature:**
```python
def calculate_area(radius)
```

**Parameters:**
- `radius`: Union[int, float] - Radius of the circle

**Returns:** float - Area of the circle (π × radius²)

**Examples:**
```python
area = calculate_area(5)  # Returns approximately 78.54
area = calculate_area(2.5)  # Returns approximately 19.63
```

## Classes

### `Calculator`

A simple calculator class that maintains a history of operations performed.

**Attributes:**
- `history`: List[str] - List of calculation history entries

**Methods:**

#### `__init__(self)`
Initialize a new Calculator instance with empty history.

#### `divide(self, x, y)`
Divides two numbers and stores the operation in history.

**Parameters:**
- `x`: Union[int, float] - Dividend (number to be divided)
- `y`: Union[int, float] - Divisor (number to divide by)

**Returns:** float - Result of the division

**Raises:**
- `ValueError`: When attempting to divide by zero

**Examples:**
```python
calc = Calculator()
result = calc.divide(10, 2)  # Returns 5.0
print(calc.get_history())  # Shows: ['10 / 2 = 5.0']
```

#### `get_history(self)`
Returns the list of all calculations performed.

**Returns:** List[str] - History of all calculations