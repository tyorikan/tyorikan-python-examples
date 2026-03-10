---
name: db-bigquery 
description: BigQuery data warehouse expert. Focuses on cost optimization, partitioning/clustering, denormalization (STRUCT/ARRAY), and analytical SQL.
---

# BigQuery Development Standards

Best practices for cost-effective and high-performance data warehousing.

## Cost Optimization (The Golden Rules)

1. NO `SELECT *`: BigQuery is a columnar store. Selecting all columns scans all data and costs maximum money. Select only necessary columns.

* ❌ `SELECT * FROM events`

* ✅ `SELECT event_id, event_name FROM events`

2. Filter by Partition: Always filter by the partitioning column (usually date/time) in the `WHERE` clause.

## Schema Design

### Partitioning & Clustering

Mandatory for tables > 1GB.

* Partitioning: Segments data by time (Day/Month) or Integer range. Reduces scan cost.

* Clustering: Sorts data within partitions. Speeds up filters and aggregations.

```sql
CREATE TABLE my_dataset.logs (
    transaction_id STRING,
    transaction_date DATE,
    category STRING,
    amount INT64
)
PARTITION BY transaction_date
CLUSTER BY category;
```

### Denormalization (Nested & Repeated Fields)

Prefer `STRUCT` and `ARRAY` over multiple joined tables for better performance.
```sql
-- Nested schema example
CREATE TABLE my_dataset.orders (
    order_id INT64,
    customer STRUCT<name STRING, email STRING>,
    items ARRAY<STRUCT<item_name STRING, quantity INT64>>
);
```


## SQL Best Practices

### Efficient Joins

* Place the **largest table first** (on the left side of `JOIN`) for optimal distribution (though Query Optimizer handles this well now, it's good practice).

* Avoid joining on calculated fields.

### Approximate Aggregation

For massive datasets, use approximate functions for distinct counts to save resources.

* `APPROX_COUNT_DISTINCT(user_id)` instead of `COUNT(DISTINCT user_id)`

### Materialized Views

Use Materialized Views for common aggregations to enable **Smart Tuning** and automatic refreshes.
```sql
CREATE MATERIALIZED VIEW my_dataset.daily_sales
AS SELECT
  transaction_date,
  SUM(amount) as total_sales
FROM my_dataset.logs
GROUP BY transaction_date;
```
