---
name: db-spanner 
description: Google Cloud Spanner expert. Focuses on schema design for horizontal scaling, interleaving, hotspot prevention, and high-performance SQL execution.
---

# Spanner Development Standards

Best practices for designing and querying Google Cloud Spanner databases.

## Schema Design Patterns

### Primary Key Selection (Hotspot Prevention)

⚠️ CRITICAL RULE: NEVER use sequential IDs (like `AUTO_INCREMENT` or timestamps) as the first part of a Primary Key. This causes hotspots.

✅ Recommended:

* UUIDv4 (stored as STRING(36))
* Bit-reversed sequence (if integer ID is strictly required)
* Hash of the business key

```sql
-- Good
CREATE TABLE Users (
  UserId STRING(36) NOT NULL,
  Email STRING(256),
  Name STRING(MAX)
) PRIMARY KEY (UserId);
```

### Table Interleaving

Use interleaving to physically co-locate child rows with parent rows for faster joins.
```sql
CREATE TABLE Singers (
  SingerId INT64 NOT NULL,
  FirstName STRING(1024),
  LastName STRING(1024)
) PRIMARY KEY (SingerId);

CREATE TABLE Albums (
  SingerId INT64 NOT NULL,
  AlbumId INT64 NOT NULL,
  AlbumTitle STRING(MAX)
) PRIMARY KEY (SingerId, AlbumId),
  INTERLEAVE IN PARENT Singers ON DELETE CASCADE;
```

## Query Optimization

### Use Secondary Indexes

Avoid full table scans by creating secondary indexes for frequently filtered columns.

```sql
-- Storing 'Email' in the index to avoid a join back to the base table (Index-Only Scan)
CREATE INDEX UsersByEmail ON Users(Email) STORING (Name);
```

### Read-Only Transactions

For reporting or batch processing, always specify `read_only=True` to avoid locking implementation.
```python
# Python Client Library Example
with database.snapshot() as snapshot:
    results = snapshot.execute_sql("SELECT * FROM Albums")
```

## SQL Dialect

* Prefer **GoogleSQL** (Standard SQL) unless the project explicitly uses the PostgreSQL dialect interface.
* Use `UNNEST` for array operations.
```sql
SELECT * FROM Users WHERE "Admin" IN UNNEST(Roles);
```
