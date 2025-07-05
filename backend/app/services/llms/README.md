# LLM Service

A comprehensive service for managing and interacting with Large Language Models (LLMs) across multiple providers.

## Features

- **Multi-provider support**: OpenAI, AWS Bedrock, Ollama, Replicate
- **Model registry**: Centralized registry of available models with metadata
- **Validation**: Model availability and configuration validation
- **Inference**: High-level interface for text generation
- **Provider abstraction**: Unified API across different LLM providers
- **Type safety**: Full TypeScript-style typing with Pydantic models

## Architecture

The service consists of several key components:

### 1. `LlmModelInfo`

Pydantic model containing metadata about each LLM:

- Model ID, provider, and name
- Context length and max output tokens
- Cost information (input/output tokens)
- Capability flags (streaming, function calling, vision)
- Description

### 2. `LlmService`

Main service class with static methods for:

- Model registry management
- Provider validation
- Model instantiation
- Capability queries

### 3. `LlmInferenceService`

High-level interface for LLM interactions:

- Text generation with various parameters
- Chat-style conversations
- Model validation
- Provider-agnostic API

### 4. Provider-specific wrappers

- `ReplicateLlm`: Replicate API wrapper
- `BedrockLlm`: AWS Bedrock wrapper
- Uses LangChain components for OpenAI and Ollama

## Available Models

### OpenAI

- `gpt-4o`: Most advanced multimodal model
- `gpt-4o-mini`: Efficient small model with multimodal capabilities
- `gpt-4-turbo`: Powerful turbo model with extended context
- `gpt-3.5-turbo`: Fast and efficient for most tasks

### AWS Bedrock

- `anthropic.claude-3-5-sonnet-20241022-v2:0`: Most capable Claude model
- `anthropic.claude-3-haiku-20240307-v1:0`: Fastest Claude model
- `amazon.titan-text-express-v1`: Amazon's text generation model

### Ollama (Local)

- `llama3.1:8b`: Meta's Llama 3.1 8B model
- `llama3.1:70b`: Meta's Llama 3.1 70B model
- `mistral:7b`: Mistral 7B model

### Replicate

- `meta/llama-2-70b-chat`: Llama 2 70B Chat model
- `mistralai/mixtral-8x7b-instruct-v0.1`: Mixtral 8x7B Instruct model

## Usage

### Basic Usage

```python
from app.services.llms import LlmService, LlmInferenceService

# Get all available models
models = LlmService.get_models()

# Get models by provider
openai_models = LlmService.get_models_by_provider("openai")

# Validate a model
is_valid, error = LlmService.validate_model("gpt-4o-mini")

# Create inference service
service = LlmInferenceService("gpt-4o-mini")

# Generate text
response = service.generate_text(
    "Explain machine learning in simple terms.",
    temperature=0.7,
    max_tokens=150
)
```

### Advanced Usage

```python
# Chat with system prompt
response = service.generate_text(
    "What's the weather like?",
    system_prompt="You are a helpful weather assistant.",
    temperature=0.3
)

# Chat response from message history
messages = [
    {"role": "system", "content": "You are a coding assistant."},
    {"role": "user", "content": "How do I create a Python list?"},
]

response = service.generate_chat_response(
    messages,
    temperature=0.1,
    max_tokens=100
)

# Model validation
is_valid, message = service.validate_model_connection()

# Get model information
model_info = service.get_model_info()
```

### Provider-Specific Examples

```python
# OpenAI
openai_service = LlmInferenceService("gpt-3.5-turbo")

# AWS Bedrock
aws_service = LlmInferenceService("anthropic.claude-3-haiku-20240307-v1:0")

# Ollama
ollama_service = LlmInferenceService("llama3.1:8b")

# Replicate
replicate_service = LlmInferenceService("meta/llama-2-70b-chat")
```

## Configuration

### Environment Variables

#### OpenAI

```bash
OPENAI_API_KEY=your_openai_api_key
```

#### AWS Bedrock

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region  # e.g., us-east-1
```

#### Ollama

```bash
OLLAMA_HOST=http://localhost:11434  # Default
```

#### Replicate

```bash
REPLICATE_API_TOKEN=your_replicate_token
```

### Default Model

Set the default LLM model in your configuration:

```python
# In app/core/config.py
DEFAULT_LLM_MODEL = "gpt-4o-mini"
```

## Error Handling

The service provides comprehensive error handling:

```python
try:
    service = LlmInferenceService("gpt-4o-mini")
    response = service.generate_text("Hello, world!")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Extending the Service

### Adding New Models

To add a new model to the registry:

```python
# In main.py, add to AVAILABLE_MODELS
"new-model-id": LlmModelInfo(
    id="new-model-id",
    provider="provider-name",
    model_name="provider-model-name",
    context_length=128000,
    max_output_tokens=4096,
    cost_per_1k_input_tokens=1.0,
    cost_per_1k_output_tokens=2.0,
    supports_streaming=True,
    supports_function_calling=False,
    supports_vision=False,
    description="Description of the new model",
)
```

### Adding New Providers

1. Create a new wrapper class (similar to `ReplicateLlm`)
2. Add validation logic in `LlmService.validate_model()`
3. Add instantiation logic in `LlmService.get_model()`
4. Add models to the registry

## Testing

Run the example usage file to test the service:

```bash
python backend/app/services/llms/example_usage.py
```

## API Reference

### LlmService

- `get_models()`: Get all available models
- `get_default_model()`: Get the default model
- `get_providers()`: Get available providers
- `get_model_ids()`: Get all model IDs
- `is_valid_model_id(model_id)`: Check if model ID is valid
- `get_model_spec(model_id)`: Get model specification
- `get_models_by_provider(provider)`: Get models by provider
- `validate_model(model_id, api_key)`: Validate model configuration
- `get_model(model_id, api_key, **kwargs)`: Get model instance

### LlmInferenceService

- `__init__(model_id, api_key, **kwargs)`: Initialize with model
- `generate_text(prompt, **kwargs)`: Generate text from prompt
- `generate_chat_response(messages, **kwargs)`: Generate chat response
- `validate_model_connection()`: Test model connection
- `get_model_info()`: Get model information

### LlmModelInfo

- `id`: Model identifier
- `provider`: Provider name
- `model_name`: Provider-specific model name
- `context_length`: Maximum context length
- `max_output_tokens`: Maximum output tokens
- `cost_per_1k_input_tokens`: Cost per 1K input tokens
- `cost_per_1k_output_tokens`: Cost per 1K output tokens
- `supports_streaming`: Whether model supports streaming
- `supports_function_calling`: Whether model supports function calling
- `supports_vision`: Whether model supports vision
- `description`: Model description
