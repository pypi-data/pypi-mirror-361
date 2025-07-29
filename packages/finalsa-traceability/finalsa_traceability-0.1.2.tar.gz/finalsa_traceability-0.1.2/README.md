# Finalsa Traceability

A comprehensive Python library for managing distributed tracing and correlation IDs across microservices and distributed systems. Provides thread-safe context management using Python's `contextvars` for proper isolation between concurrent operations.

## Features

- **Thread-Safe Context Management**: Uses Python's `contextvars` for proper isolation
- **Automatic ID Generation**: Creates correlation IDs, trace IDs, and span IDs
- **Hop Tracking**: Automatically extends correlation IDs as requests flow through services
- **HTTP Integration**: Standard header constants for easy integration
- **Async Support**: Full support for async/await operations
- **Type Hints**: Complete type annotations for better development experience
- **100% Test Coverage**: Comprehensive test suite ensuring reliability

## Installation

```bash
# Using uv (recommended)
uv add finalsa-traceability

# Using pip
pip install finalsa-traceability

# For development with examples
uv sync --group examples --group test
```

## Quick Start

### Basic Usage

```python
from finalsa.traceability import set_context, get_context

# Set traceability context for your service
set_context(
    correlation_id="user-request-123",
    service_name="auth-service"
)

# Get current context
context = get_context()
print(context["correlation_id"])  # "user-request-123-XXXXX"
print(context["trace_id"])        # Auto-generated UUID
print(context["span_id"])         # Auto-generated UUID
```

### HTTP Service Integration

```python
from finalsa.traceability import (
    set_context_from_dict, 
    get_context,
    HTTP_HEADER_CORRELATION_ID,
    HTTP_HEADER_TRACE_ID,
    HTTP_HEADER_SPAN_ID
)

# Extract traceability from incoming HTTP request
def handle_request(request):
    headers = {
        'correlation_id': request.headers.get(HTTP_HEADER_CORRELATION_ID),
        'trace_id': request.headers.get(HTTP_HEADER_TRACE_ID),
        'span_id': request.headers.get(HTTP_HEADER_SPAN_ID)
    }
    
    # Set context for this service
    set_context_from_dict(headers, service_name="api-gateway")
    
    # Your business logic here
    result = process_request(request)
    
    # Add traceability to outgoing response
    context = get_context()
    response.headers[HTTP_HEADER_CORRELATION_ID] = context["correlation_id"]
    response.headers[HTTP_HEADER_TRACE_ID] = context["trace_id"]
    response.headers[HTTP_HEADER_SPAN_ID] = context["span_id"]
    
    return response
```

### Flask Integration

```python
from flask import Flask, request, g
from finalsa.traceability import set_context_from_dict, get_context

app = Flask(__name__)

@app.before_request
def before_request():
    # Extract traceability from request headers
    headers = {
        'correlation_id': request.headers.get('X-Correlation-ID'),
        'trace_id': request.headers.get('X-Trace-ID'), 
        'span_id': request.headers.get('X-Span-ID')
    }
    set_context_from_dict(headers, service_name="my-flask-app")

@app.after_request  
def after_request(response):
    # Add traceability to response headers
    context = get_context()
    response.headers['X-Correlation-ID'] = context["correlation_id"]
    response.headers['X-Trace-ID'] = context["trace_id"]
    response.headers['X-Span-ID'] = context["span_id"]
    return response

@app.route('/api/users')
def get_users():
    # Context is automatically available
    context = get_context()
    print(f"Processing request with correlation_id: {context['correlation_id']}")
    return {"users": []}
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request, Response
from finalsa.traceability import set_context_from_dict, get_context

app = FastAPI()

@app.middleware("http")
async def traceability_middleware(request: Request, call_next):
    # Extract traceability from request headers
    headers = {
        'correlation_id': request.headers.get('x-correlation-id'),
        'trace_id': request.headers.get('x-trace-id'),
        'span_id': request.headers.get('x-span-id')
    }
    set_context_from_dict(headers, service_name="my-fastapi-app")
    
    # Process request
    response = await call_next(request)
    
    # Add traceability to response headers
    context = get_context()
    response.headers['x-correlation-id'] = context["correlation_id"]
    response.headers['x-trace-id'] = context["trace_id"]
    response.headers['x-span-id'] = context["span_id"]
    
    return response

@app.get("/api/users")
async def get_users():
    context = get_context()
    print(f"Processing request with correlation_id: {context['correlation_id']}")
    return {"users": []}
```

