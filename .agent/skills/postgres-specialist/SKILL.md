---
name: db-postgresql 
description: PostgreSQL expert. Focuses on relational modeling, advanced indexing (B-Tree, GIN), JSONB optimization, and concurrent transaction management.
---

# PostgreSQL Development Standards

Best practices for robust and performant PostgreSQL applications.

## Schema & Data Types

### JSONB usage
Use `JSONB` (Binary JSON) over `JSON` for indexing support.

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexing a specific key in JSONB
CREATE INDEX idx_events_payload_type ON events ((payload->>'type'));
-- GIN Index for arbitrary search
CREATE INDEX idx_events_payload ON events USING GIN (payload);
```

### Date and Time

Always use `TIMESTAMPTZ` (timestamp with time zone) to avoid timezone confusion.

## Indexing Strategy

### Partial Indexes

Index only what you need to save space and write cost.
```sql
-- Only index active users
CREATE INDEX idx_users_email_active ON users (email) WHERE status = 'active';
```

### Concurrent Index Creation

In production, always use `CONCURRENTLY` to avoid locking the table.
```sql
CREATE INDEX CONCURRENTLY idx_users_name ON users (name);
```

## Performance & maintenance

### Connection Pooling

PostgreSQL has a high per-connection overhead. Always use a pooler (e.g., **PgBouncer** or in-app pooling via SQLAlchemy).
```python
# SQLAlchemy Async Engine with pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10
)
```

### Vacuuming

Ensure `autovacuum` is enabled (default). For heavy update tables, tune `autovacuum_vacuum_scale_factor`.