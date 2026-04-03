import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("DIAL_API_KEY")
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    API_VERSION = os.getenv("API_VERSION")

    MODEL_SUPERVISOR = os.getenv("MODEL_SUPERVISOR", "claude-sonnet-4@20250514")
    MODEL_SALES = os.getenv("MODEL_SALES", "claude-haiku-4-5@20251001")
    MODEL_INVENTORY = os.getenv("MODEL_INVENTORY", "claude-haiku-4-5@20251001")
    MODEL_SUPPORT = os.getenv("MODEL_SUPPORT", "claude-haiku-4-5@20251001")
    MODEL_MARKETING = os.getenv("MODEL_MARKETING", "claude-haiku-4-5@20251001")
    MODEL_MEMORY = os.getenv("MODEL_MEMORY", "claude-3-5-haiku@20241022")
    MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING", "text-embedding-3-small-1")

    DB_PATH = os.getenv("DB_PATH", "data/ecommerce.db")

    QDRANT_MODE = os.getenv("QDRANT_MODE", "memory")
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_PATH = os.getenv("QDRANT_PATH", "data/qdrant")

    TEMPERATURE = 0.2


def get_llm(model_name: str):
    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(
        api_key=Config.API_KEY,
        azure_endpoint=Config.AZURE_ENDPOINT,
        api_version=Config.API_VERSION,
        azure_deployment=model_name,
        temperature=Config.TEMPERATURE,
    )


def get_embeddings():
    from langchain_openai import AzureOpenAIEmbeddings

    return AzureOpenAIEmbeddings(
        api_key=Config.API_KEY,
        azure_endpoint=Config.AZURE_ENDPOINT,
        azure_deployment=Config.MODEL_EMBEDDING,
    )
