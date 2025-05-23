import replicate  
import os
from app.models import ModelProvider, LlmModel
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from typing import Optional, Any, Dict
from app.api.deps import SessionDep
from sqlmodel import select
from langchain_community.llms import Replicate  
from langchain.schema import HumanMessage

class ReplicateWrapper:
    """Wrapper for Replicate API to make it compatible with our interface"""
    
    def __init__(self, model_id: str, temperature: float = 0.0, **kwargs):
        self.model_id = model_id
        self.temperature = temperature
        self.kwargs = kwargs
        
        # Check if we have a modelversion format (owner/model:version)
        if ":" in model_id:
            self.owner_model, self.version = model_id.split(":")
        else:
            self.owner_model = model_id
            self.version = None

    def invoke(self, prompt):
        """Run the model with the provided prompt"""
        if isinstance(prompt, str):
            input_text = prompt
            system_prompt = self.kwargs.get("system_prompt", "")
        elif hasattr(prompt, 'content'):
            input_text = prompt.content
            system_prompt = self.kwargs.get("system_prompt", "")
        else:
            # Handle list of messages by identifying system and user messages
            system_messages = [msg.content for msg in prompt if hasattr(msg, 'type') and msg.type == 'system']
            user_messages = [msg.content for msg in prompt if hasattr(msg, 'content') and not (hasattr(msg, 'type') and msg.type == 'system')]
            
            system_prompt = system_messages[0] if system_messages else self.kwargs.get("system_prompt", "")
            input_text = "\n".join(user_messages)
            
        try:
            # Prepare input with proper structure for Replicate models
            input_params = {
                "prompt": input_text,
                "temperature": self.temperature,
            }
            
            # Add system prompt if available
            if system_prompt:
                input_params["system_prompt"] = system_prompt
                
            # Add any additional parameters from kwargs that should be passed to the model
            for key, value in self.kwargs.items():
                if key not in ["system_prompt"]:  # Skip already handled keys
                    input_params[key] = value
                    
            print(f"Running Replicate model: {self.model_id}")
            print(f"Input parameters: {input_params}")
            
            # Use Replicate's stream function for better compatibility
            if self.kwargs.get("streaming", False):
                # For streaming, we'll gather chunks and join them
                chunks = []
                for chunk in replicate.stream(
                    self.model_id if self.version else self.owner_model,
                    input=input_params
                ):
                    chunks.append(chunk)
                return "".join(chunks)
            else:
                # For non-streaming use case
                output = replicate.run(
                    self.model_id if self.version else self.owner_model,
                    input=input_params
                )
                
                # Handle various output formats
                if isinstance(output, list):
                    return output[0] if len(output) == 1 else "".join(output)
                return output
        except Exception as e:
            print(f"Error running Replicate model: {e}")
            raise

def create_llm(provider: ModelProvider, model_id: str, 
               temperature: float = 0.0, 
               api_key: Optional[str] = None,
               additional_params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Factory function to create the appropriate LLM based on provider.
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
        base_url = params.get("OLLAMA_BASE_URL", "http://ollama:11434")
        return ChatOllama(
            model=model_id,
            temperature=temperature,
            base_url=base_url,
            **params
        )
    
    elif provider == ModelProvider.REPLICATE:
        # Configure Replicate
        if api_key:
            print("API key provided with length:", len(api_key))
            os.environ["REPLICATE_API_TOKEN"] = api_key
        

        print(f"Creating Replicate LLM wrapper for model: {model_id}")
        print(f"REPLICATE_API_TOKEN set: {'Yes' if 'REPLICATE_API_TOKEN' in os.environ else 'No'}")
        print(f"Token length: {len(os.environ.get('REPLICATE_API_TOKEN', ''))}")
        
        print("Now creating Replicate LLM wrapper...")
        wrapper = ReplicateWrapper(
            model_id=model_id,
            temperature=temperature,
            **params
        )
        print("Replicate LLM wrapper created successfully.")
        # Create a Replicate wrapper
        return wrapper
    
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