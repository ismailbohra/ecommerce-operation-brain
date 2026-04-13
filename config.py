import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("DIAL_API_KEY")
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    API_VERSION = os.getenv("API_VERSION")

    MODEL_SUPERVISOR = os.getenv("MODEL_SUPERVISOR")
    MODEL_SALES = os.getenv("MODEL_SALES")
    MODEL_INVENTORY = os.getenv("MODEL_INVENTORY")
    MODEL_SUPPORT = os.getenv("MODEL_SUPPORT")
    MODEL_MARKETING = os.getenv("MODEL_MARKETING")
    MODEL_MEMORY = os.getenv("MODEL_MEMORY")
    MODEL_ACTION = os.getenv("MODEL_ACTION")
    MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING")
    MODEL_TESTING = os.getenv("MODEL_TESTING")

    DB_PATH = os.getenv("DB_PATH")

    QDRANT_MODE = os.getenv("QDRANT_MODE")
    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT"))
    QDRANT_PATH = os.getenv("QDRANT_PATH")

    TEMPERATURE = 0.2


def get_langfuse_handler():
    if not os.getenv("LANGFUSE_SECRET_KEY"):
        return None

    from langfuse.langchain import CallbackHandler

    return CallbackHandler()


def get_callbacks():
    handler = get_langfuse_handler()
    return [handler] if handler else []


def get_llm(model_name: str = None, temperature: float = None, timeout: int = 120):
    from langchain_openai import AzureChatOpenAI

    return AzureChatOpenAI(
        api_key=Config.API_KEY,
        azure_endpoint=Config.AZURE_ENDPOINT,
        api_version=Config.API_VERSION,
        azure_deployment=model_name or Config.MODEL_SUPERVISOR,
        temperature=temperature if temperature is not None else Config.TEMPERATURE,
        timeout=timeout,
        streaming=True
    )


def get_embeddings():
    from langchain_openai import AzureOpenAIEmbeddings

    return AzureOpenAIEmbeddings(
        api_key=Config.API_KEY,
        azure_endpoint=Config.AZURE_ENDPOINT,
        azure_deployment=Config.MODEL_EMBEDDING,
    )


def get_supervisor_llm():
    return get_llm(Config.MODEL_SUPERVISOR)


def get_sales_llm():
    return get_llm(Config.MODEL_SALES)


def get_inventory_llm():
    return get_llm(Config.MODEL_INVENTORY)


def get_support_llm():
    return get_llm(Config.MODEL_SUPPORT)


def get_marketing_llm():
    return get_llm(Config.MODEL_MARKETING)


def get_memory_llm():
    return get_llm(Config.MODEL_MEMORY)


def get_action_llm():
    return get_llm(Config.MODEL_ACTION)
