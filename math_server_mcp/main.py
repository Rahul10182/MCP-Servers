from fastmcp import FastMCP

app = FastMCP("math-server")


@app.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


@app.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    return a - b


@app.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


@app.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@app.tool()
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent"""
    return base ** exponent


@app.tool()
def square_root(n: float) -> float:
    """Calculate the square root of a number"""
    if n < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return n ** 0.5


if __name__ == "__main__":
    app.run()