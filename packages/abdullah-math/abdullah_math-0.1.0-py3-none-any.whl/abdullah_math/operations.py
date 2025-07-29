"""
Basic mathematical operations for the abdullah_math package.
"""

def add(a, b):
    """
    Add two numbers.
    
    Args:
        a (int/float): First number
        b (int/float): Second number
        
    Returns:
        int/float: Sum of a and b
        
    Examples:
        >>> add(2, 3)
        5
        >>> add(2.5, 3.5)
        6.0
    """
    return a + b

def subtract(a, b):
    """
    Subtract two numbers.
    
    Args:
        a (int/float): First number
        b (int/float): Second number
        
    Returns:
        int/float: Difference of a and b
        
    Examples:
        >>> subtract(5, 3)
        2
        >>> subtract(10.5, 4.5)
        6.0
    """
    return a - b

def multiply(a, b):
    """
    Multiply two numbers.
    
    Args:
        a (int/float): First number
        b (int/float): Second number
        
    Returns:
        int/float: Product of a and b
        
    Examples:
        >>> multiply(3, 4)
        12
        >>> multiply(2.5, 4)
        10.0
    """
    return a * b

def divide(a, b):
    """
    Divide two numbers.
    
    Args:
        a (int/float): Numerator
        b (int/float): Denominator
        
    Returns:
        float: Result of a divided by b
        
    Raises:
        ValueError: If b is zero
        
    Examples:
        >>> divide(10, 2)
        5.0
        >>> divide(7, 2)
        3.5
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b