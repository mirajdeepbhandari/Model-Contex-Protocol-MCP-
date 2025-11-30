import asyncio
from fastmcp import FastMCP
from configs.config_loader import settings
from tools.db_tools import DBTools
from tools.math_tools import MathTools
from tools.retrival_tools import RetrievalTools

mcp = FastMCP(name=settings.SERVER_NAME, version=settings.VERSION)

# Instantiate class and register its tools
MathTools(mcp)
RetrievalTools(mcp)
DBTools(mcp)


if __name__ == "__main__":
    asyncio.run(mcp.run_async())
    # mcp.run(transport="http", host=settings.HOST, port=settings.PORT)
