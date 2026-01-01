# Product Self-Knowledge Skill - Claude & Anthropic Expert

## Purpose
Authoritative information about Anthropic products, Claude API, and best practices for AI integration.

## Claude Models Overview

### Current Models (as of 2025)

| Model | Best For | Context | Cost (per 1M tokens) |
|-------|----------|---------|----------------------|
| Claude Opus 4 | Complex reasoning, research, coding | 200K | $15 / $75 |
| Claude Sonnet 4 | Balanced performance, daily tasks | 200K | $3 / $15 |
| Claude Haiku 3.5 | Fast responses, high-volume | 200K | $0.25 / $1.25 |

*Cost format: Input / Output tokens*

### Model Selection Guide

- **Claude Opus 4**: PhD-level analysis, complex code, nuanced writing
- **Claude Sonnet 4**: General coding, content creation, customer support
- **Claude Haiku 3.5**: Classification, extraction, high-throughput tasks

## Claude API Basics

### Authentication

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")
# Or set ANTHROPIC_API_KEY environment variable
```

### Basic Message

```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)
print(message.content[0].text)
```

### System Prompts

```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are a helpful coding assistant. Be concise.",
    messages=[
        {"role": "user", "content": "Explain Python decorators"}
    ]
)
```

### Multi-turn Conversations

```python
messages = [
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What's its population?"}
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=messages
)
```

## Prompt Caching (Beta)

### Overview
Cache large contexts (system prompts, documents) to reduce costs by up to 90%.

### How It Works

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "Your very long system prompt here...",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Pricing

| Token Type | Price (per 1M) |
|------------|----------------|
| Cache Write | $3.75 (25% premium) |
| Cache Read | $0.30 (90% discount!) |
| Regular Input | $3.00 |
| Output | $15.00 |

### Cache Requirements
- Minimum 1024 tokens to cache
- 5-minute TTL (extended on each use)
- Cache hits require exact prefix match

### Best Practices
1. Place static content at the beginning
2. Add `cache_control` to last cacheable block
3. Keep variable content at the end
4. Monitor cache hit rates

## Vision Capabilities

### Sending Images

```python
import base64

# From file
with open("image.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe this image"
                }
            ],
        }
    ],
)

# From URL
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": "https://example.com/image.png",
                    },
                },
                {
                    "type": "text",
                    "text": "What's in this image?"
                }
            ],
        }
    ],
)
```

### Supported Formats
- JPEG, PNG, GIF, WebP
- Max 20MB per image
- Recommended: < 1568 pixels on long edge

## Tool Use (Function Calling)

### Defining Tools

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g., San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in NYC?"}]
)
```

### Handling Tool Calls

```python
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input

            # Execute your function
            result = execute_tool(tool_name, tool_input)

            # Send result back
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    }
                ]
            })

            # Get final response
            final_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                tools=tools,
                messages=messages
            )
```

## Streaming

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## Rate Limits

### Default Limits (Tier 1)

| Metric | Limit |
|--------|-------|
| Requests per minute | 50 |
| Tokens per minute | 40,000 |
| Tokens per day | 1,000,000 |

### Handling Rate Limits

```python
import time
from anthropic import RateLimitError

def call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise
```

## Best Practices

### Prompt Engineering
1. Be specific and clear
2. Provide examples (few-shot)
3. Use structured output formats
4. Break complex tasks into steps
5. Use system prompts for consistent behavior

### Error Handling

```python
from anthropic import (
    Anthropic,
    APIError,
    AuthenticationError,
    RateLimitError,
)

client = Anthropic()

try:
    response = client.messages.create(...)
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limited - retry later")
except APIError as e:
    print(f"API error: {e}")
```

### Token Counting

```python
# Approximate token count (rough estimate)
def estimate_tokens(text):
    return len(text) // 4

# Use response usage for accurate counts
response = client.messages.create(...)
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
```

## References
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Model Comparison](https://docs.anthropic.com/en/docs/models-overview)
- [Prompt Engineering Guide](https://docs.anthropic.com/en/docs/prompt-engineering)
