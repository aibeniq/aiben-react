"""
Adapter to integrate the existing embeddings service with the vectordb service
"""

from typing import List, Dict, Any, Optional
import asyncio
import logging
from ..core.models import EmbeddingModel
from app.models import ModelProvider
from app.services.embeddings.embeddings import load_embeddings_model
from .base import BaseVectorizer
from ..config.settings import get_model_config

logger = logging.getLogger(__name__)


class EmbeddingsServiceAdapter(BaseVectorizer):
    """Adapter to use the existing embeddings service with vectordb"""

    def __init__(
        self,
        model_name: str,
        provider: ModelProvider,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model_name, **kwargs)
        self.provider = provider
        self.api_key = api_key
        self._embeddings_model = None
        self._model_config = get_model_config(model_name)

    async def initialize(self) -> bool:
        """Initialize the embeddings model"""
        try:
            # Load the embeddings model using your existing service
            self._embeddings_model = load_embeddings_model(
                provider=self.provider, model_id=self.model_name, api_key=self.api_key
            )

            self._is_initialized = True
            logger.info(
                f"Initialized {self.provider.value} embeddings model: {self.model_name}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to initialize embeddings model {self.model_name}: {e}"
            )
            self._is_initialized = False
            return False

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if not self.is_initialized():
            await self.initialize()

        if not self._embeddings_model:
            raise RuntimeError("Embeddings model not initialized")

        # Validate and truncate text if needed
        if not self.validate_text_length(text):
            text = self.truncate_text(text)

        try:
            # Run in thread pool since the embeddings service is synchronous
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, self._embeddings_model.embed_query, text
            )
            return embedding

        except Exception as e:
            logger.error(f"Error embedding text with {self.model_name}: {e}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        if not self.is_initialized():
            await self.initialize()

        if not self._embeddings_model:
            raise RuntimeError("Embeddings model not initialized")

        # Validate and truncate texts if needed
        processed_texts = []
        for text in texts:
            if not self.validate_text_length(text):
                text = self.truncate_text(text)
            processed_texts.append(text)

        try:
            # Use the embeddings service's batch method
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, self._embeddings_model.embed_documents, processed_texts
            )
            return embeddings

        except Exception as e:
            logger.error(f"Error batch embedding with {self.model_name}: {e}")
            # Fallback to individual embeddings
            return await super().embed_batch(processed_texts)

    def get_model_name(self) -> str:
        """Get the model name"""
        return self.model_name

    def get_vector_dimension(self) -> int:
        """Get the vector dimension"""
        # Try to get from config first
        if self._model_config.get("dimensions"):
            return self._model_config["dimensions"]

        # For unknown models, try to get from a test embedding
        if self._embeddings_model:
            try:
                test_embedding = self._embeddings_model.embed_query("test")
                return len(test_embedding)
            except Exception:
                pass

        # Default fallback
        return 1536  # Common dimension for many models

    def get_max_tokens(self) -> int:
        """Get maximum tokens supported"""
        # Try to get from config first
        if self._model_config.get("max_tokens"):
            return self._model_config["max_tokens"]

        # Provider-specific defaults
        if self.provider == ModelProvider.OPENAI:
            return 8191
        elif self.provider == ModelProvider.HUGGINGFACE:
            return 512  # Conservative default for most HF models
        elif self.provider == ModelProvider.OLLAMA:
            return 2048  # Common for local models
        elif self.provider == ModelProvider.AWS:
            return 8192  # Common for Bedrock models
        elif self.provider == ModelProvider.REPLICATE:
            return 8191  # Similar to OpenAI
        else:
            return 1000  # Conservative default

    async def health_check(self) -> bool:
        """Check if the vectorizer is healthy and ready"""
        try:
            if not self.is_initialized():
                return False

            # Try a simple embedding to verify the service is working
            test_embedding = await self.embed_text("health check")
            return len(test_embedding) > 0

        except Exception as e:
            logger.error(f"Health check failed for {self.model_name}: {e}")
            return False

    async def close(self):
        """Clean up resources"""
        # The embeddings service doesn't require explicit cleanup
        self._embeddings_model = None
        self._is_initialized = False


def create_embeddings_adapter(
    model_name: str, provider: ModelProvider, api_key: Optional[str] = None, **kwargs
) -> EmbeddingsServiceAdapter:
    """Factory function to create an embeddings service adapter"""
    return EmbeddingsServiceAdapter(
        model_name=model_name, provider=provider, api_key=api_key, **kwargs
    )


# Register the adapter factory with the vectorizer registry
def register_embeddings_service_factories():
    """Register factory functions for all supported providers"""
    from .base import vectorizer_registry

    # Register for each provider
    for provider in ModelProvider:
        vectorizer_registry.register_factory(
            provider.value,
            lambda model_name, provider=provider, **kwargs: create_embeddings_adapter(
                model_name, provider, **kwargs
            ),
        )


# Auto-register when module is imported
register_embeddings_service_factories()
