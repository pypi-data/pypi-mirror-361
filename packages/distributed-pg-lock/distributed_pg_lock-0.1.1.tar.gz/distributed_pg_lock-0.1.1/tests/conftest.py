import pytest

from distributed_pg_lock import DistributedLockManager, db

@pytest.fixture(scope="module")
def lock_manager():
    """Fixture providing a lock manager instance"""
    db.create_tables()
    yield DistributedLockManager(lock_timeout_minutes=0.1)
    db.drop_tables()