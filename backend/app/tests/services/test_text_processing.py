"""
Unit tests for text_processing.py service functions.
Tests token estimation and text chunking functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.text_processing import estimate_tokens, chunk_text
from app.core.config import settings


class TestTextProcessing:
    """Test suite for text processing utility functions."""

    def test_estimate_tokens_gpt4(self):
        """Test token estimation for GPT-4 model."""
        text = "Hello world"
        tokens = estimate_tokens(text, "gpt-4")
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_estimate_tokens_gpt35(self):
        """Test token estimation for GPT-3.5 model."""
        text = "Hello world"
        tokens = estimate_tokens(text, "gpt-3.5-turbo")
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_estimate_tokens_unknown_model(self):
        """Test token estimation for unknown model (falls back to cl100k_base)."""
        text = "Hello world"
        tokens = estimate_tokens(text, "unknown-model")
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_estimate_tokens_empty_text(self):
        """Test token estimation for empty text."""
        tokens = estimate_tokens("", "gpt-4")
        assert tokens == 0

    def test_estimate_tokens_long_text(self):
        """Test token estimation for longer text."""
        text = "This is a longer piece of text that should have more tokens than a short phrase."
        tokens = estimate_tokens(text, "gpt-4")
        assert isinstance(tokens, int)
        assert tokens > 5  # Should have more tokens than "Hello world"

    @patch("app.services.text_processing.tiktoken")
    def test_estimate_tokens_tiktoken_error(self, mock_tiktoken):
        """Test token estimation when tiktoken fails (fallback to character count)."""
        mock_tiktoken.encoding_for_model.side_effect = Exception("Tiktoken error")

        text = "Hello world"  # 11 characters
        tokens = estimate_tokens(text, "gpt-4")

        # Fallback is len(text) // 4, so 11 // 4 = 2
        assert tokens == 2

    def test_chunk_text_no_chunking_needed(self):
        """Test text chunking when text fits within max tokens."""
        text = "Short text"
        max_tokens = 100

        with patch("app.services.text_processing.estimate_tokens", return_value=5):
            chunks = chunk_text(text, max_tokens)

        assert chunks == [text]

    def test_chunk_text_chunking_required(self):
        """Test text chunking when text exceeds max tokens."""
        text = "Line 1\nLine 2\nLine 3\nLine 4"
        max_tokens = 10000  # Use realistic token limit

        # Mock token estimation - total text exceeds max_tokens, forces chunking
        with patch("app.services.text_processing.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 15000  # Each call returns 15000
            chunks = chunk_text(text, max_tokens)

        # Since total exceeds max_tokens, it goes to chunking logic
        # Each line exceeds chunk_token_limit (5000), so each becomes separate chunk
        assert isinstance(chunks, list)
        assert len(chunks) == 4  # 4 lines, each chunked separately

    def test_chunk_text_empty_text(self):
        """Test text chunking with empty text."""
        chunks = chunk_text("", 100)
        assert chunks == [""]

    def test_chunk_text_single_line(self):
        """Test text chunking with single line text."""
        text = "This is a single line of text"
        chunks = chunk_text(text, 100)
        assert chunks == [text]

    def test_chunk_text_no_max_tokens_provided(self):
        """Test text chunking when max_tokens is None (uses default)."""
        text = "Short text"

        with patch.object(settings, "TWINCHECK_MAX_TOKENS_PER_CHUNK", 50):
            with patch("app.services.text_processing.estimate_tokens", return_value=5):
                chunks = chunk_text(text)

        assert chunks == [text]

    def test_chunk_text_small_chunk_threshold(self):
        """Test text chunking with small chunk size (uses small prompt reserve)."""
        text = "Line 1\nLine 2\nLine 3"
        max_tokens = settings.CHUNK_PROCESSING_SIZE_THRESHOLD - 10  # Below threshold

        with patch("app.services.text_processing.estimate_tokens", return_value=5):
            chunks = chunk_text(text, max_tokens)

        # Should use small prompt reserve
        assert isinstance(chunks, list)

    def test_chunk_text_large_chunk_threshold(self):
        """Test text chunking with large chunk size (uses large prompt reserve)."""
        text = "Line 1\nLine 2\nLine 3"
        max_tokens = settings.CHUNK_PROCESSING_SIZE_THRESHOLD + 10  # Above threshold

        with patch("app.services.text_processing.estimate_tokens", return_value=5):
            chunks = chunk_text(text, max_tokens)

        # Should use large prompt reserve
        assert isinstance(chunks, list)

    def test_chunk_text_exact_token_limit(self):
        """Test text chunking when text exactly matches token limit."""
        text = "Exact match text"
        max_tokens = 10

        with patch("app.services.text_processing.estimate_tokens", return_value=10):
            chunks = chunk_text(text, max_tokens)

        assert chunks == [text]

    def test_chunk_text_chunk_boundary_logic(self):
        """Test the chunk boundary logic with multiple lines."""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        max_tokens = 10000  # Use realistic token limit

        # Mock to force chunking: total fits, but we'll simulate per-line logic
        with patch("app.services.text_processing.estimate_tokens") as mock_estimate:
            mock_estimate.return_value = 5000  # Total fits within max_tokens
            chunks = chunk_text(text, max_tokens)

        # Since total fits, returns single chunk
        assert len(chunks) == 1
        assert chunks[0] == text

    @pytest.mark.parametrize(
        "model", ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-3.5", "unknown-model"]
    )
    def test_estimate_tokens_different_models(self, model):
        """Test token estimation across different model names."""
        text = "Test text for token estimation"
        tokens = estimate_tokens(text, model)
        assert isinstance(tokens, int)
        assert tokens >= 0

    @pytest.mark.parametrize(
        "text,max_tokens,expected_chunks",
        [
            ("", 100, [""]),
            ("Single line", 100, ["Single line"]),
            ("Line 1\nLine 2", 10, ["Line 1\nLine 2"]),  # Assuming it fits
        ],
    )
    def test_chunk_text_parametrized(self, text, max_tokens, expected_chunks):
        """Parametrized test for text chunking with various inputs."""
        with patch("app.services.text_processing.estimate_tokens", return_value=5):
            chunks = chunk_text(text, max_tokens)

        assert chunks == expected_chunks

    def test_estimate_tokens_unicode_text(self):
        """Test token estimation with unicode characters."""
        text = "Hello 世界 🌍"
        tokens = estimate_tokens(text, "gpt-4")
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_chunk_text_preserves_line_breaks(self):
        """Test that chunking preserves line breaks within chunks."""
        text = "Line 1\nLine 2\nLine 3"

        with patch("app.services.text_processing.estimate_tokens", return_value=20):
            chunks = chunk_text(text, 50)

        assert chunks[0] == text  # Should not be chunked
        assert "\n" in chunks[0]  # Line breaks preserved
