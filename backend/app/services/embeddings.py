from app.models import ModelProvider
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from typing import Optional

def load_embeddings_model(provider: ModelProvider, model_id: str, api_key: Optional[str] = None):
    """
    Factory function to create the appropriate embeddings model based on provider.
    
    Args:
        provider: The model provider (HuggingFace, OpenAI, etc.)
        model_id: The model identifier
        api_key: Optional API key for providers that require authentication
        
    Returns:
        An initialized embeddings model ready for use
    """
    if provider == ModelProvider.HUGGINGFACE:
        print("Loading HuggingFace embeddings model with model_id:", model_id)
        return HuggingFaceEmbeddings(model_name=model_id)
    
    elif provider == ModelProvider.OPENAI:
        # If API key is provided, use it; otherwise, rely on environment variable
        if api_key:
            return OpenAIEmbeddings(model=model_id, openai_api_key=api_key)
        else:
            return OpenAIEmbeddings(model=model_id)
        
    elif provider == ModelProvider.OLLAMA:
        # Configure Ollama embeddings
        # The base_url is the Ollama server location (default is http://localhost:11434)
        base_url = "http://localhost:11434"  # You might want to make this configurable
        return OllamaEmbeddings(model=model_id, base_url=base_url)
    
    else:
        raise ValueError(f"Unsupported model provider: {provider}")