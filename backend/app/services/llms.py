from app.models import ModelProvider, LlmModel
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from typing import Optional, Any, Dict
from app.api.deps import SessionDep
from sqlmodel import select

def create_llm(provider: ModelProvider, model_id: str, 
               temperature: float = 0.0, 
               api_key: Optional[str] = None,
               additional_params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Factory function to create the appropriate LLM based on provider.
    
    Args:
        provider: The model provider (OpenAI, Ollama, etc.)
        model_id: The model identifier
        temperature: LLM temperature setting
        api_key: Optional API key for providers that require authentication
        additional_params: Additional parameters specific to the LLM provider
        
    Returns:
        An initialized LLM ready for use
    """
    params = additional_params or {}
    
    if provider == ModelProvider.OPENAI:
        # If API key is provided, use it; otherwise, rely on environment variable
        if api_key:
            return ChatOpenAI(
                model=model_id, 
                temperature=temperature,
                openai_api_key=api_key,
                **params
            )
        else:
            return ChatOpenAI(
                model=model_id, 
                temperature=temperature,
                **params
            )
    
    elif provider == ModelProvider.OLLAMA:
        # Configure Ollama
        base_url = params.get("base_url", "http://localhost:11434")
        return ChatOllama(
            model=model_id,
            temperature=temperature,
            base_url=base_url,
            **params
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    

def get_default_llm(session: SessionDep):
    """Get the current default LLM from the database."""
    # Try to get the default model
    default_model = session.exec(
        select(LlmModel)
        .where(LlmModel.is_default == True)
    ).first()

    if default_model:
        print(f"Loading default LLM model: {default_model.name} ({default_model.model_id}, provider: {default_model.provider})")
    
    # If no default model is found, fallback to a hardcoded value
    if not default_model:
        return create_llm(
            provider=ModelProvider.OPENAI,
            model_id="gpt-4o-mini",
            temperature=0.0
        )
    
    return create_llm(
        provider=default_model.provider,
        model_id=default_model.model_id,
        temperature=0.0
    )