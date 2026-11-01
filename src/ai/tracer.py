import os
from config.settings import settings
from config.logging_config import logger

def configure_langsmith():
    """
    Configures LangSmith tracing environment variables if enabled and configured.
    Operates dormant if credentials are missing or tracing is disabled.
    """
    if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        logger.info(f"LangSmith distributed tracing enabled for project '{settings.LANGCHAIN_PROJECT}'.")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.info("LangSmith tracing is dormant (disabled or unconfigured).")
