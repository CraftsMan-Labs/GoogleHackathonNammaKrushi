# Python Clean Code Rules for AI Systems

## File Organization & Structure
- **models/**: All Pydantic models in separate files (`user.py`, `product.py`)
- **config/**: Configuration variables and constants (`settings.py`, `constants.py`)
- **api/**: FastAPI routers grouped by domain (`users.py`, `products.py`)
- **services/**: Business logic separated from API handlers
- **schemas/**: Request/response schemas distinct from database models

## Type Safety & Compliance
- Use `from __future__ import annotations` for forward references
- All function parameters and returns must have type hints
- Use `typing.Union` or `|` for Python 3.10+ union types
- Leverage `typing.Generic`, `TypeVar` for reusable components
- Configure pyright strict mode: `"strict": ["**/*.py"]`

## Pydantic Best Practices
```python
class BaseModel(PydanticBaseModel):
    class Config:
        validate_assignment = True
        use_enum_values = True
        arbitrary_types_allowed = False
```
- Use `Field()` for validation and documentation
- Implement custom validators with `@validator` or `@field_validator`
- Separate request/response models from database models

## FastAPI Architecture
- Use dependency injection for database sessions, auth, configs
- Implement proper exception handlers with custom exceptions
- Structure endpoints: `@router.get("/users/{user_id}", response_model=UserResponse)`
- Use `BackgroundTasks` for non-blocking operations
- Implement proper middleware for CORS, logging, authentication

## Streaming Data Implementation
```python
from fastapi.responses import StreamingResponse
import asyncio

async def stream_data():
    async for data in data_source():
        yield f"data: {data.json()}\n\n"

@app.get("/stream")
async def get_stream():
    return StreamingResponse(stream_data(), media_type="text/plain")
```
- Use `async`/`await` for all I/O operations
- Implement Server-Sent Events (SSE) for real-time updates
- Use WebSockets for bidirectional communication
- Handle connection cleanup with `try`/`finally` blocks

## Code Quality Rules
- Maximum line length: 88 characters (Black standard)
- Use `ruff` with aggressive settings: `--select=ALL --ignore=D,ANN`
- Implement proper error handling with specific exception types
- Use dataclasses or Pydantic for data containers, avoid dictionaries
- Follow single responsibility principle for functions and classes

## Performance & Async Patterns
- Use `asyncio.gather()` for concurrent operations
- Implement connection pooling for databases
- Use `functools.lru_cache` for expensive computations
- Leverage `asyncio.Queue` for producer-consumer patterns

## Documentation & Testing
- Use docstrings with Google/NumPy format
- Type-annotate test functions and fixtures
- Use `pytest-asyncio` for async test cases
- Implement health checks and monitoring endpoints

## Import Organization
```python
# Standard library
import asyncio
from typing import AsyncGenerator

# Third-party
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

# Local imports
from .models.user import User
from .config.settings import get_settings
```

## Error Handling
- Create custom exception classes inheriting from `HTTPException`
- Use proper HTTP status codes
- Implement global exception handlers
- Log errors with structured logging (JSON format)

These rules ensure maintainable, scalable, and type-safe Python applications that leverage modern async patterns and streaming capabilities.