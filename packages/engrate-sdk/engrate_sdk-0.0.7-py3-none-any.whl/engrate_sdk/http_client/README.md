# Engrate SDK HTTP Client

This module provides HTTP client utilities for the Engrate SDK. It is responsible for handling HTTP requests and responses, abstracting away the underlying implementation details.

## Features

- Simplified HTTP request methods (GET, POST, PUT, DELETE)
- Configurable headers and timeouts
- Error handling and response parsing
- Support for authentication

## Usage

```python
from engrate_sdk.http_client import HttpClient

client = HttpClient(base_url="https://api.example.com")
response = client.get("/endpoint", params={"key": "value"})
print(response.json())
```

## Configuration

You can configure the HTTP client with custom headers, authentication tokens, and timeouts:

```python
client = HttpClient(
  base_url="https://api.example.com",
  headers={"Authorization": "Bearer <token>"},
  timeout=10
)
```