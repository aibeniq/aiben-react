import tiktoken
from typing import List, Dict, Any
from app.core.config import settings


def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    try:
        if "gpt-4" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-4")
        elif "gpt-3.5" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return len(text) // 4


def chunk_documents_with_metadata(
    documents: List[Any], max_tokens: int = None
) -> List[Dict[str, Any]]:
    """
    Chunk documents while preserving page metadata.

    Args:
        documents: List of LangChain Document objects with metadata
        max_tokens: Maximum tokens per chunk

    Returns:
        List of dicts with 'content' and 'metadata' (including page info)
    """
    if max_tokens is None:
        max_tokens = settings.TWINCHECK_MAX_TOKENS_PER_CHUNK

    # Use centralized prompt reserve settings based on chunk size
    if max_tokens <= settings.CHUNK_PROCESSING_SIZE_THRESHOLD:
        prompt_reserve = settings.CHUNK_PROCESSING_PROMPT_RESERVE_SMALL
    else:
        prompt_reserve = settings.CHUNK_PROCESSING_PROMPT_RESERVE_LARGE

    chunk_token_limit = max_tokens - prompt_reserve

    chunks = []
    current_chunk_text = []
    current_tokens = 0
    current_pages = set()  # Track which pages are in the current chunk

    for doc in documents:
        page_num = doc.metadata.get("page", 1)
        lines = doc.page_content.split("\n")

        for line in lines:
            line_tokens = estimate_tokens(line + "\n")

            # If adding this line would exceed the limit and we have content, save current chunk
            if current_tokens + line_tokens > chunk_token_limit and current_chunk_text:
                chunks.append(
                    {
                        "content": "\n".join(current_chunk_text),
                        "pages": sorted(list(current_pages)),
                        "metadata": {
                            "source": doc.metadata.get("source", "unknown"),
                            "pages": sorted(list(current_pages)),
                        },
                    }
                )
                current_chunk_text = []
                current_tokens = 0
                current_pages = set()

            current_chunk_text.append(line)
            current_tokens += line_tokens
            current_pages.add(page_num)

    # Add the last chunk if it has content
    if current_chunk_text:
        chunks.append(
            {
                "content": "\n".join(current_chunk_text),
                "pages": sorted(list(current_pages)),
                "metadata": {
                    "source": (
                        documents[0].metadata.get("source", "unknown")
                        if documents
                        else "unknown"
                    ),
                    "pages": sorted(list(current_pages)),
                },
            }
        )

    return chunks


def chunk_text(text: str, max_tokens: int = None) -> list[str]:
    if max_tokens is None:
        max_tokens = settings.TWINCHECK_MAX_TOKENS_PER_CHUNK

    if estimate_tokens(text) <= max_tokens:
        return [text]

    chunks = []
    lines = text.split("\n")
    current_chunk = []
    current_tokens = 0

    # Use centralized prompt reserve settings based on chunk size
    if max_tokens <= settings.CHUNK_PROCESSING_SIZE_THRESHOLD:
        prompt_reserve = settings.CHUNK_PROCESSING_PROMPT_RESERVE_SMALL
    else:
        prompt_reserve = settings.CHUNK_PROCESSING_PROMPT_RESERVE_LARGE

    chunk_token_limit = max_tokens - prompt_reserve

    for line in lines:
        line_tokens = estimate_tokens(line + "\n")
        if current_tokens + line_tokens > chunk_token_limit and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_tokens = 0
        current_chunk.append(line)
        current_tokens += line_tokens

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks
