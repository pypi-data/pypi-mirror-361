"""
Utility functions for generating and manipulating traceability IDs.

This module provides functions for generating correlation IDs, trace IDs, span IDs,
and for adding hops to correlation IDs as they flow through different services.

Constants:
    HTTP_HEADER_*: Standard HTTP header names for traceability IDs
    ASYNC_CONTEXT_*: Keys for storing traceability data in async contexts

Example:
    Basic ID generation:
        from finalsa.traceability.functions import (
            default_correlation_id,
            default_trace_id,
            add_hop_to_correlation
        )

        # Generate new correlation ID
        corr_id = default_correlation_id("user-service")
        print(corr_id)  # "user-service-A1B2C"

        # Add hop to existing correlation ID
        extended = add_hop_to_correlation(corr_id)
        print(extended)  # "user-service-A1B2C-X9Y8Z"

        # Generate trace ID
        trace = default_trace_id()
        print(trace)  # "550e8400-e29b-41d4-a716-446655440000"
"""

import random
import string
from typing import Optional
from uuid import uuid4

# HTTP Header constants for traceability
HTTP_HEADER_CORRELATION_ID = "X-Correlation-ID"
"""Standard HTTP header name for correlation ID.

Use this constant when setting/getting correlation IDs from HTTP headers
to ensure consistency across your application.
"""

HTTP_HEADER_TRACE_ID = "X-Trace-ID"
"""Standard HTTP header name for trace ID.

Use this constant when setting/getting trace IDs from HTTP headers
to ensure consistency across your application.
"""

HTTP_HEADER_SPAN_ID = "X-Span-ID"
"""Standard HTTP header name for span ID.

Use this constant when setting/getting span IDs from HTTP headers
to ensure consistency across your application.
"""

HTTP_AUTHORIZATION_HEADER = "Authorization"
"""Standard HTTP authorization header name.

Included for convenience when working with authenticated requests
that also need traceability.
"""

# Async context variable keys
ASYNC_CONTEXT_CORRELATION_ID = "correlation_id"
"""Key name for correlation ID in async context storage."""

ASYNC_CONTEXT_TRACE_ID = "trace_id"
"""Key name for trace ID in async context storage."""

ASYNC_CONTEXT_SPAN_ID = "span_id"
"""Key name for span ID in async context storage."""

ASYNC_CONTEXT_TOPIC = "topic"
"""Key name for topic information in async context storage.

Useful for message queue or pub/sub systems where you need to track
which topic/channel a message came from.
"""

ASYNC_CONTEXT_SUBTOPIC = "subtopic"
"""Key name for subtopic information in async context storage.

Useful for more granular topic tracking in message systems.
"""

ASYNC_CONTEXT_AUTHORIZATION = "auth"
"""Key name for authorization information in async context storage.

Use this for storing auth tokens or user context that should flow
with traceability information.
"""


def id_generator(size=5, chars=string.ascii_uppercase + string.digits):
    """Generate a random alphanumeric ID string.

    Creates a random string using the specified character set. By default,
    uses uppercase letters and digits.

    Args:
        size: Length of the generated ID. Defaults to 5.
        chars: Character set to use for generation. Defaults to uppercase letters + digits.

    Returns:
        Random string of specified length.

    Raises:
        IndexError: If chars is empty.
        TypeError: If chars is not a string.

    Examples:
        >>> id_generator()
        'A1B2C'

        >>> id_generator(10)
        'X9Y8Z7W6V5'

        >>> id_generator(3, 'ABC')
        'BAC'

    Note:
        This function uses Python's random module, which is not cryptographically
        secure. For security-sensitive applications, consider using the secrets module.
    """
    return ''.join(random.choice(chars) for _ in range(size))


def default_correlation_id(
    service_name: Optional[str] = None
) -> str:
    """Generate a default correlation ID with service name prefix.

    Creates a correlation ID in the format: "{service_name}-{random_id}"

    Args:
        service_name: Name of the service generating the ID. If None, uses "DEFAULT".

    Returns:
        Correlation ID string in format "service_name-XXXXX".

    Examples:
        >>> default_correlation_id("user-service")
        'user-service-A1B2C'

        >>> default_correlation_id()
        'DEFAULT-X9Y8Z'

        >>> default_correlation_id("")
        '-M4N5P'

    Note:
        This function is typically used when starting a new request trace
        or when no correlation ID is provided by upstream services.
    """
    if service_name is None:
        service_name = "DEFAULT"
    return f"{service_name}-{id_generator()}"


def default_span_id() -> str:
    """Generate a default span ID using UUID4.

    Creates a new span ID using Python's uuid4() function, which generates
    a random UUID according to RFC 4122.

    Returns:
        UUID string in format "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".

    Examples:
        >>> default_span_id()
        '550e8400-e29b-41d4-a716-446655440000'

        >>> default_span_id()
        '6ba7b810-9dad-11d1-80b4-00c04fd430c8'

    Note:
        Each call generates a unique ID. Span IDs should be unique within
        a trace and are used to identify individual operations.
    """
    return str(uuid4())


def default_trace_id() -> str:
    """Generate a default trace ID using UUID4.

    Creates a new trace ID using Python's uuid4() function, which generates
    a random UUID according to RFC 4122.

    Returns:
        UUID string in format "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".

    Examples:
        >>> default_trace_id()
        '550e8400-e29b-41d4-a716-446655440000'

        >>> default_trace_id()
        '6ba7b810-9dad-11d1-80b4-00c04fd430c8'

    Note:
        Each call generates a unique ID. Trace IDs should be unique across
        your entire system and represent the top-level request or operation.
    """
    return str(uuid4())


def add_hop_to_correlation(
    correlation_id: str,
) -> str:
    """Add a hop to an existing correlation ID.

    Extends a correlation ID by appending a new random segment, creating
    a trail of hops as the request flows through different services.

    Args:
        correlation_id: The existing correlation ID to extend.

    Returns:
        Extended correlation ID in format "original_id-XXXXX".

    Raises:
        AttributeError: If correlation_id is empty or falsy.

    Examples:
        >>> add_hop_to_correlation("user-service-A1B2C")
        'user-service-A1B2C-X9Y8Z'

        >>> add_hop_to_correlation("request-123")
        'request-123-M4N5P'

        Chain multiple hops:
        >>> original = "service-A1B2C"
        >>> hop1 = add_hop_to_correlation(original)
        >>> hop2 = add_hop_to_correlation(hop1)
        >>> print(hop2)
        'service-A1B2C-X9Y8Z-Q7R8S'

    Note:
        This function is crucial for distributed tracing. Each service should
        add its own hop when processing a request, creating a traceable path
        through your service architecture.
    """
    if not correlation_id:
        raise AttributeError("Correlation ID cannot be empty")
    hop = id_generator()
    return f"{correlation_id}-{hop}"
