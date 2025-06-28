import tiktoken
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


def chunk_text(text: str, max_tokens: int = None) -> list[str]:
    if max_tokens is None:
        max_tokens = settings.TWINCHECK_MAX_TOKENS_PER_CHUNK

    if estimate_tokens(text) <= max_tokens:
        return [text]

    chunks = []
    lines = text.split("\n")
    current_chunk = []
    current_tokens = 0
    chunk_token_limit = max_tokens - settings.TWINCHECK_PROMPT_RESERVE_TOKENS

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