### Message Queue Integration

```python
from finalsa.traceability import set_context_from_dict, get_context

# Publishing messages
def publish_message(message_data):
    context = get_context()
    
    # Add traceability to message properties
    message_properties = {
        'correlation_id': context["correlation_id"],
        'trace_id': context["trace_id"],
        'span_id': context["span_id"]
    }
    
    publish_to_queue(message_data, properties=message_properties)

# Consuming messages  
def handle_message(message):
    # Extract traceability from message properties
    headers = {
        'correlation_id': message.properties.get('correlation_id'),
        'trace_id': message.properties.get('trace_id'),
        'span_id': message.properties.get('span_id')
    }
    
    set_context_from_dict(
        headers, 
        service_name="order-processor",
        queue_name="orders",
        message_id=message.id
    )
    
    # Process message with traceability context
    process_order(message.data)
```

## API Reference

### Context Management

#### `set_context(correlation_id=None, trace_id=None, span_id=None, service_name=None, **kwargs)`

Set multiple traceability IDs and custom variables in one call.

**Parameters:**
- `correlation_id` (str, optional): Correlation ID to extend with hop
- `trace_id` (str, optional): Trace ID to set (generates UUID if None)
- `span_id` (str, optional): Span ID to set (generates UUID if None)  
- `service_name` (str, optional): Service name for correlation ID generation
- `**kwargs`: Additional custom variables to store

#### `set_context_from_dict(context, service_name=None, **kwargs)`

Set traceability context from a dictionary (e.g., HTTP headers).

**Parameters:**
- `context` (dict): Dictionary with 'correlation_id', 'trace_id', 'span_id' keys
- `service_name` (str, optional): Service name for new correlation ID generation
- `**kwargs`: Additional custom variables to store

#### `get_context() -> Dict`

Get the complete current traceability context.

**Returns:** Dictionary containing correlation_id, trace_id, span_id, and custom variables.

### Individual Setters/Getters

#### `set_correlation_id(value=None, service_name=None)`
#### `set_trace_id(value=None)`
#### `set_span_id(value=None)`
#### `get_correlation_id() -> Optional[str]`
#### `get_trace_id() -> Optional[str]`
#### `get_span_id() -> Optional[str]`

### ID Generation Functions

#### `default_correlation_id(service_name=None) -> str`

Generate correlation ID in format "service_name-XXXXX".

#### `default_trace_id() -> str`

Generate trace ID using UUID4.

#### `default_span_id() -> str`

Generate span ID using UUID4.

#### `add_hop_to_correlation(correlation_id) -> str`

Add a hop to existing correlation ID.

#### `id_generator(size=5, chars=string.ascii_uppercase + string.digits) -> str`

Generate random alphanumeric ID.

### Constants

#### HTTP Headers
- `HTTP_HEADER_CORRELATION_ID` = "X-Correlation-ID"
- `HTTP_HEADER_TRACE_ID` = "X-Trace-ID"
- `HTTP_HEADER_SPAN_ID` = "X-Span-ID"
- `HTTP_AUTHORIZATION_HEADER` = "Authorization"

#### Async Context Keys
- `ASYNC_CONTEXT_CORRELATION_ID` = "correlation_id"
- `ASYNC_CONTEXT_TRACE_ID` = "trace_id"
- `ASYNC_CONTEXT_SPAN_ID` = "span_id"
- `ASYNC_CONTEXT_TOPIC` = "topic"
- `ASYNC_CONTEXT_SUBTOPIC` = "subtopic"
- `ASYNC_CONTEXT_AUTHORIZATION` = "auth"

## Advanced Usage

### Custom Variables

```python
from finalsa.traceability import set_context, get_context

# Store custom variables with traceability context
set_context(
    correlation_id="request-123",
    service_name="user-service",
    user_id="user-456",
    operation="login",
    ip_address="192.168.1.1"
)

context = get_context()
print(context["user_id"])      # "user-456"
print(context["operation"])    # "login"
print(context["ip_address"])   # "192.168.1.1"
```

