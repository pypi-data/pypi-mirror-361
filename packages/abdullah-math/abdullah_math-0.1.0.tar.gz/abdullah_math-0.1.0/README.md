# Abdullah Math

A simple Python package for basic mathematical operations.

## Features

- Addition
- Subtraction
- Multiplication
- Division (with zero division protection)

## Installation

```bash
pip install abdullah_math
```

## Usage

```python
from abdullah_math import add, subtract, multiply, divide

# Addition
result = add(5, 3)
print(result)  # Output: 8

# Subtraction
result = subtract(10, 4)
print(result)  # Output: 6

# Multiplication
result = multiply(3, 7)
print(result)  # Output: 21

# Division
result = divide(15, 3)
print(result)  # Output: 5.0

# Division by zero raises ValueError
try:
    result = divide(10, 0)
except ValueError as e:
    print(e)  # Output: Cannot divide by zero
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Installing in Development Mode

```bash
pip install -e .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
