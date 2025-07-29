# HACS OpenAI Integration

Generic OpenAI integration for HACS providing embeddings, structured outputs, tool calling, and configurable clients that work with any HACS types.

## Features

- **Embeddings**: OpenAI embedding models for vectorization
- **Structured Outputs**: Generate any HACS model using instructor or native structured outputs
- **Tool Calling**: Both legacy function calling and new tool calling formats
- **Configurable Clients**: Fully configurable OpenAI clients with custom parameters
- **Generic Utilities**: Work with any HACS Pydantic models
- **Batch Processing**: Efficient batch operations for high-volume use cases

## Installation

```bash
pip install hacs-openai
```

## Quick Start

### Basic Client Setup

```python
from hacs_openai import create_openai_client

# Basic client with defaults
client = create_openai_client()

# Custom configuration
client = create_openai_client(
    model="gpt-4o",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",  # Custom API URL
    temperature=0.7,
    max_tokens=4096
)
```

### Structured Output Generation

```python
from hacs_openai import create_structured_generator
from hacs_models import Patient

# Create generator
generator = create_structured_generator(
    model="gpt-4o",
    temperature=0.3,  # Lower for structured output
    api_key="your-api-key"
)

# Generate any HACS model
patient = generator.generate_hacs_resource(
    resource_type=Patient,
    user_prompt="Create a patient record for John Doe, 30 years old, male"
)

print(f"Generated: {patient.display_name}")
```

### Tool Calling

```python
from hacs_openai import OpenAIClient, OpenAIToolRegistry

# Setup client and tool registry
client = OpenAIClient()
registry = OpenAIToolRegistry()

# Register any function as a tool
def calculate_value(input_data: str, multiplier: int = 1) -> str:
    return f"Result: {input_data} * {multiplier}"

registry.register_tool(
    name="calculate_value",
    function=calculate_value,
    description="Calculate a value with multiplier",
    parameters={
        "type": "object",
        "properties": {
            "input_data": {"type": "string"},
            "multiplier": {"type": "integer", "default": 1}
        },
        "required": ["input_data"]
    }
)

# Use tools in conversation
response = client.tool_call(
    messages=[
        {"role": "user", "content": "Calculate value for 'test' with multiplier 5"}
    ],
    tools=registry.get_tools()
)
```

### Embeddings for Vector Search

```python
from hacs_openai import create_openai_embedding

# Create embedding model
embedding_model = create_openai_embedding(
    model="text-embedding-3-small",
    api_key="your-api-key"
)

# Generate embeddings
text = "Any text content"
embedding = embedding_model.embed(text)
print(f"Embedding dimensions: {len(embedding)}")
```

## Advanced Usage

### Custom System Prompts

```python
from hacs_openai import OpenAIStructuredGenerator

# Custom system prompt
system_prompt = """You are an AI assistant that generates structured data.
Follow the provided schema exactly and ensure all required fields are populated."""

generator = OpenAIStructuredGenerator(
    model="gpt-4o",
    temperature=0.3,
    system_prompt=system_prompt
)

# Generate with custom prompt
result = generator.generate_hacs_resource(
    resource_type=YourModel,
    user_prompt="Generate data based on this input"
)
```

### Batch Processing

```python
from hacs_openai import create_structured_generator

generator = create_structured_generator()

# Generate multiple resources
prompts = [
    "Generate first resource",
    "Generate second resource", 
    "Generate third resource"
]

results = generator.generate_batch_resources(
    resource_type=YourModel,
    prompts=prompts
)

for result in results:
    if result:
        print(f"Generated: {result}")
```

### Native Structured Outputs

```python
from hacs_openai import OpenAIClient

client = OpenAIClient()

# Use OpenAI's native structured output
response = client.native_structured_output(
    messages=[
        {"role": "user", "content": "Generate structured data"}
    ],
    response_schema=YourModel.model_json_schema()
)

# Parse response
result = YourModel(**response)
```

## Configuration

### Environment Variables

```bash
# OpenAI API configuration
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_URL="https://api.openai.com/v1"  # Custom API URL
export OPENAI_ORGANIZATION="your-org-id"

# Default model settings
export OPENAI_DEFAULT_MODEL="gpt-4o"
export OPENAI_DEFAULT_TEMPERATURE="0.7"
```

### Client Configuration

```python
from hacs_openai import OpenAIClient

# Fully configured client
client = OpenAIClient(
    model="gpt-4o",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    organization="your-org-id",
    timeout=30.0,
    max_retries=3,
    temperature=0.7,
    max_tokens=4096,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
)
```

## Error Handling

```python
from hacs_openai import create_structured_generator
import openai

generator = create_structured_generator()

try:
    result = generator.generate_hacs_resource(
        resource_type=YourModel,
        user_prompt="Generate data"
    )
except openai.APIError as e:
    print(f"OpenAI API error: {e}")
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Optimization

### Batch Operations

```python
# Process multiple requests efficiently
results = generator.generate_batch_resources(
    resource_type=YourModel,
    prompts=batch_prompts,
    max_tokens=1000,  # Limit tokens per request
    temperature=0.1   # Lower temperature for consistency
)
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate(prompt: str) -> YourModel:
    return generator.generate_hacs_resource(
        resource_type=YourModel,
        user_prompt=prompt
    )
```

## Generic Features

### Work with Any HACS Model

The utilities work with any Pydantic model:

```python
from pydantic import BaseModel
from hacs_openai import create_structured_generator

class CustomModel(BaseModel):
    name: str
    value: int
    description: str

generator = create_structured_generator()
result = generator.generate_hacs_resource(
    resource_type=CustomModel,
    user_prompt="Generate a custom model instance"
)
```

### Tool Integration

```python
# Register tools that work with any data
def process_data(data: dict, operation: str) -> dict:
    # Generic data processing
    return {"processed": data, "operation": operation}

registry = OpenAIToolRegistry()
registry.register_tool(
    name="process_data",
    function=process_data,
    description="Process any data with specified operation",
    parameters={
        "type": "object",
        "properties": {
            "data": {"type": "object"},
            "operation": {"type": "string"}
        },
        "required": ["data", "operation"]
    }
)
```

## API Reference

### Classes

- `OpenAIClient`: Enhanced OpenAI client with HACS integration
- `OpenAIStructuredGenerator`: Generate any HACS model from text
- `OpenAIToolRegistry`: Registry for tools and functions
- `OpenAIEmbedding`: Embedding model for vectorization

### Functions

- `create_openai_client()`: Create configured OpenAI client
- `create_structured_generator()`: Create structured output generator
- `create_openai_embedding()`: Create embedding model
- `create_openai_vectorizer()`: Create complete vectorizer

## Contributing

See [Contributing Guidelines](../../CONTRIBUTING.md) for development setup and contribution process.

## License

Apache License 2.0 - see [LICENSE](../../LICENSE) for details. 