pip install uv
uv init
uv add fastmcp
uv add strands-agents
uv add pydantic-settings
uv add loguru
uv add jupyter
uv add pinecone
uv add langchain_community
uv add pypdf
uv add langchain
uv add langchain-google-genai
uv add pinecone



uv run fastmcp dev server.py
uv run server.py

for claude interactions
uv run fastmcp install claude-desktop server.py


