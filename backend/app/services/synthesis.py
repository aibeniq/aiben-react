"""
Hierarchical Synthesis Utilities

This module provides shared utilities for hierarchical synthesis of large documents
across all Full Document Scan features (ReportGenie, Chatbot, VeraDoc, etc.).

When chunk analyses are too large to fit in a single LLM call, hierarchical synthesis
splits them into batches, synthesizes each batch, then combines the results.
"""

from typing import List, Optional
import logging

from app.services.text_processing import estimate_tokens
from app.services.llms import invoke_llm
from app.core.config import settings

logger = logging.getLogger(__name__)


def hierarchical_synthesis(
    chunk_analyses: List[str],
    question: str,
    llm,
    session,
    user_id: int,
    max_tokens_per_group: int,
    language_instruction: str,
    synthesis_template: Optional[str] = None,
    template_params: Optional[dict] = None,
) -> str:
    """
    Perform hierarchical synthesis when chunk analyses are too large for a single LLM call.
    
    This function is used across multiple features:
    - ReportGenie Generate (Full Document Scan)
    - Chatbot Full Document Scan (KB and Document queries)
    - VeraDoc Full Document Scan
    - Any other feature that needs to synthesize many chunk analyses
    
    Algorithm:
    1. Group chunk analyses into batches that fit within token limits
    2. Synthesize each batch separately
    3. If multiple batches, synthesize the batch results into final answer
    4. If single batch, synthesize directly and return
    
    Args:
        chunk_analyses: List of individual chunk analysis texts to synthesize
        question: The question being answered
        llm: The LLM instance to use for synthesis
        session: Database session for tracking LLM interactions
        user_id: User ID for LLM interaction tracking
        max_tokens_per_group: Maximum tokens allowed per synthesis group
        language_instruction: Language instruction for the LLM (e.g., "Respond in English")
        synthesis_template: Template to use for synthesis (defaults to CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE)
        template_params: Additional parameters to pass to the template (optional)
        
    Returns:
        Final synthesized answer combining all chunk analyses
    """
    if synthesis_template is None:
        synthesis_template = settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE
    
    if template_params is None:
        template_params = {}
    
    logger.info(f"🔄 Starting hierarchical synthesis for {len(chunk_analyses)} chunk analyses")
    print(f"🔄 Starting hierarchical synthesis for {len(chunk_analyses)} chunk analyses")
    
    # Calculate how many analyses can fit in one synthesis call
    template_overhead = 2000  # Reserve for template text
    available_tokens = max_tokens_per_group - template_overhead
    
    # Group analyses into batches that fit within token limit
    batches = []
    current_batch = []
    current_batch_tokens = 0
    
    for idx, analysis in enumerate(chunk_analyses):
        analysis_tokens = estimate_tokens(analysis, model=getattr(llm, "model_name", "gpt-4o"))
        
        if current_batch_tokens + analysis_tokens > available_tokens and current_batch:
            # Current batch is full, start a new one
            batches.append(current_batch)
            logger.debug(f"  📦 Batch {len(batches)}: {len(current_batch)} analyses (~{current_batch_tokens:,} tokens)")
            print(f"  📦 Batch {len(batches)}: {len(current_batch)} analyses (~{current_batch_tokens:,} tokens)")
            current_batch = [analysis]
            current_batch_tokens = analysis_tokens
        else:
            current_batch.append(analysis)
            current_batch_tokens += analysis_tokens
    
    # Add the last batch
    if current_batch:
        batches.append(current_batch)
        logger.debug(f"  📦 Batch {len(batches)}: {len(current_batch)} analyses (~{current_batch_tokens:,} tokens)")
        print(f"  📦 Batch {len(batches)}: {len(current_batch)} analyses (~{current_batch_tokens:,} tokens)")
    
    logger.info(f"📊 Split into {len(batches)} batches for hierarchical synthesis")
    print(f"📊 Split into {len(batches)} batches for hierarchical synthesis")
    
    # If we only have one batch, synthesize it directly and return
    if len(batches) == 1:
        logger.info(f"  ✅ Only one batch - performing single synthesis")
        print(f"  ✅ Only one batch - performing single synthesis")
        batch_combined = "\n\n".join(batches[0])
        
        # Build template parameters
        params = {
            "chunk_analyses": batch_combined,
            "question": question,
            "language_instruction": language_instruction,
            "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
            **template_params,  # Merge any additional parameters
        }
        
        return invoke_llm(
            llm,
            synthesis_template,
            params,
        )
    
    # Synthesize each batch
    batch_syntheses = []
    for batch_idx, batch in enumerate(batches):
        batch_combined = "\n\n".join(batch)
        
        logger.info(f"  🔄 Synthesizing batch {batch_idx + 1}/{len(batches)}...")
        print(f"  🔄 Synthesizing batch {batch_idx + 1}/{len(batches)}...")
        
        # Build template parameters
        params = {
            "chunk_analyses": batch_combined,
            "question": question,
            "language_instruction": language_instruction,
            "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
            **template_params,  # Merge any additional parameters
        }
        
        batch_synthesis = invoke_llm(
            llm,
            synthesis_template,
            params,
        )
        batch_syntheses.append(batch_synthesis)
        
        batch_tokens = estimate_tokens(batch_synthesis, model=getattr(llm, "model_name", "gpt-4o"))
        logger.debug(f"  ✅ Batch {batch_idx + 1} synthesized ({batch_tokens:,} tokens)")
        print(f"  ✅ Batch {batch_idx + 1} synthesized ({batch_tokens:,} tokens)")
    
    # Final synthesis: combine all batch syntheses
    final_combined = "\n\n".join(batch_syntheses)
    final_combined_tokens = estimate_tokens(final_combined, model=getattr(llm, "model_name", "gpt-4o"))
    logger.info(f"  🔄 Final synthesis of {len(batch_syntheses)} batch results (~{final_combined_tokens:,} tokens)...")
    print(f"  🔄 Final synthesis of {len(batch_syntheses)} batch results (~{final_combined_tokens:,} tokens)...")
    
    # Build template parameters for final synthesis
    final_params = {
        "chunk_analyses": final_combined,
        "question": question,
        "language_instruction": language_instruction,
        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
        **template_params,  # Merge any additional parameters
    }
    
    final_synthesis = invoke_llm(
        llm,
        synthesis_template,
        final_params,
    )
    
    final_tokens = estimate_tokens(final_synthesis, model=getattr(llm, "model_name", "gpt-4o"))
    logger.info(f"  ✅ Hierarchical synthesis complete ({final_tokens:,} tokens)")
    print(f"  ✅ Hierarchical synthesis complete ({final_tokens:,} tokens)")
    
    return final_synthesis


