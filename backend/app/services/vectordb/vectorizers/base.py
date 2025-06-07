"""
Abstract base class for vectorizers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class VectorizerInterface(ABC):
    """Abstract interface for vectorizers"""

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
        self._is_initialized = False

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the vectorizer (load model, setup connections, etc.)"""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name"""
        pass

    @abstractmethod
    def get_vector_dimension(self) -> int:
        """Get the vector dimension"""
        pass

    @abstractmethod
    def get_max_tokens(self) -> int:
        """Get maximum tokens supported"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the vectorizer is healthy and ready"""
        pass

    @abstractmethod
    async def close(self):
        """Clean up resources"""
        pass

    # Common utility methods
    def is_initialized(self) -> bool:
        """Check if vectorizer is initialized"""
        return self._is_initialized

    def validate_text_length(self, text: str) -> bool:
        """Validate if text is within token limits"""
        # Basic implementation - subclasses can override with proper tokenization
        return len(text.split()) <= self.get_max_tokens()

    def truncate_text(self, text: str) -> str:
        """Truncate text to fit within token limits"""
        words = text.split()
        max_words = self.get_max_tokens()  # Rough approximation
        if len(words) <= max_words:
            return text

        logger.warning(f"Truncating text from {len(words)} to {max_words} words")
        return " ".join(words[:max_words])


class BaseVectorizer(VectorizerInterface):
    """Base implementation with common functionality"""

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.batch_size = kwargs.get("batch_size", 32)
        self.max_retries = kwargs.get("max_retries", 3)
        self.retry_delay = kwargs.get("retry_delay", 1.0)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Default batch implementation using individual embeddings"""
        if not self.is_initialized():
            await self.initialize()

        # Process in batches to avoid overwhelming the service
        results = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)

        return results

    async def _process_batch(self, texts: List[str]) -> List[List[float]]:
        """Process a single batch with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Create tasks for concurrent processing
                tasks = [self.embed_text(text) for text in texts]
                return await asyncio.gather(*tasks)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Failed to process batch after {self.max_retries} attempts: {e}"
                    )
                    raise

                logger.warning(
                    f"Batch processing attempt {attempt + 1} failed: {e}. Retrying..."
                )
                await asyncio.sleep(
                    self.retry_delay * (2**attempt)
                )  # Exponential backoff

        return []  # This should never be reached

    async def embed_text_with_retry(self, text: str) -> List[float]:
        """Embed text with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return await self.embed_text(text)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Failed to embed text after {self.max_retries} attempts: {e}"
                    )
                    raise

                logger.warning(
                    f"Embedding attempt {attempt + 1} failed: {e}. Retrying..."
                )
                await asyncio.sleep(self.retry_delay * (2**attempt))

        return []  # This should never be reached


class VectorizerRegistry:
    """Registry for managing vectorizers"""

    def __init__(self):
        self._vectorizers: Dict[str, VectorizerInterface] = {}
        self._factories: Dict[str, callable] = {}

    def register_factory(self, provider: str, factory_func: callable):
        """Register a vectorizer factory function"""
        self._factories[provider] = factory_func

    async def get_vectorizer(self, model_name: str, **kwargs) -> VectorizerInterface:
        """Get or create a vectorizer instance"""
        if model_name in self._vectorizers:
            vectorizer = self._vectorizers[model_name]
            if vectorizer.is_initialized():
                return vectorizer

        # Determine provider from model name or config
        provider = self._determine_provider(model_name, **kwargs)

        if provider not in self._factories:
            raise ValueError(f"No factory registered for provider: {provider}")

        # Create new vectorizer
        vectorizer = self._factories[provider](model_name, **kwargs)
        await vectorizer.initialize()

        self._vectorizers[model_name] = vectorizer
        return vectorizer

    def _determine_provider(self, model_name: str, **kwargs) -> str:
        """Determine the provider based on model name"""
        if model_name.startswith("text-embedding"):
            return "openai"
        elif "custom" in model_name.lower():
            return "custom"
        elif "provider" in kwargs:
            return kwargs["provider"]
        else:
            raise ValueError(f"Cannot determine provider for model: {model_name}")

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all registered vectorizers"""
        results = {}
        for model_name, vectorizer in self._vectorizers.items():
            try:
                results[model_name] = await vectorizer.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {model_name}: {e}")
                results[model_name] = False

        return results

    async def close_all(self):
        """Close all vectorizers"""
        for vectorizer in self._vectorizers.values():
            try:
                await vectorizer.close()
            except Exception as e:
                logger.error(f"Error closing vectorizer: {e}")

        self._vectorizers.clear()

    def list_models(self) -> List[str]:
        """List all available model names"""
        return list(self._vectorizers.keys())


# Global registry instance
vectorizer_registry = VectorizerRegistry()
