import os
from pathlib import Path
import replicate
import requests
from app.models import ModelProvider
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import OllamaEmbeddings
from langchain.embeddings.base import Embeddings
from typing import Optional, List
from dotenv import load_dotenv
import json

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
    current_dir = Path(__file__).resolve().parent

    # Navigate to project root (3 levels up from the current file)
    root_dir = current_dir.parent.parent.parent

    # Load .env from project root
    load_dotenv(dotenv_path=os.path.join(root_dir, ".env"), override=True)

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
    elif provider == "replicate":
        current_dir = Path(__file__).resolve().parent

        # Navigate to project root (3 levels up from the current file)
        root_dir = current_dir.parent.parent.parent

        # Load .env from project root
        load_dotenv(dotenv_path=os.path.join(root_dir, ".env"), override=True)
        api_key = os.getenv("REPLICATE_API_TOKEN")
        print("API key length:", len(api_key) if api_key else 0)
        
        return ReplicateEmbeddings(model_id=model_id, api_key=api_key)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    
class ReplicateEmbeddings(Embeddings):
    """Embeddings implementation using Replicate API."""

    current_dir = Path(__file__).resolve().parent

    # Navigate to project root (3 levels up from the current file)
    root_dir = current_dir.parent.parent.parent

    # Load .env from project root
    load_dotenv(dotenv_path=os.path.join(root_dir, ".env"), override=True)
    
    def __init__(self, model_id: str, api_key: str = None):
        """Initialize Replicate embeddings.
        
        Args:
            model_id: The model identifier on Replicate
            api_key: Optional API key for Replicate
        """
        # First try explicit API key
        #if api_key and api_key.strip():
        #    os.environ["REPLICATE_API_TOKEN"] = api_key
        #    print(f"Using provided API key (length: {len(api_key)})")
        #else:
        #    # Try from environment
        #    api_key = os.environ.get("REPLICATE_API_TOKEN")
        #    if not api_key or not api_key.strip():
        #        # Last resort - try to load from .env directly
        #        try:
        #            load_dotenv(dotenv_path="/app/../.env", override=True)
        #            # Or more robustly:
        #            possible_paths = [
        #                "/app/../.env",  # Docker path
        #                "../.env",       # Relative path
        #                "../../.env",    # Another common relative path
        #            ]
        #            for path in possible_paths:
        #                if os.path.exists(path):
        #                    load_dotenv(dotenv_path=path, override=True)
        #                    break
        #            api_key = os.environ.get("REPLICATE_API_TOKEN")
        #            print(f"Loaded API key from .env file: {'Success' if api_key else 'Failed'}")
        #        except Exception as e:
        #            print(f"Error loading .env: {e}")
        #            
        #    if not api_key or not api_key.strip():
        #        raise ValueError("REPLICATE_API_TOKEN not set in environment variables and no API key provided")
        #    else:
        #        print(f"Using API key from environment (length: {len(api_key)})")
        
        self.model_id = model_id
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts."""
        embeddings = []
        for text in texts:
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query text."""
        # Run the Replicate model to get embeddings
        try:
            # Add debugging here
            print(f"Using token of length: {len(os.environ.get('REPLICATE_API_TOKEN', ''))}")
            
            #TO DO: figure out why only this hardcoded example works??

            # experiment with sample input from Replicate website
            #input_example = {
            #    "sentences": "search_query: What is TSNE?\nsearch_query: Who is Laurens van der Maaten?"
            #}
            #input_example = {
            #    "sentences": "search_query: Look ma! No hands!\nsearch_query: Look pa! Two hands!"
            #}

            #formatted input
            #formatted_input = f"search_query: {text}"

            #output = replicate.run(
            #    self.model_id,
            #    #input = input_example,
            #    #input={"sentences": formatted_input},
            #    input={"texts": "[\"text\"]"},
            #    use_file_output=False
            #)
            text_json = json.dumps([text])

            output = replicate.run(
                self.model_id,
                input={
                    "texts": text_json,
                    "batch_size": 32,
                    "normalize_embeddings": True
                }
            )
            
            # Parse the output depending on the model's response format
            # This may need adjustment based on the specific Replicate model used
            if isinstance(output, list) and all(isinstance(x, float) for x in output):
                print("Replicate output is a list of floats.")
                return output
            elif isinstance(output, dict) and "embedding" in output:
                print("Replicate output is a dictionary with 'embedding' key.")	
                return output["embedding"]
            elif len(output) > 0:
                print(f"Replicate output is a list of type: {type(output[0])}")
                try:
                    # Attempt to convert to list of floats if possible
                    embedding = [float(x) for x in output]
                    print("Successfully converted output to list of floats.")
                    return embedding
                except (ValueError, TypeError):
                    pass
            else:
                print("Replicate output is of unexpected type:", type(output))
                raise ValueError(f"Unexpected output format from Replicate model: {type(output)}")
                
        except Exception as e:
            raise ValueError(f"Error getting embeddings from Replicate: {str(e)}")