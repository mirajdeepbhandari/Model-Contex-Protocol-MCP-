import math
from loguru import logger
from fastmcp import FastMCP

class MathTools:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        logger.info("Registering basic MathTools methods...")
        self.register_tools()

    async def add(self, a: float, b: float) -> float:
        return a + b

    async def subtract(self, a: float, b: float) -> float:
        return a - b

    async def multiply(self, a: float, b: float) -> float:
        return a * b

    async def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b

    async def power(self, a: float, b: float) -> float:
        return a ** b

    async def factorial(self, n: int) -> int:
        if n < 0:
            raise ValueError("Factorial not defined for negative numbers")
        return math.factorial(n)

    # registering all the tools
    def register_tools(self):
        tools = [
            (self.add, "add", "Add two numbers"),
            (self.subtract, "subtract", "Subtract b from a"),
            (self.multiply, "multiply", "Multiply two numbers"),
            (self.divide, "divide", "Divide a by b"),
            (self.power, "power", "a raised to the power of b"),
            (self.factorial, "factorial", "Factorial of a number"),
        ]
        for method, name, desc in tools:
            self.mcp.tool(method, name=name, description=desc)
            logger.info("="*40)
            logger.info(f"Registered tool: {name}")
        logger.info("="*40)
