# LangChain Core Package

A comprehensive package providing LangChain utilities with token tracking, RAG, and agent support.

## Features

- **OpenAI Provider**: Unified interface for all OpenAI services
- **Embeddings Support**: Easy text embedding generation
- **Chat Models**: Simplified chat interactions
- **LangChain Integration**: Seamless integration with LangChain ecosystem
- **Configuration Management**: Flexible configuration options

## Installation

```bash
pip install abs-langchain-core
```

## Quick Start

### Basic Usage

```python
from abs_langchain_core import OpenAIProvider

# Create provider (uses environment variables)
provider = OpenAIProvider()

# Simple chat
response = provider.chat("Hello, how are you?")
print(response)

# Chat with custom parameters on the fly
response = provider.chat(
    "Tell me a joke",
    temperature=0.9,
    max_tokens=100
)
```

### With Custom Configuration

```python
from abs_langchain_core import OpenAIProvider

# Create provider with custom parameters
provider = OpenAIProvider(
    api_key="your-api-key",
    model_name="gpt-4",
    temperature=0.3,
    max_tokens=150,
    streaming=False,
    base_url="https://api.openai.com/v1"
)

response = provider.chat("Explain quantum computing.")
```

### Using Embeddings

```python
from abs_langchain_core import create_openai_provider

provider = create_openai_provider(api_key="your-api-key")

# Single text embedding
embedding = provider.embed_text("Sample text for embedding")

# Single text embedding with custom parameters
embedding = provider.embed_text(
    "Sample text",
    model="text-embedding-3-small",
    chunk_size=500
)

# Multiple texts with custom parameters
embeddings = provider.embed_text(
    ["First document", "Second document"],
    model="text-embedding-3-large",
    chunk_size=2000
)
```

### Creating LangChain Chains

```python
from abs_langchain_core import OpenAIProvider
from langchain_core.prompts import ChatPromptTemplate

provider = OpenAIProvider()

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "Answer this question: {question}")
])

# Create chain with custom parameters
chain = provider.create_chain(
    prompt,
    temperature=0.1,
    max_tokens=200
)

# Use the chain
result = chain.invoke({"question": "What is Python?"})
print(result.content)

# Create chain with output parser
from langchain_core.output_parsers import StrOutputParser

chain_with_parser = provider.create_chain(
    prompt,
    output_parser=StrOutputParser(),
    temperature=0.3,
    top_p=0.8
)
```

### Custom Parameters

```python
from abs_langchain_core import create_openai_provider

# Create provider with function calling
provider = create_openai_provider(
    functions=[
        {
            "name": "get_weather",
            "description": "Get weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    ],
    function_call="auto"
)

# Chat with custom parameters on the fly
response = provider.chat(
    "What's the weather like in New York?",
    temperature=0.1,
    max_tokens=200
)

# Update parameters dynamically
provider.update_chat_model_kwargs(temperature=0.1, max_tokens=200)

# Get model with custom parameters (doesn't affect cached model)
custom_model = provider.get_chat_model_with_custom_params(
    temperature=0.9,
    top_p=0.8
)
```

### Comprehensive Kwargs Support

All methods support `**kwargs` for maximum flexibility:

```python
# Chat with comprehensive parameters
response = provider.chat(
    "Explain machine learning",
    system_message="You are a technical expert.",
    temperature=0.1,
    max_tokens=200,
    top_p=0.8,
    frequency_penalty=0.1,
    presence_penalty=0.1
)

# Embeddings with custom parameters
embedding = provider.embed_text(
    "Sample text",
    model="text-embedding-3-small",
    chunk_size=500,
    embedding_ctx_length=8191
)

# Raw model access with kwargs
raw_chat = provider.get_raw_chat_model(
    temperature=0.8,
    top_p=0.7
)

raw_embeddings = provider.get_raw_embeddings_model(
    model="text-embedding-3-large",
    chunk_size=2000
)
```

## Configuration

The `OpenAIProvider` class is fully customizable through `**kwargs`. Only essential parameters are explicit:

### Essential Parameters:
- `api_key`: OpenAI API key (uses environment variable if not provided)
- `model_name`: Model name for chat (default: "gpt-3.5-turbo")

### All Other Parameters:
All other parameters are passed through `**kwargs` and can include any valid parameter for:
- **ChatOpenAI**: `temperature`, `max_tokens`, `top_p`, `frequency_penalty`, `presence_penalty`, `timeout`, `max_retries`, `streaming`, `verbose`, `base_url`, `organization`, `functions`, `function_call`, etc.
- **OpenAIEmbeddings**: `model`, `chunk_size`, `embedding_ctx_length`, `max_retries`, `timeout`, etc.

### Parameter Precedence:
1. Parameters passed to methods (highest priority)
2. Parameters in `chat_model_kwargs`/`embeddings_model_kwargs`
3. Parameters passed during initialization
4. Default values (lowest priority)

## Environment Variables

The provider automatically reads these environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_BASE_URL`: Custom base URL
- `OPENAI_ORGANIZATION`: Organization ID

## API Reference

### OpenAIProvider

Main class for interacting with OpenAI services.

#### Methods

- `chat(messages, system_message=None, **kwargs)`: Send chat messages with optional custom parameters
- `embed_text(text, **kwargs)`: Generate embeddings with optional custom parameters
- `create_chain(prompt, output_parser=None, **kwargs)`: Create LangChain chains with custom parameters
- `create_chat_prompt(messages, input_variables=None, **kwargs)`: Create chat prompts with custom parameters
- `update_config(**kwargs)`: Update configuration
- `update_chat_model_kwargs(**kwargs)`: Update custom chat model parameters
- `update_embeddings_model_kwargs(**kwargs)`: Update custom embeddings parameters
- `get_chat_model_with_custom_params(**kwargs)`: Get chat model with custom parameters
- `get_embeddings_model_with_custom_params(**kwargs)`: Get embeddings model with custom parameters
- `get_raw_chat_model(**kwargs)`: Get raw chat model with optional custom parameters
- `get_raw_embeddings_model(**kwargs)`: Get raw embeddings model with optional custom parameters
- `get_config(**kwargs)`: Get current configuration
- `validate_config(**kwargs)`: Validate configuration

### OpenAIProviderConfig

Configuration dataclass for provider settings.

### create_openai_provider()

Convenience function for quick provider setup.

## Examples

See `examples/openai_provider_usage.py` for comprehensive usage examples.

## License

MIT License
