"""
Simplified embeddings integration for Vector Database Service
"""

from typing import List, Optional
import asyncio
import logging
import hashlib
from app.models import ModelProvider
from app.services.embeddings.embeddings import load_embeddings_model
from .config.settings import settings, get_model_config

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Simplified embedding service for vectordb"""

    def __init__(self):
        self._models = {}

    async def get_embeddings(
        self,
        texts: List[str],
        model_name: str,
        provider: ModelProvider,
        api_key: Optional[str] = None,
    ) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        model = await self._get_model(model_name, provider, api_key)

        # Validate text lengths
        processed_texts = []
        for text in texts:
            if not self._validate_text_length(text, model_name):
                text = self._truncate_text(text, model_name)
            processed_texts.append(text)

        try:
            # Run embedding generation in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, model.embed_documents, processed_texts
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings with {model_name}: {e}")
            raise

    async def get_single_embedding(
        self,
        text: str,
        model_name: str,
        provider: ModelProvider,
        api_key: Optional[str] = None,
    ) -> List[float]:
        """Generate embedding for a single text"""
        model = await self._get_model(model_name, provider, api_key)

        if not self._validate_text_length(text, model_name):
            text = self._truncate_text(text, model_name)

        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(None, model.embed_query, text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding with {model_name}: {e}")
            raise

    async def _get_model(
        self, model_name: str, provider: ModelProvider, api_key: Optional[str] = None
    ):
        """Get or create embedding model instance"""
        cache_key = f"{provider.value}:{model_name}"

        if cache_key not in self._models:
            model = load_embeddings_model(
                provider=provider, model_id=model_name, api_key=api_key
            )
            self._models[cache_key] = model

        return self._models[cache_key]

    def _validate_text_length(self, text: str, model_name: str) -> bool:
        """Validate if text is within token limits"""
        config = get_model_config(model_name)
        max_tokens = config.get("max_tokens", 8000)
        # Simple word-based approximation
        return len(text.split()) <= max_tokens

    def _truncate_text(self, text: str, model_name: str) -> str:
        """Truncate text to fit within token limits"""
        config = get_model_config(model_name)
        max_tokens = config.get("max_tokens", 8000)

        words = text.split()
        if len(words) <= max_tokens:
            return text

        logger.warning(f"Truncating text from {len(words)} to {max_tokens} words")
        return " ".join(words[:max_tokens])

    def determine_provider(self, model_name: str) -> ModelProvider:
        """Determine provider from model name"""
        if model_name.startswith("text-embedding"):
            return ModelProvider.OPENAI
        elif "claude" in model_name.lower():
            return ModelProvider.ANTHROPIC
        elif model_name.startswith("embed"):
            return ModelProvider.HUGGINGFACE
        else:
            return ModelProvider.OPENAI  # Default fallback


def generate_content_hash(content: str) -> str:
    """Generate hash for content deduplication"""
    return hashlib.sha256(content.encode()).hexdigest()


def split_text_into_chunks(
    content: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[str]:
    """Simple text chunking implementation"""
    if not content.strip():
        return []

    words = content.split()
    chunks = []

    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        # Move start position with overlap
        start = end - chunk_overlap
        if start < 0:
            start = 0

    return chunks
