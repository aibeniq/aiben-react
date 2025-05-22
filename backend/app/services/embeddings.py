import os
import requests
from app.models import ModelProvider
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import OllamaEmbeddings
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
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
        print(f"Loading Ollama embeddings model with model_id: {model_id}, base_url: {base_url}")
        
        # First check if Ollama server is reachable
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ValueError(f"Ollama server not responding correctly at {base_url} (status: {response.status_code})")
            
            # Check if model exists (but don't fail, as Ollama can pull models on demand)
            models_data = response.json()
            # Different versions of Ollama API return different structures
            available_models = []
            if "models" in models_data:  # Newer versions
                available_models = [model["name"] for model in models_data.get("models", [])]
            else:  # Older versions
                available_models = [model["name"] for model in models_data.get("models", [])]

            if model_id not in available_models:
                print(f"Warning: Model {model_id} may not be available in Ollama. Available models: {available_models}")
                print(f"Ollama will attempt to pull the model if it's not found locally.")
                
        except requests.RequestException as e:
            raise ValueError(f"Cannot connect to Ollama server at {base_url}: {str(e)}")
        
        # Create and return the embeddings model
        return OllamaEmbeddings(model=model_id, base_url=base_url)
    
    else:
        raise ValueError(f"Unsupported model provider: {provider}")