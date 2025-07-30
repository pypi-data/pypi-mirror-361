# Distributed PostgreSQL Lock

[![PyPI version](https://img.shields.io/pypi/v/distributed-pg-lock)](https://pypi.org/project/distributed-pg-lock/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust distributed locking system using PostgreSQL with automatic heartbeating, timeout management and automatic stale lock recovery for coordinated resource access.

## Features

- **Distributed Locking**: Coordinate resources across multiple processes/machines
- **Heartbeating**: Automatic keep-alive for long-running operations
- **Timeout Handling**: Automatic lock expiration
- **PostgreSQL Backed**: Leverages PostgreSQL's transactional integrity
- **Context Managers**: Pythonic `with` statement support
- **Graceful Shutdown**: Automatic lock release on process termination

## Installation

```bash
pip install distributed-pg-lock
```

## Basic Usage

```python
from distributed_pg_lock import DistributedLockManager, db

# Configure database
db.configure(url="postgresql://user:pass@localhost/mydb")
db.create_tables()

# Create lock manager
lock_manager = DistributedLockManager()

# Get a lock
lock = lock_manager.get_lock("critical_resource")

with lock:
    if lock.is_acquired:
        # Perform critical operations
        print("Working with protected resource")
    else:
        print("Could not acquire lock")
```

## Advanced Usage

```python
# Concurrent processing example
from concurrent.futures import ThreadPoolExecutor
from distributed_pg_lock import DistributedLockManager

lock_manager = DistributedLockManager()

def process_order(order_id):
    lock = lock_manager.get_lock(f"order_{order_id}")
    with lock:
        if lock.is_acquired:
            # Process order exclusively
            print(f"Processing order {order_id}")

# Process 100 orders concurrently
with ThreadPoolExecutor(max_workers=10) as executor:
    for order_id in range(1, 101):
        executor.submit(process_order, order_id)
```

## Documentation

### Database Configuration
```python
db.configure(
    url="postgresql://user:pass@localhost/dbname",
    pool_size=10,
    max_overflow=20,
    echo=False
)
```

### Lock Manager Options
```python
lock_manager = DistributedLockManager(
    lock_timeout_minutes=1,  # Lock expiration time
    owner_id="app-server-1"  # Custom owner identifier
)
```

### Force Release Locks (Admin)
```python
lock_manager.force_release_lock("stale_resource")
```

## Testing
```bash
pip install -e .[test]
pytest tests/
```

## Performance
See `examples/load_test_performance.py` for a load testing script that simulates:
- 200 concurrent pods
- Multiple resources
- High contention scenarios