### Thread Safety

The library uses Python's `contextvars` which ensures proper isolation between threads and async tasks:

```python
import threading
from finalsa.traceability import set_context, get_context

def worker_thread(thread_id):
    # Each thread has its own context
    set_context(
        correlation_id=f"thread-{thread_id}",
        service_name="worker-service"
    )
    
    context = get_context()
    print(f"Thread {thread_id}: {context['correlation_id']}")

# Create multiple threads
threads = []
for i in range(5):
    thread = threading.Thread(target=worker_thread, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

### Async/Await Support

```python
import asyncio
from finalsa.traceability import set_context, get_context

async def async_task(task_id):
    # Each async task has its own context
    set_context(
        correlation_id=f"task-{task_id}",
        service_name="async-service"
    )
    
    await asyncio.sleep(0.1)  # Simulate async work
    
    context = get_context()
    print(f"Task {task_id}: {context['correlation_id']}")

async def main():
    # Run multiple async tasks
    tasks = [async_task(i) for i in range(5)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

## Best Practices

### 1. Service Naming
Use consistent service names across your application:

```python
SERVICE_NAME = "auth-service"
set_context(service_name=SERVICE_NAME)
```

### 2. HTTP Header Propagation
Always propagate traceability headers between services:

```python
import requests
from finalsa.traceability import get_context, HTTP_HEADER_CORRELATION_ID

def call_downstream_service():
    context = get_context()
    headers = {
        HTTP_HEADER_CORRELATION_ID: context["correlation_id"],
        "X-Trace-ID": context["trace_id"],
        "X-Span-ID": context["span_id"]
    }
    
    response = requests.get("http://downstream-service/api", headers=headers)
    return response
```

### 3. Error Handling
Include traceability in error logs:

```python
import logging
from finalsa.traceability import get_context

def handle_error(error):
    context = get_context()
    logging.error(
        f"Error occurred - "
        f"correlation_id: {context.get('correlation_id')}, "
        f"trace_id: {context.get('trace_id')}, "
        f"error: {error}"
    )
```

### 4. Database Operations
Include traceability in database logs:

```python
from finalsa.traceability import get_context

def execute_query(sql, params):
    context = get_context()
    
    # Log query with traceability
    logging.info(
        f"Executing query - "
        f"correlation_id: {context.get('correlation_id')}, "
        f"sql: {sql}"
    )
    
    # Execute query
    return database.execute(sql, params)
```

## Examples

The `examples/` directory contains comprehensive examples demonstrating different use cases:

### Basic Usage
- **`examples/basic_usage.py`** - Simple usage patterns and basic context operations

### Web Framework Integration
- **`examples/fastapi_integration.py`** - Complete FastAPI application with middleware, dependency injection, async patterns, and error handling

### Concurrency & Thread Safety
- **`examples/thread_safety_demo.py`** - Thread and async safety demonstrations

### Running Examples

Using uv (recommended):
```bash
# Install example dependencies
uv sync --group examples

# Basic usage example
uv run python examples/basic_usage.py

# FastAPI example 
uv run python examples/fastapi_integration.py
# Or use the convenience script
./run_fastapi_example.sh

# Thread safety demo
uv run python examples/thread_safety_demo.py
```

Using pip:
```bash
# Install example dependencies
pip install -r examples/requirements.txt

# Run examples
python examples/basic_usage.py
python examples/fastapi_integration.py
python examples/thread_safety_demo.py
```

See `examples/README.md` for detailed usage instructions and API patterns.

## Development

### Requirements
- Python 3.9+ (uses only standard library for core functionality)
- Optional dependencies for examples and testing (see `pyproject.toml`)

### Running Tests

```bash
# Install development dependencies
uv add --dev pytest coverage

# Run tests
uv run pytest

# Run tests with coverage
uv run coverage run -m pytest
uv run coverage report --show-missing
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### v0.1.1
- Initial release
- Basic traceability context management
- HTTP header constants
- Thread-safe operation using contextvars
- Comprehensive test suite with 100% coverage