def check_synthesis_token_limit(
    chunk_analyses: List[str],
    question: str,
    language_instruction: str,
    llm,
    synthesis_template: Optional[str] = None,
    template_params: Optional[dict] = None,
) -> tuple[int, bool]:
    """
    Check if a synthesis prompt would exceed token limits.
    
    Args:
        chunk_analyses: List of chunk analysis texts
        question: The question being answered
        language_instruction: Language instruction for the LLM
        llm: The LLM instance (for model name)
        synthesis_template: Template to use for synthesis
        template_params: Additional template parameters
        
    Returns:
        Tuple of (estimated_tokens, exceeds_limit)
    """
    if synthesis_template is None:
        synthesis_template = settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE
    
    if template_params is None:
        template_params = {}
    
    # Build test synthesis prompt
    chunk_analyses_text = "\n\n".join(chunk_analyses)
    
    params = {
        "chunk_analyses": chunk_analyses_text,
        "question": question,
        "language_instruction": language_instruction,
        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
        **template_params,
    }
    
    test_synthesis_prompt = synthesis_template.format(**params)
    
    estimated_tokens = estimate_tokens(
        test_synthesis_prompt,
        model=getattr(llm, "model_name", "gpt-4o")
    )
    
    max_allowed = getattr(settings, 'OPENAI_MAX_TOKENS_PER_REQUEST', 80000)
    exceeds_limit = estimated_tokens > max_allowed
    
    return estimated_tokens, exceeds_limit
