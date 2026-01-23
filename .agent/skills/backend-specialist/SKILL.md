---
name: backend-specialist 
description: Python FastAPI expert patterns. Includes clean architecture structure, Pydantic v2 usage, SQLAlchemy async patterns, and pytest templates.
---

# Backend Development Patterns (FastAPI)

Standards for building robust, scalable Python web APIs.

## Project Structure
```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/  # Route handlers
│   │   └── api.py      # Router aggregation
│   └── deps.py         # Dependency Injection
├── core/
│   ├── config.py       # Pydantic Settings
│   └── security.py     # JWT & Password hashing
├── db/
│   ├── session.py      # Async Engine & Session
│   └── base.py         # ORM Base
├── models/             # SQLAlchemy Models
├── schemas/            # Pydantic Schemas
└── services/           # Business Logic
```


## Implementation Patterns

### Pydantic V2 Models

```python
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```


## Dependency Injection
```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models import User
from app.core import security

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    payload = security.decode_token(token)
    user = await db.get(User, payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
```


## Service Layer (Business Logic)
```python
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, schema: UserCreate) -> User:
        # Business logic: Check if exists
        existing = await self.get_by_email(schema.email)
        if existing:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_pw = security.get_password_hash(schema.password)
        
        # Create instance
        db_user = User(
            email=schema.email, 
            hashed_password=hashed_pw,
            full_name=schema.full_name
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
```

## Testing Patterns

### Pytest Fixtures
```python
# conftest.py
import pytest_asyncio
from httpx import AsyncClient
from app.main import app

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### Unit Test Example
```python
async def test_create_user(async_client, db_session):
    payload = {"email": "test@example.com", "password": "securepassword"}
    response = await async_client.post("/api/v1/users/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
```