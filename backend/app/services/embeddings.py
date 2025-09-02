import os
from pathlib import Path
import replicate
import requests
from fastapi import HTTPException
from app.models import ModelProvider
from app.core.config import settings
from app.core.ml_imports import get_langchain_huggingface, check_ml_capabilities
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_aws import BedrockEmbeddings
from langchain_core.embeddings import Embeddings
from typing import Optional, List
from dotenv import load_dotenv
import json
from app.services.retry_utils import (
    retry_openai_api,
    retry_aws_api,
    retry_replicate_api,
)


def load_embeddings_model(
    provider: ModelProvider, model_id: str, api_key: Optional[str] = None
):
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
        # Use lazy loading for HuggingFace embeddings
        HuggingFaceEmbeddings = get_langchain_huggingface()

        if HuggingFaceEmbeddings is None:
            raise HTTPException(
                status_code=503,
                detail="HuggingFace embeddings not available. ML capabilities are not installed. Use OpenAI, AWS, or Ollama providers instead.",
            )

        # Debug: Print last 6 chars of HuggingFace token(s)
        hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")
        hf_token_alt = os.environ.get("HF_TOKEN", "")
        hf_token_hub = os.environ.get("HF_HUB_TOKEN", "")
        print(
            f"[DEBUG] HUGGINGFACEHUB_API_TOKEN ends with: {hf_token[-6:] if hf_token else '[NONE]'}"
        )
        print(
            f"[DEBUG] HF_TOKEN ends with: {hf_token_alt[-6:] if hf_token_alt else '[NONE]'}"
        )
        print(
            f"[DEBUG] HF_HUB_TOKEN ends with: {hf_token_hub[-6:] if hf_token_hub else '[NONE]'}"
        )

        print("Loading HuggingFace embeddings model with model_id:", model_id)
        return HuggingFaceEmbeddings(model_name=model_id)
    elif provider == ModelProvider.AWS:
        # Configure AWS Bedrock embeddings with retry logic
        region = os.environ.get("AWS_REGION", "eu-north-1")
        print(
            f"Loading AWS Bedrock embeddings model with model_id: {model_id}, region: {region}"
        )

        # Return retry-enabled wrapper
        return RetryBedrockEmbeddings(
            model_id=model_id, region_name=region, api_key=api_key
        )

    elif provider == ModelProvider.OPENAI:
        # Return retry-enabled wrapper for OpenAI embeddings
        print(f"Loading OpenAI embeddings model with model_id: {model_id}")
        return RetryOpenAIEmbeddings(model=model_id, openai_api_key=api_key)

    elif provider == ModelProvider.OLLAMA:
        # Configure Ollama embeddings - use dedicated embedding model
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")

        # Use dedicated embedding model instead of chat models
        embedding_model = (
            "nomic-embed-text"
            if model_id in ["llama3", "mistral", "qwen2.5:14b"]
            else model_id
        )

        print(
            f"Loading Ollama embeddings model with model_id: {embedding_model}, base_url: {base_url}"
        )

        # First check if Ollama server is reachable
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ValueError(
                    f"Ollama server not responding correctly at {base_url} (status: {response.status_code})"
                )

            # Check if model exists (but don't fail, as Ollama can pull models on demand)
            models_data = response.json()
            # Different versions of Ollama API return different structures
            available_models = []
            if "models" in models_data:  # Newer versions
                available_models = [
                    model["name"] for model in models_data.get("models", [])
                ]
            else:  # Older versions
                available_models = [
                    model["name"] for model in models_data.get("models", [])
                ]

            if embedding_model not in available_models:
                print(
                    f"Warning: Model {embedding_model} may not be available in Ollama. Available models: {available_models}"
                )
                print(
                    f"Ollama will attempt to pull the model if it's not found locally."
                )

        except requests.RequestException as e:
            raise ValueError(f"Cannot connect to Ollama server at {base_url}: {str(e)}")

        # Create and return the embeddings model
        return OllamaEmbeddings(model=embedding_model, base_url=base_url)
    elif provider == "replicate":
        current_dir = Path(__file__).resolve().parent

        # Navigate to project root (3 levels up from the current file)
        root_dir = current_dir.parent.parent.parent

        # Load .env from project root
        load_dotenv(dotenv_path=os.path.join(root_dir, ".env"), override=True)
        api_key = os.getenv("REPLICATE_API_TOKEN")
        print("API key length:", len(api_key) if api_key else 0)

        replicate_embeddings = ReplicateEmbeddings(model_id=model_id, api_key=api_key)
        print("Replicate embeddings model loaded successfully.")

        return replicate_embeddings
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
        # if api_key and api_key.strip():
        #    os.environ["REPLICATE_API_TOKEN"] = api_key
        #    print(f"Using provided API key (length: {len(api_key)})")
        # else:
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

    @retry_replicate_api(min_wait=1, max_wait=60, max_attempts=6)
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts."""
        print(f"Embedding {len(texts)} documents using Replicate...")

        try:
            # Format all texts for batch processing
            texts_json = json.dumps(texts)

            # Try batch embedding first
            output = replicate.run(
                self.model_id,
                input={
                    "texts": texts_json,
                    "batch_size": min(32, len(texts)),  # Don't exceed model limits
                    "normalize_embeddings": True,
                },
            )

            print(f"Batch embedding output type: {type(output)}")

            # Process the output based on its structure
            embeddings = []

            if isinstance(output, list):
                # If output matches number of input texts, it's likely one embedding per text
                if len(output) == len(texts) and all(
                    isinstance(emb, list) for emb in output
                ):
                    print("Batch output appears to be one embedding per text")
                    return output

                # If triple-nested structure: [[[values for text 1]], [[values for text 2]], ...]
                elif len(output) == len(texts) and all(
                    isinstance(x, list) and len(x) == 1 and isinstance(x[0], list)
                    for x in output
                ):
                    print("Triple-nested batch output - extracting inner values")
                    return [x[0] for x in output]

                # For triple-nested single output: [[[values for text 1, values for text 2, ...]]]
                elif (
                    len(output) == 1
                    and isinstance(output[0], list)
                    and len(output[0]) == len(texts)
                ):
                    print("Triple-nested single batch - returning inner batch")
                    return output[0]

                # Handle unexpected structures by falling back to one-by-one embedding
                else:
                    print(
                        f"Complex batch structure, falling back to individual embedding"
                    )
                    return [self.embed_query(text) for text in texts]
            else:
                print(
                    f"Unexpected batch output type: {type(output)}, falling back to individual embedding"
                )
                return [self.embed_query(text) for text in texts]

        except Exception as batch_e:
            print(
                f"Batch embedding failed: {str(batch_e)}, falling back to individual embedding"
            )
            import traceback

            traceback.print_exc()

            # Fall back to individual embedding
            embeddings = []
            for i, text in enumerate(texts):
                try:
                    embedding = self.embed_query(text)
                    embeddings.append(embedding)
                except Exception as e:
                    print(f"Error embedding text {i}: {str(e)}")
                    # Use a zero vector as fallback to avoid crashing
                    embeddings.append([0.0] * 768)  # Common embedding size

            return embeddings

    @retry_replicate_api(min_wait=1, max_wait=60, max_attempts=6)
    def embed_query(self, text: str) -> List[float]:
        """Embed a query text."""
        # Run the Replicate model to get embeddings
        try:
            print(
                f"Using token of length: {len(os.environ.get('REPLICATE_API_TOKEN', ''))}"
            )

            text_json = json.dumps([text])

            output = replicate.run(
                self.model_id,
                input={
                    "texts": text_json,
                    "batch_size": 32,
                    "normalize_embeddings": True,
                },
            )

            print(f"Replicate embeddings output type: {type(output)}")

            # Handle different output formats, including triple-nested lists
            if isinstance(output, list):
                # Case 1: Direct list of floats [0.1, 0.2, ...]
                if all(isinstance(x, (float, int)) for x in output):
                    print("Output is a flat list of numbers")
                    return output

                # Case 2: List containing a single list of floats [[0.1, 0.2, ...]]
                elif (
                    len(output) == 1
                    and isinstance(output[0], list)
                    and all(isinstance(x, (float, int)) for x in output[0])
                ):
                    print("Output is a list containing a single list of numbers")
                    return output[0]

                # Case 3: Triple-nested list [[[0.1, 0.2, ...]]]
                elif (
                    len(output) == 1
                    and isinstance(output[0], list)
                    and len(output[0]) == 1
                    and isinstance(output[0][0], list)
                ):
                    print("Output is a triple-nested list - extracting inner values")
                    return output[0][0]

                # Case 4: List of lists for multiple embeddings [[0.1, 0.2, ...], [0.3, 0.4, ...]]
                elif all(
                    isinstance(x, list) and all(isinstance(y, (float, int)) for y in x)
                    for x in output
                ):
                    print(
                        "Output is a list of embedding lists - taking first embedding"
                    )
                    return output[0]

                # Try to find any list of floats in the structure
                else:
                    print(
                        f"Complex output structure: {type(output)} with length {len(output)}"
                    )

                    # If it's a list with one element that's also a list
                    if len(output) == 1 and isinstance(output[0], list):
                        inner = output[0]
                        print(
                            f"Examining inner list of type {type(inner)} with length {len(inner)}"
                        )

                        # Keep unwrapping lists until we find a list of floats
                        current = output
                        depth = 0
                        while (
                            depth < 5 and isinstance(current, list) and len(current) > 0
                        ):
                            if all(isinstance(x, (float, int)) for x in current):
                                print(f"Found valid embedding at depth {depth}")
                                return current
                            current = current[0]
                            depth += 1

                        print(
                            f"Couldn't find valid embedding after {depth} levels of unwrapping"
                        )

                    # If it's just a strange structure, log details and raise error
                    print(
                        f"Unexpected structure. First element type: {type(output[0]) if len(output) > 0 else 'N/A'}"
                    )
                    raise ValueError(
                        f"Couldn't extract embeddings from complex output structure: {str(output)[:100]}..."
                    )

            elif isinstance(output, dict) and "embedding" in output:
                print("Output is a dictionary with 'embedding' key")
                return output["embedding"]

            else:
                print(f"Unexpected output type: {type(output)}")
                raise ValueError(
                    f"Unexpected output format from Replicate model: {type(output)}"
                )

        except Exception as e:
            print(f"Error in embed_query: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ValueError(f"Error getting embeddings from Replicate: {str(e)}")
        """Embed a query text."""
        # Run the Replicate model to get embeddings
        try:
            # Add debugging here
            print(
                f"Using token of length: {len(os.environ.get('REPLICATE_API_TOKEN', ''))}"
            )

            # TO DO: figure out why only this hardcoded example works??

            # experiment with sample input from Replicate website
            # input_example = {
            #    "sentences": "search_query: What is TSNE?\nsearch_query: Who is Laurens van der Maaten?"
            # }
            # input_example = {
            #    "sentences": "search_query: Look ma! No hands!\nsearch_query: Look pa! Two hands!"
            # }

            # formatted input
            # formatted_input = f"search_query: {text}"

            # output = replicate.run(
            #    self.model_id,
            #    #input = input_example,
            #    #input={"sentences": formatted_input},
            #    input={"texts": "[\"text\"]"},
            #    use_file_output=False
            # )
            text_json = json.dumps([text])

            output = replicate.run(
                self.model_id,
                input={
                    "texts": text_json,
                    "batch_size": 32,
                    "normalize_embeddings": True,
                },
            )

            print("Replicate embeddings output:", output)

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
                return output
                # try:
                #    # Attempt to convert to list of floats if possible
                #    embedding = [float(x) for x in output]
                #    print("Successfully converted output to list of floats.")
                #    return embedding
                # except (ValueError, TypeError):
                #    pass
            else:
                print("Replicate output is of unexpected type:", type(output))
                raise ValueError(
                    f"Unexpected output format from Replicate model: {type(output)}"
                )

        except Exception as e:
            raise ValueError(f"Error getting embeddings from Replicate: {str(e)}")


class RetryOpenAIEmbeddings:
    """OpenAI embeddings wrapper with retry logic."""

    def __init__(self, model: str, openai_api_key: Optional[str] = None):
        from langchain_openai import OpenAIEmbeddings

        self.embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=openai_api_key,
            max_retries=0,  # Disable OpenAI's internal retries
            request_timeout=30,  # Set reasonable timeout
        )

    @retry_openai_api(min_wait=5, max_wait=120, max_attempts=5)
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents with retry logic."""
        return self.embeddings.embed_documents(texts)

    @retry_openai_api(min_wait=5, max_wait=120, max_attempts=5)
    def embed_query(self, text: str) -> List[float]:
        """Embed a query text with retry logic."""
        return self.embeddings.embed_query(text)


class RetryBedrockEmbeddings:
    """AWS Bedrock embeddings wrapper with retry logic."""

    def __init__(self, model_id: str, region_name: str, api_key: Optional[str] = None):
        from langchain_aws import BedrockEmbeddings

        if api_key:
            self.embeddings = BedrockEmbeddings(
                model_id=model_id, region_name=region_name, api_key=api_key
            )
        else:
            self.embeddings = BedrockEmbeddings(
                model_id=model_id, region_name=region_name
            )

    @retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents with retry logic."""
        return self.embeddings.embed_documents(texts)

    @retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)
    def embed_query(self, text: str) -> List[float]:
        """Embed a query text with retry logic."""
        return self.embeddings.embed_query(text)
