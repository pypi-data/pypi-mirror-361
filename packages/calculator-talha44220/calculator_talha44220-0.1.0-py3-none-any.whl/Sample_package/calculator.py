"""
Simple Calculator Module
Provides basic arithmetic operations
"""

class Calculator:
    """A simple calculator class for basic arithmetic operations."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
    
    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """Subtract b from a."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, a, b):
        """Raise a to the power of b."""
        result = a ** b
        self.history.append(f"{a} ** {b} = {result}")
        return result
    
    def sqrt(self, a):
        """Calculate square root of a number."""
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = a ** 0.5
        self.history.append(f"sqrt({a}) = {result}")
        return result
    
    def clear_history(self):
        """Clear calculation history."""
        self.history = []
    
    def get_history(self):
        """Get calculation history."""
        return self.history.copy()


# Convenience functions for direct use
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Raise a to the power of b."""
    return a ** b

def sqrt(a):
    """Calculate square root of a number."""
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return a ** 0.5