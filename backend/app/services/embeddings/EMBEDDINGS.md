# embeddings service

the embeddings service provides a unified interface for managing and using different embedding models.

# initialization

the embeddings service is used through static methods and doesn't require initialization. import it directly from the service:

```python
from app.services.embeddings import EmbeddingService
```

# available methods

#### `get_models()`

returns a list of all available embedding models.

**returns**

- `List[EmbeddingModelInfo]` - list of all available models

**usage**

```python
models = EmbeddingService.get_models()
```

---

#### `get_default_model()`

returns the default embedding model configured in settings.

**returns**

- `EmbeddingModelInfo` - default model information

**usage**

```python
default_model = EmbeddingService.get_default_model()
```

---

#### `get_providers()`

returns a list of all available embedding providers.

**returns**

- `List[str]` - list of provider names

**usage**

```python
providers = EmbeddingService.get_providers()
```

---

#### `get_model_ids()`

returns a list of all available model IDs.

**returns**

- `List[str]` - list of model identifiers

**usage**

```python
model_ids = EmbeddingService.get_model_ids()
```

---

#### `is_valid_model_id(model_id)`

checks if a model ID is valid and available.

**parameters**

- `model_id: str` - model identifier to validate

**returns**

- `bool` - true if valid, false otherwise

**usage**

```python
is_valid = EmbeddingService.is_valid_model_id("text-embedding-3-small")
```

---

#### `get_model_spec(model_id)`

gets detailed specification for a specific model.

**parameters**

- `model_id: str` - model identifier

**returns**

- `Optional[EmbeddingModelInfo]` - model specification or None if not found

**usage**

```python
spec = EmbeddingService.get_model_spec("text-embedding-3-small")
```

---

#### `get_models_by_provider(provider)`

gets all models for a specific provider.

**parameters**

- `provider: str` - provider name (e.g., "openai", "aws")

**returns**

- `List[EmbeddingModelInfo]` - list of models for the provider

**usage**

```python
openai_models = EmbeddingService.get_models_by_provider("openai")
```

---

#### `validate_model(model_id, api_key=None)`

validates if a model is available and properly configured.

**parameters**

- `model_id: str` - model identifier to validate
- `api_key: Optional[str]` - optional API key override

**returns**

- `tuple[bool, Optional[str]]` - (is_valid, error_message)

**validation checks**

- model exists in registry
- required environment variables are set
- provider-specific credentials are available

**usage**

```python
is_valid, error = EmbeddingService.validate_model("text-embedding-3-small")
```

---

#### `get_model(model_id, api_key=None)`

gets an initialized embedding model instance.

**parameters**

- `model_id: str` - model identifier from the registry
- `api_key: Optional[str]` - optional API key override

**returns**

- `Embeddings` - initialized embeddings model

**usage**

```python
embeddings = EmbeddingService.get_model("text-embedding-3-small")
vector = embeddings.embed_query("hello world")
vectors = embeddings.embed_documents(["text 1", "text 2"])
```

---

#### `ReplicateEmbeddings(model_id, api_key=None)`

custom embeddings implementation for Replicate API models.

**parameters**

- `model_id: str` - the model identifier on Replicate
- `api_key: Optional[str]` - optional API key for Replicate

**methods**

- `embed_documents(texts)` - embeds a list of texts using batch processing
- `embed_query(text)` - embeds a single query text

**features**

- attempts batch processing for efficiency
- falls back to individual embedding if batch fails
- handles various output formats from Replicate
- provides zero-vector fallback for failed embeddings

**usage**

```python
embeddings = ReplicateEmbeddings("sentence-transformers/all-MiniLM-L6-v2")
vector = embeddings.embed_query("hello world")
```

# schema

#### `EmbeddingModelInfo`

pydantic model for embedding model information.

```python
class EmbeddingModelInfo(BaseModel):
    id: str                                 # unique model identifier
    provider: str                           # provider name (openai, aws, replicate)
    model_name: str                         # actual model name used by provider
    dimensions: int                         # embedding vector dimensions
    max_input_length: Optional[int] = None  # maximum input tokens
    cost_per_1M_tokens: Optional[float] = None  # cost per 1M tokens
    description: Optional[str] = None       # model description
```

---

#### available models registry

##### openai models

```python
"text-embedding-3-small": EmbeddingModelInfo(
    id="text-embedding-3-small",
    provider="openai",
    model_name="text-embedding-3-small",
    dimensions=1536,
    max_input_length=8191,
    cost_per_1M_tokens=0.02,
    description="OpenAI's efficient small embedding model"
)

"text-embedding-3-large": EmbeddingModelInfo(
    id="text-embedding-3-large",
    provider="openai",
    model_name="text-embedding-3-large",
    dimensions=3072,
    max_input_length=8191,
    cost_per_1M_tokens=0.13,
    description="OpenAI's high-performance large embedding model"
)

"text-embedding-ada-002": EmbeddingModelInfo(
    id="text-embedding-ada-002",
    provider="openai",
    model_name="text-embedding-ada-002",
    dimensions=1536,
    max_input_length=8191,
    cost_per_1M_tokens=0.1,
    description="OpenAI's legacy embedding model"
)
```

##### aws bedrock models

```python
"amazon.titan-embed-text-v2:0": EmbeddingModelInfo(
    id="amazon.titan-embed-text-v2:0",
    provider="aws",
    model_name="amazon.titan-embed-text-v2:0",
    dimensions=1024,
    max_input_length=8192,
    cost_per_1M_tokens=0.021,
    description="Amazon's Titan 2.0 embedding model for AWS Bedrock"
)

"cohere.embed-english-v3": EmbeddingModelInfo(
    id="cohere.embed-english-v3",
    provider="aws",
    model_name="cohere.embed-english-v3",
    dimensions=1024,
    max_input_length=512,
    cost_per_1M_tokens=0.1,
    description="Cohere's English embedding model available on AWS Bedrock"
)

"cohere.embed-multilingual-v3": EmbeddingModelInfo(
    id="cohere.embed-multilingual-v3",
    provider="aws",
    model_name="cohere.embed-multilingual-v3",
    dimensions=1024,
    max_input_length=512,
    cost_per_1M_tokens=0.1,
    description="Cohere's multilingual embedding model available on AWS Bedrock"
)
```

---

#### environment variables

##### openai provider

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

##### aws bedrock provider

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1  # or AWS_REGION
```

##### replicate provider

```bash
REPLICATE_API_TOKEN=your_replicate_api_token
```

---

#### error handling

##### model validation errors

```python
# invalid model ID
is_valid, error = EmbeddingService.validate_model("invalid-model")
# returns: (False, "Model 'invalid-model' not found. Available models: ...")

# missing API key
is_valid, error = EmbeddingService.validate_model("text-embedding-3-small")
# returns: (False, "OPENAI_API_KEY environment variable required...")

# missing AWS credentials
is_valid, error = EmbeddingService.validate_model("amazon.titan-embed-text-v2:0")
# returns: (False, "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables required...")
```

##### model loading errors

```python
try:
    embeddings = EmbeddingService.get_model("text-embedding-3-small")
except ValueError as e:
    # could be due to invalid credentials, network issues, etc.
    print(f"failed to load model: {e}")
```

---

#### provider-specific features

##### openai

- supports OpenAI's latest embedding models
- automatic API key management
- standard langchain interface

##### aws bedrock

- supports Amazon Titan and Cohere models
- automatic AWS credential management
- region-aware configuration

##### replicate

- custom implementation for Replicate API
- batch processing support
- complex output format handling
- automatic fallback mechanisms
