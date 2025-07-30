# zbq

A lightweight, wrapper around Google Cloud BigQuery with Polars integration. Simplifies querying and data ingestion with a unified interface, supporting read, write, insert, and delete operations on BigQuery tables.

## Features
* Transparent BigQuery client initialization with automatic project and credentials detection
* Use Polars DataFrames seamlessly for input/output
* Unified .bq() method for CRUD operations with SQL and DataFrame inputs
* Supports table creation, overwrite warnings, and write mode control
* Context manager support for client lifecycle management

## Examples:
```SQL
from zbq import zclient

query = "select * from project.dataset.table"

# Read, Update, Insert, Delete
results = zclient(action="read", query)

# Write data
zclient.bq(
    action="write",
    df=df,
    dataset="dataset",
    table="table",
    write_type="WRITE_TRUNCATE",
    warning=True
)
```
