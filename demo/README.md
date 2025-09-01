# Code Auto-Documenter Demonstration

This directory contains examples demonstrating the Code Auto-Documenter's capabilities.

## Sample Project Structure

The `sample_project/` directory contains a small Python codebase with minimal documentation:
- `math_utils.py` - Basic mathematical functions and a Calculator class
- `string_helpers.py` - String manipulation utilities

## Generated Documentation

The `after_documentation/` directory shows the automatically generated documentation:
- Well-structured API reference documentation
- Function signatures with parameter types
- Comprehensive examples and usage patterns
- Organized by programming language

## Evaluation Results

The `evaluation_results/` directory contains quality metrics:
- Readability analysis with Flesch scores
- Coverage percentage calculations  
- Hallucination detection for accuracy
- Overall quality assessment

## Before vs After Comparison

### Before (Original Code)
```python
def add_numbers(a, b):
    return a + b

class Calculator:
    def __init__(self):
        self.history = []
    
    def divide(self, x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        result = x / y
        self.history.append(f"{x} / {y} = {result}")
        return result
```

### After (Generated Documentation)
- **Complete API Reference**: Detailed function and class documentation
- **Parameter Documentation**: Type hints and descriptions for all parameters
- **Usage Examples**: Code examples showing how to use each function
- **Error Handling**: Documentation of exceptions and edge cases
- **Structured Format**: Consistent markdown formatting across all documentation

## Quality Metrics Summary

The evaluation system provides:
- **Readability Score**: 41.2/100 (Needs improvement - expected with fallback mode)
- **Coverage Score**: Tracks documentation completeness
- **Confidence Score**: 100% (High confidence in accuracy)

The lower readability score is expected when using the fallback documentation mode without AI enhancement.

## Usage Commands

```bash
# Generate documentation
python main.py generate demo/sample_project --output demo/after_documentation

# Evaluate documentation quality
python main.py evaluate demo/after_documentation/python --output demo/evaluation_results

# Analyze specific file
python main.py analyze demo/sample_project/math_utils.py
```