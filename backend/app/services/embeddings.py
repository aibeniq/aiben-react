import os
from pathlib import Path
import replicate
import requests
from app.models import ModelProvider
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_aws import BedrockEmbeddings
from langchain_core.embeddings import Embeddings
from typing import Optional, List, Dict
from dotenv import load_dotenv
import json
from dataclasses import dataclass


@dataclass
class EmbeddingModelSpec:
    """Specification for an embedding model."""

    id: str  # unique identifier for the model
    provider: str  # provider name (openai, huggingface, etc.)
    model_name: str  # actual model name used by provider
    dimensions: int  # embedding vector dimensions
    max_input_length: Optional[int] = None  # max input tokens/chars
    cost_per_1k_tokens: Optional[float] = None  # cost in USD
    description: Optional[str] = None


class EmbeddingService:
    """Service for managing and loading embedding models."""

    # registry of available embedding models
    AVAILABLE_MODELS: Dict[str, EmbeddingModelSpec] = {
        "openai-text-3-small": EmbeddingModelSpec(
            id="openai-text-3-small",
            provider="openai",
            model_name="text-embedding-3-small",
            dimensions=1536,
            max_input_length=8191,
            cost_per_1k_tokens=0.00002,
            description="OpenAI's efficient small embedding model",
        ),
        "openai-text-3-large": EmbeddingModelSpec(
            id="openai-text-3-large",
            provider="openai",
            model_name="text-embedding-3-large",
            dimensions=3072,
            max_input_length=8191,
            cost_per_1k_tokens=0.00013,
            description="OpenAI's high-performance large embedding model",
        ),
        "openai-ada-002": EmbeddingModelSpec(
            id="openai-ada-002",
            provider="openai",
            model_name="text-embedding-ada-002",
            dimensions=1536,
            max_input_length=8191,
            cost_per_1k_tokens=0.0001,
            description="OpenAI's legacy embedding model",
        ),
    }

    @classmethod
    def list_available_models(cls) -> List[str]:
        """Get list of available model IDs."""
        return list(cls.AVAILABLE_MODELS.keys())

    @classmethod
    def get_model_spec(cls, model_id: str) -> Optional[EmbeddingModelSpec]:
        """Get specification for a specific model."""
        return cls.AVAILABLE_MODELS.get(model_id)

    @classmethod
    def get_models_by_provider(cls, provider: str) -> List[EmbeddingModelSpec]:
        """Get all models for a specific provider."""
        return [
            spec for spec in cls.AVAILABLE_MODELS.values() if spec.provider == provider
        ]

    @classmethod
    def get_model_specs(cls) -> Dict[str, EmbeddingModelSpec]:
        """Get all model specifications."""
        return cls.AVAILABLE_MODELS.copy()

    @classmethod
    def validate_model(
        cls, model_id: str, api_key: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if a model is available and properly configured.

        Returns:
            tuple: (is_valid, error_message)
        """
        # check if model exists in registry
        if model_id not in cls.AVAILABLE_MODELS:
            available = ", ".join(cls.AVAILABLE_MODELS.keys())
            return False, f"Model '{model_id}' not found. Available models: {available}"

        spec = cls.AVAILABLE_MODELS[model_id]

        # validate provider-specific requirements
        if spec.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                return (
                    False,
                    f"OPENAI_API_KEY environment variable required for model '{model_id}'",
                )

        # TODO: add other providers

        return True, None

    @classmethod
    def get_model(cls, model_id: str, api_key: Optional[str] = None) -> Embeddings:
        """
        Get an embedding model by ID.

        Args:
            model_id: The model identifier from the registry
            api_key: Optional API key override

        Returns:
            An initialized embeddings model

        Raises:
            ValueError: If model is invalid or cannot be loaded
        """
        # validate model
        is_valid, error_msg = cls.validate_model(model_id, api_key)
        if not is_valid:
            raise ValueError(error_msg)

        spec = cls.AVAILABLE_MODELS[model_id]

        # load model based on provider
        try:
            if spec.provider == "openai":
                return OpenAIEmbeddings(model=spec.model_name, openai_api_key=api_key)

            # TODO: add other providers

            else:
                raise ValueError(f"Unsupported provider: {spec.provider}")

        except Exception as e:
            raise ValueError(f"Failed to load model '{model_id}': {str(e)}")


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
