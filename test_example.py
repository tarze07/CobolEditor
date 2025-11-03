# Python example
def greet(name):
    """Display a greeting message"""
    message = f"Hello, {name}!"
    print(message)

class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, x, y):
        # Add two numbers
        return x + y

    def multiply(self, x, y):
        '''Multiply two numbers'''
        return x * y

if __name__ == "__main__":
    greet("World")
    calc = Calculator()
    result = calc.add(10, 20)
    print(f"Result: {result}")

    for i in range(10):
        if i % 2 == 0:
            print(f"Even: {i}")
