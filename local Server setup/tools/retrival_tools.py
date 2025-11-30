import asyncio
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from loguru import logger
from pinecone import Pinecone
from fastmcp import FastMCP
from configs.config_loader import settings

class RetrievalTools:
    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDINGS_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
        )
        self.pinecone_client = Pinecone(
            api_key=settings.PINECONE_API_KEY,
            ssl_verify=False,
        )
        self.index = self.pinecone_client.Index(settings.INDEX_NAME)
        self.namespace = settings.NAME_SPACE
        self.index_name = settings.INDEX_NAME
        logger.info("Registering RetrievalTools methods...")
        self.register_tools()

    # async def retriever(self, query):
    #     query_embeddings = self.embeddings_model.aembed_documents(query)
    #     if self.pinecone_client.has_index(self.index_name):
    #         index = self.pinecone_client.Index(self.index_name)
    #         pc_data = index.describe_index_stats()
    #         if self.namespace in pc_data.get("namespaces", {}):
    #             results = index.query(
    #                 namespace=self.namespace,
    #                 vector=query_embeddings,
    #                 top_k=5,
    #                 include_values=False,
    #                 include_metadata=True,
    #             )
    #             result_text = "\n\n".join([match['metadata']['text'] for match in results.matches])
    #             return result_text
    #     return None
    
    async def retriever(self, query: str):
        query_embeddings = await self.embeddings_model.aembed_query(query)
        def run_pinecone():
            if not self.pinecone_client.has_index(self.index_name):
                return None
            index = self.pinecone_client.Index(self.index_name)
            stats = index.describe_index_stats()
            if self.namespace not in stats.get("namespaces", {}):
                return None
            return index.query(
                namespace=self.namespace,
                vector=query_embeddings,
                top_k=5,
                include_values=False,
                include_metadata=True,
            )
        results = await asyncio.to_thread(run_pinecone)
        if not results or not results.matches:
            return None
        return "\n\n".join(m["metadata"]["text"] for m in results.matches)

    def register_tools(self):
        tools = [
            (
                self.retriever,
                "retriever",
                """Retrieve relevant information from the 1996 Nepal Family Health Survey (NFHS) document,
                   including geography, demographics, fertility, family planning, population policies,
                   and health survey methodology, based on a user query.""",
            ),
        ]
        for method, name, desc in tools:
            self.mcp.tool(method, name=name, description=desc)
            logger.info("="*40)
            logger.info(f"Registered tool: {name}")
        logger.info("="*40)
        
