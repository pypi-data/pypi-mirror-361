# SVECTOR Python SDK

[![PyPI version](https://img.shields.io/pypi/v/svector-sdk.svg)](https://pypi.org/project/svector-sdk/)  
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-blue.svg)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![Downloads](https://img.shields.io/pypi/dm/svector-sdk.svg)](https://pypi.org/project/svector-sdk/)

**Official Python SDK for accessing SVECTOR APIs.**

SVECTOR develops high-performance AI models and automation solutions, specializing in artificial intelligence, mathematical computing, and computational research. This Python SDK provides programmatic access to SVECTOR's API services, offering intuitive model completions, document processing, and seamless integration with SVECTOR's advanced AI systems (e.g., Spec-3, Spec-3-Turbo, Theta-35).

The library includes type hints for request parameters and response fields, and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx) and [requests](https://github.com/psf/requests).

## Quick Start

```bash
pip install svector-sdk
```

```python
from svector import SVECTOR

client = SVECTOR(api_key="your-api-key")  # or set SVECTOR_API_KEY env var

# Conversational API - just provide instructions and input!
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful AI assistant that explains complex topics clearly.",
    input="What is artificial intelligence?",
)

print(response.output)
```

## Table of Contents

- [Installation](#installation)
- [Authentication](#authentication)
- [Core Features](#core-features)
- [Conversations API (Recommended)](#conversations-api-recommended)
- [Chat Completions API (Advanced)](#chat-completions-api-advanced)
- [Streaming Responses](#streaming-responses)
- [File Management & Document Processing](#file-management--document-processing)
- [Models](#models)
- [Error Handling](#error-handling)
- [Async Support](#async-support)
- [Advanced Configuration](#advanced-configuration)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)
- [Contributing](#contributing)

## Installation

### pip
```bash
pip install svector-sdk
```

### Development Install
```bash
git clone https://github.com/svector-corporation/svector-python
cd svector-python
pip install -e ".[dev]"
```

## Authentication

Get your API key from the [SVECTOR Dashboard](https://www.svector.co.in) and set it as an environment variable:

```bash
export SVECTOR_API_KEY="your-api-key-here"
```

Or pass it directly to the client:

```python
from svector import SVECTOR

client = SVECTOR(api_key="your-api-key-here")
```

## Core Features

- **Conversations API** - Simple instructions + input interface
- **Advanced Chat Completions** - Full control with role-based messages
- **Real-time Streaming** - Server-sent events for live responses
- **File Processing** - Upload and process documents (PDF, DOCX, TXT, etc.)
- **Knowledge Collections** - Organize files for enhanced RAG
- **Type Safety** - Full type hints and IntelliSense support
- **Async Support** - AsyncSVECTOR client for high-performance applications
- **Robust Error Handling** - Comprehensive error types and retry logic
- **Multi-environment** - Works everywhere Python runs

## Conversations API (Recommended)

The **Conversations API** provides a, user-friendly interface. Just provide instructions and input - the SDK handles all the complex role management internally!

### Basic Conversation

```python
from svector import SVECTOR

client = SVECTOR()

response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful assistant that explains things clearly.",
    input="What is machine learning?",
    temperature=0.7,
    max_tokens=200,
)

print(response.output)
print(f"Request ID: {response.request_id}")
print(f"Token Usage: {response.usage}")
```

### Conversation with Context

```python
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a programming tutor that helps students learn coding.",
    input="Can you show me an example?",
    context=[
        "How do I create a function in Python?",
        "You can create a function using the def keyword followed by the function name and parameters..."
    ],
    temperature=0.5,
)
```

### Streaming Conversation

```python
stream = client.conversations.create_stream(
    model="spec-3-turbo",
    instructions="You are a creative storyteller.",
    input="Tell me a short story about robots and humans.",
    stream=True,
)

print("Story: ", end="", flush=True)
for event in stream:
    if not event.done:
        print(event.content, end="", flush=True)
    else:
        print("\nStory completed!")
```

### Document-based Conversation

```python
# First upload a document
with open("research-paper.pdf", "rb") as f:
    file_response = client.files.create(f, purpose="default")

# Then ask questions about it
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a research assistant that analyzes documents.",
    input="What are the key findings in this paper?",
    files=[{"type": "file", "id": file_response.file_id}],
)
```

## Chat Completions API (Advanced)

For full control over the conversation structure, use the Chat Completions API with role-based messages:

### Basic Chat

```python
response = client.chat.create(
    model="spec-3-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ],
    max_tokens=150,
    temperature=0.7,
)

print(response["choices"][0]["message"]["content"])
```

### Multi-turn Conversation

```python
conversation = [
    {"role": "system", "content": "You are a helpful programming assistant."},
    {"role": "user", "content": "How do I reverse a string in Python?"},
    {"role": "assistant", "content": "You can reverse a string using slicing: string[::-1]"},
    {"role": "user", "content": "Can you show me other methods?"}
]

response = client.chat.create(
    model="spec-3-turbo",
    messages=conversation,
    temperature=0.5,
)
```

### Developer Role (System-level Instructions)

```python
response = client.chat.create(
    model="spec-3-turbo",
    messages=[
        {"role": "developer", "content": "You are an expert code reviewer. Provide detailed feedback."},
        {"role": "user", "content": "Please review this Python code: def add(a, b): return a + b"}
    ],
)
```

## Streaming Responses

Both Conversations and Chat APIs support real-time streaming:

### Conversations Streaming

```python
stream = client.conversations.create_stream(
    model="spec-3-turbo",
    instructions="You are a creative writer.",
    input="Write a poem about technology.",
    stream=True,
)

for event in stream:
    if not event.done:
        print(event.content, end="", flush=True)
    else:
        print("\nStream completed")
```

### Chat Streaming

```python
stream = client.chat.create_stream(
    model="spec-3-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    stream=True,
)

for event in stream:
    if "choices" in event and len(event["choices"]) > 0:
        delta = event["choices"][0].get("delta", {})
        content = delta.get("content", "")
        if content:
            print(content, end="", flush=True)
```

## File Management & Document Processing

Upload and process various file formats for enhanced AI capabilities:

### Upload from File

```python
from pathlib import Path

# PDF document
with open("document.pdf", "rb") as f:
    pdf_file = client.files.create(f, purpose="default")

# Text file from path
file_response = client.files.create(
    Path("notes.txt"), 
    purpose="default"
)

print(f"File uploaded: {file_response.file_id}")
```

### Upload from Bytes

```python
with open("document.pdf", "rb") as f:
    data = f.read()

file_response = client.files.create(
    data, 
    purpose="default", 
    filename="document.pdf"
)
```

### Upload from String Content

```python
content = """
# Research Notes
This document contains important findings...
"""

file_response = client.files.create(
    content.encode(), 
    purpose="default", 
    filename="notes.md"
)
```

### Document Q&A

```python
# Upload documents
with open("manual.pdf", "rb") as f:
    doc1 = client.files.create(f, purpose="default")

with open("faq.docx", "rb") as f:
    doc2 = client.files.create(f, purpose="default")

# Ask questions about the documents
answer = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful assistant that answers questions based on the provided documents.",
    input="What are the key features mentioned in the manual?",
    files=[
        {"type": "file", "id": doc1.file_id},
        {"type": "file", "id": doc2.file_id}
    ],
)
```

## Knowledge Collections

Organize multiple files into collections for better performance and context management:

```python
# Add files to a knowledge collection
result1 = client.knowledge.add_file("collection-123", "file-456")
result2 = client.knowledge.add_file("collection-123", "file-789")

# Use the entire collection in conversations
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a research assistant with access to our knowledge base.",
    input="Summarize all the information about our products.",
    files=[{"type": "collection", "id": "collection-123"}],
)
```

## Models

SVECTOR provides several cutting-edge foundational AI models:

### Available Models

```python
# List all available models
models = client.models.list()
print(models["models"])
```

**SVECTOR's Foundational Models:**

- **`spec-3-turbo`** - Fast, efficient model for most use cases
- **`spec-3`** - Standard model with balanced performance  
- **`theta-35-mini`** - Lightweight model for simple tasks
- **`theta-35`** - Advanced model for complex reasoning

### Model Selection Guide

```python
# For quick responses and general tasks
quick_response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful assistant.",
    input="What time is it?",
)

# For complex reasoning and analysis
complex_analysis = client.conversations.create(
    model="theta-35",
    instructions="You are an expert data analyst.",
    input="Analyze the trends in this quarterly report.",
    files=[{"type": "file", "id": "report-file-id"}],
)

# For lightweight tasks
simple_task = client.conversations.create(
    model="theta-35-mini",
    instructions="You help with simple questions.",
    input="What is 2 + 2?",
)
```

## Error Handling

The SDK provides comprehensive error handling with specific error types:

```python
from svector import (
    SVECTOR, 
    AuthenticationError, 
    RateLimitError, 
    NotFoundError,
    APIError
)

client = SVECTOR()

try:
    response = client.conversations.create(
        model="spec-3-turbo",
        instructions="You are a helpful assistant.",
        input="Hello world",
    )
    
    print(response.output)
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
    print("Get your API key from https://www.svector.co.in")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print("Please wait before making another request")
except NotFoundError as e:
    print(f"Resource not found: {e}")
except APIError as e:
    print(f"API error: {e} (Status: {e.status_code})")
    print(f"Request ID: {getattr(e, 'request_id', 'N/A')}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Available Error Types

- **`AuthenticationError`** - Invalid API key or authentication issues
- **`PermissionDeniedError`** - Insufficient permissions for the resource
- **`NotFoundError`** - Requested resource not found
- **`RateLimitError`** - API rate limit exceeded
- **`UnprocessableEntityError`** - Invalid request data or parameters
- **`InternalServerError`** - Server-side errors
- **`APIConnectionError`** - Network connection issues
- **`APIConnectionTimeoutError`** - Request timeout

## Async Support

The SDK provides full async support with `AsyncSVECTOR`:

### Async Basic Usage

```python
import asyncio
from svector import AsyncSVECTOR

async def main():
    async with AsyncSVECTOR() as client:
        response = await client.conversations.create(
            model="spec-3-turbo",
            instructions="You are a helpful assistant.",
            input="Explain quantum computing in simple terms.",
        )
        print(response.output)

asyncio.run(main())
```

### Async Streaming

```python
async def streaming_example():
    async with AsyncSVECTOR() as client:
        stream = await client.conversations.create_stream(
            model="spec-3-turbo",
            instructions="You are a creative storyteller.",
            input="Write a poem about technology.",
            stream=True,
        )
        
        async for event in stream:
            if not event.done:
                print(event.content, end="", flush=True)
        print()

asyncio.run(streaming_example())
```

### Async Concurrent Requests

```python
async def concurrent_example():
    async with AsyncSVECTOR() as client:
        # Multiple async conversations
        tasks = [
            client.conversations.create(
                model="spec-3-turbo",
                instructions="You are a helpful assistant.",
                input=f"What is {topic}?"
            )
            for topic in ["artificial intelligence", "quantum computing", "blockchain"]
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        topics = ["artificial intelligence", "quantum computing", "blockchain"]
        for topic, response in zip(topics, responses):
            if isinstance(response, Exception):
                print(f"{topic}: Error - {response}")
            else:
                print(f"{topic}: {response.output[:100]}...")

asyncio.run(concurrent_example())
```

## Advanced Configuration

### Client Configuration

```python
from svector import SVECTOR

client = SVECTOR(
    api_key="your-api-key",
    base_url="https://api.svector.co.in",           # Custom API endpoint
    timeout=30,                                  # Request timeout in seconds
    max_retries=3,                               # Retry failed requests
    verify_ssl=True,                             # SSL verification
    http_client=None,                            # Custom HTTP client
)
```

### Async Configuration

```python
from svector import AsyncSVECTOR

client = AsyncSVECTOR(
    api_key="your-api-key",
    timeout=30,
    max_retries=3,
)
```

### Per-request Options

```python
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful assistant.",
    input="Hello",
    timeout=60,           # Override timeout for this request
    headers={             # Additional headers
        "X-Custom-Header": "value",
        "X-Request-Source": "my-app"
    }
)
```

### Raw Response Access

```python
# Get both response data and raw HTTP response
response, raw = client.conversations.create_with_response(
    model="spec-3-turbo",
    instructions="You are a helpful assistant.",
    input="Hello",
)

print(f"Status: {raw.status_code}")
print(f"Headers: {raw.headers}")
print(f"Response: {response.output}")
print(f"Request ID: {response.request_id}")
```

## Complete Examples

### Intelligent Chat Application

```python
from svector import SVECTOR

class IntelligentChat:
    def __init__(self, api_key: str):
        self.client = SVECTOR(api_key=api_key)
        self.conversation_history = []

    def chat(self, user_message: str, system_instructions: str = None) -> str:
        # Add user message to history
        self.conversation_history.append(user_message)

        response = self.client.conversations.create(
            model="spec-3-turbo",
            instructions=system_instructions or "You are a helpful and friendly AI assistant.",
            input=user_message,
            context=self.conversation_history[-10:],  # Keep last 10 messages
            temperature=0.7,
        )

        # Add AI response to history
        self.conversation_history.append(response.output)
        return response.output

    def stream_chat(self, user_message: str):
        print("Assistant: ", end="", flush=True)
        
        stream = self.client.conversations.create_stream(
            model="spec-3-turbo",
            instructions="You are a helpful AI assistant. Be conversational and engaging.",
            input=user_message,
            context=self.conversation_history[-6:],
            stream=True,
        )

        full_response = ""
        for event in stream:
            if not event.done:
                print(event.content, end="", flush=True)
                full_response += event.content
        print()

        self.conversation_history.append(user_message)
        self.conversation_history.append(full_response)

    def clear_history(self):
        self.conversation_history = []

# Usage
import os
chat = IntelligentChat(os.environ.get("SVECTOR_API_KEY"))

# Regular chat
print(chat.chat("Hello! How are you today?"))

# Streaming chat
chat.stream_chat("Tell me an interesting fact about space.")

# Specialized chat
print(chat.chat(
    "Explain quantum computing", 
    "You are a physics professor who explains complex topics in simple terms."
))
```

### Document Analysis System

```python
from svector import SVECTOR
from pathlib import Path

class DocumentAnalyzer:
    def __init__(self):
        self.client = SVECTOR()
        self.uploaded_files = []

    def add_document(self, file_path: str) -> str:
        try:
            with open(file_path, "rb") as f:
                file_response = self.client.files.create(
                    f, 
                    purpose="default",
                    filename=Path(file_path).name
                )
            
            self.uploaded_files.append(file_response.file_id)
            print(f"Uploaded: {file_path} (ID: {file_response.file_id})")
            return file_response.file_id
        except Exception as error:
            print(f"Failed to upload {file_path}: {error}")
            raise error

    def add_document_from_text(self, content: str, filename: str) -> str:
        file_response = self.client.files.create(
            content.encode(), 
            purpose="default", 
            filename=filename
        )
        self.uploaded_files.append(file_response.file_id)
        return file_response.file_id

    def analyze(self, query: str, analysis_type: str = "insights") -> str:
        instructions = {
            "summary": "You are an expert document summarizer. Provide clear, concise summaries.",
            "questions": "You are an expert analyst. Answer questions based on the provided documents with citations.",
            "insights": "You are a research analyst. Extract key insights, patterns, and important findings."
        }

        response = self.client.conversations.create(
            model="spec-3-turbo",
            instructions=instructions[analysis_type],
            input=query,
            files=[{"type": "file", "id": file_id} for file_id in self.uploaded_files],
            temperature=0.3,  # Lower temperature for more factual responses
        )

        return response.output

    def compare_documents(self, query: str) -> str:
        if len(self.uploaded_files) < 2:
            raise ValueError("Need at least 2 documents to compare")

        return self.analyze(
            f"Compare and contrast the documents regarding: {query}",
            "insights"
        )

    def get_uploaded_file_ids(self):
        return self.uploaded_files.copy()

# Usage
analyzer = DocumentAnalyzer()

# Add multiple documents
analyzer.add_document("./reports/quarterly-report.pdf")
analyzer.add_document("./reports/annual-summary.docx")
analyzer.add_document_from_text("""
# Meeting Notes
Key decisions:
1. Increase R&D budget by 15%
2. Launch new product line in Q3
3. Expand team by 5 engineers
""", "meeting-notes.md")

# Analyze documents
summary = analyzer.analyze(
    "Provide a comprehensive summary of all documents",
    "summary"
)
print("Summary:", summary)

insights = analyzer.analyze(
    "What are the key business decisions and their potential impact?",
    "insights"
)
print("Insights:", insights)

# Compare documents
comparison = analyzer.compare_documents(
    "financial performance and future projections"
)
print("Comparison:", comparison)
```

### Multi-Model Comparison

```python
from svector import SVECTOR
import time

class ModelComparison:
    def __init__(self):
        self.client = SVECTOR()

    def compare_models(self, prompt: str):
        models = ["spec-3-turbo", "spec-3", "theta-35", "theta-35-mini"]
        
        print(f"Comparing models for prompt: \"{prompt}\"\n")

        results = []
        for model in models:
            try:
                start_time = time.time()
                
                response = self.client.conversations.create(
                    model=model,
                    instructions="You are a helpful assistant. Be concise but informative.",
                    input=prompt,
                    max_tokens=150,
                )
                
                duration = time.time() - start_time
                
                results.append({
                    "model": model,
                    "response": response.output,
                    "duration": duration,
                    "usage": response.usage,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "model": model,
                    "error": str(e),
                    "success": False
                })

        # Display results
        for result in results:
            if result["success"]:
                print(f"Model: {result['model']}")
                print(f"Duration: {result['duration']:.2f}s")
                print(f"Tokens: {result['usage'].get('total_tokens', 'N/A')}")
                print(f"Response: {result['response'][:200]}...")
                print("─" * 80)
            else:
                print(f"{result['model']} failed: {result['error']}")

# Usage
comparison = ModelComparison()
comparison.compare_models("Explain the concept of artificial general intelligence")
```

## Best Practices

### 1. Use Conversations API for Simplicity
```python
# Recommended: Clean and simple
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful assistant.",
    input=user_message,
)

# More complex: Manual role management
response = client.chat.create(
    model="spec-3-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_message}
    ],
)
```

### 2. Handle Errors Gracefully
```python
import time

def chat_with_retry(client, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.conversations.create(
                model="spec-3-turbo",
                instructions="You are helpful.",
                input=prompt
            )
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

### 3. Use Appropriate Models
```python
# For quick responses
model = "spec-3-turbo"

# For complex reasoning
model = "theta-35"

# For simple tasks
model = "theta-35-mini"
```

### 4. Optimize File Usage
```python
# Upload once, use multiple times
with open("document.pdf", "rb") as f:
    file_response = client.files.create(f, purpose="default")
    file_id = file_response.file_id

# Use in multiple conversations
for question in questions:
    response = client.conversations.create(
        model="spec-3-turbo",
        instructions="You are a document analyst.",
        input=question,
        files=[{"type": "file", "id": file_id}],
    )
```

### 5. Environment Variables
```python
import os
from svector import SVECTOR

# Use environment variables
client = SVECTOR(api_key=os.environ.get("SVECTOR_API_KEY"))

# Don't hardcode API keys
client = SVECTOR(api_key="sk-hardcoded-key-here")  # Never do this!
```

### 6. Use Context Managers for Async
```python
# Recommended: Use context manager
async with AsyncSVECTOR() as client:
    response = await client.conversations.create(...)

# Manual cleanup required
client = AsyncSVECTOR()
try:
    response = await client.conversations.create(...)
finally:
    await client.close()
```

## Testing

Run tests with pytest:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest

# Run with coverage
pytest --cov=svector
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -e ".[dev]"`
4. Make your changes
5. Add tests and documentation
6. Run tests and linting
7. Submit a pull request

## License

Apache License - see [LICENSE](LICENSE) file for details.

## Links & Support

- **Website**: [https://www.svector.co.in](https://www.svector.co.in)
- **Documentation**: [https://platform.svector.co.in](https://platform.svector.co.in)
- **Issues**: [GitHub Issues](https://github.com/SVECTOR-CORPORATION/svector-python/issues)
- **Support**: [support@svector.co.in](mailto:support@svector.co.in)
- **PyPI Package**: [svector-sdk](https://pypi.org/project/svector-sdk/)

---

**Built with ❤️ by SVECTOR Corporation** - *Pushing the boundaries of AI, Mathematics, and Computational research*
