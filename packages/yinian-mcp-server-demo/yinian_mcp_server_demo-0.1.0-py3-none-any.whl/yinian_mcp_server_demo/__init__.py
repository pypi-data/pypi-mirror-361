from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def sub(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool()
def mul(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def div(a: int, b: int) -> int:
    """Divide two numbers"""
    return a / b

@mcp.tool()
def pow(a: int, b: int) -> int:
    """Raise a number to a power"""
    return a ** b

@mcp.tool()
def sqrt(a: int) -> int:
    """Get the square root of a number"""
    return a ** 0.5

@mcp.tool()
def fact(a: int) -> int:
    """Get the factorial of a number"""
    if a < 0:
        return -1
    if a == 0:
        return 1
    else:
        return a * fact(a - 1)

@mcp.tool()
def fib(n: int) -> int:
    """Get the nth Fibonacci number"""
    if n < 0:
        return -1
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

@mcp.tool()
def is_prime(n: int) -> bool:
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Greet a personalized person"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport="stdio")