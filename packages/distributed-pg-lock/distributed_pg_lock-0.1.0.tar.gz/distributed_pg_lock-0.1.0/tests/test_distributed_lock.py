"""
Distributed Lock Tests
---------------------
Comprehensive test suite for distributed lock functionality.
Run with:

     PYTHONPATH=src pytest tests/test_distributed_lock.py -v --log-cli-level=INFO
"""

import threading
import time
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import pytest
from sqlalchemy import text

from distributed_pg_lock import DistributedLockManager, db, models

# Configure logging
logger = logging.getLogger(__name__)

class TestDistributedLock:
    """Main test class for distributed lock functionality."""

    @staticmethod
    def _worker(pod_id, lock_manager, resource, stats, work_duration=0.1):
        """Test worker simulating concurrent lock access."""
        try:
            lock = lock_manager.get_lock(resource)
            with lock:
                if lock.is_acquired:
                    enter_time = datetime.now()
                    time.sleep(work_duration)
                    exit_time = datetime.now()
                    
                    with stats['lock']:
                        stats['success'] += 1
                        stats['timings'].append({
                            'pod_id': pod_id,
                            'resource': resource,
                            'enter': enter_time,
                            'exit': exit_time
                        })
                else:
                    with stats['lock']:
                        stats['failures'] += 1
        except Exception as e:
            logger.error(f"Pod {pod_id} failed: {str(e)}")

    def test_basic_lock_acquire_release(self, lock_manager):
        """Test basic lock acquisition and release cycle."""
        resource = "test_resource"
        lock = lock_manager.get_lock(resource)
        
        # Test explicit acquire/release
        assert lock.acquire()
        assert lock.is_acquired
        lock.release()
        assert not lock.is_acquired
        
        # Test context manager
        with lock:
            assert lock.is_acquired
        assert not lock.is_acquired

    def test_concurrent_access(self, lock_manager):
        """Verify exclusive access under high concurrency."""
        resource = "concurrent_resource"
        stats = {
            'success': 0,
            'failures': 0,
            'timings': [],
            'lock': threading.Lock()
        }
        
        # Run 50 pods competing for the same resource
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(
                    self._worker, i, lock_manager, resource, stats, random.uniform(0.05, 0.1)
                ) for i in range(50)
            ]
            for future in as_completed(futures):
                future.result()
        
        # Verify no overlapping access
        timings = sorted(stats['timings'], key=lambda x: x['enter'])
        for i in range(1, len(timings)):
            assert timings[i-1]['exit'] <= timings[i]['enter'], \
                f"Concurrent access detected between {timings[i-1]['pod_id']} and {timings[i]['pod_id']}"

    def test_stale_lock_recovery(self, lock_manager):
        """Test automatic recovery of stale locks."""
        resource = "stale_resource"
        
        # Manually Create stale lock
        with db.session() as session:
            stale_time = datetime.utcnow() - timedelta(minutes=1)
            session.execute(text("""
                INSERT INTO distributed_lock 
                (resource_name, lock_owner, last_heartbeat)
                VALUES (:resource, 'stale-owner', :stale_time)
                ON CONFLICT (resource_name) DO UPDATE
                SET lock_owner = 'stale-owner',
                    last_heartbeat = :stale_time
            """), {
                'resource': resource,
                'stale_time': stale_time
            })
            session.commit()
        
        # Verify acquisition works
        lock = lock_manager.get_lock(resource)
        assert lock.acquire()
        lock.release()

    def test_heartbeat_maintenance(self, lock_manager):
        """Verify heartbeat keeps lock alive."""
        resource = "heartbeat_test"
        lock = lock_manager.get_lock(resource)
        
        assert lock.acquire()
        time.sleep(10)  # Longer than heartbeat interval
        
        # Verify lock is still held
        with db.session() as session:
            lock_record = session.query(models.DistributedLock).filter_by(
                resource_name=resource
            ).first()
            assert lock_record.lock_owner == lock_manager.owner_id
        
        lock.release()

    def test_lock_timeout(self, lock_manager):
        """Verify lock expiration after timeout."""
        resource = "timeout_test"
        
        # Acquire lock with first manager
        lock1 = lock_manager.get_lock(resource)
        assert lock1.acquire()
        
        # Get initial heartbeat time
        with db.session() as session:
            lock_record = session.query(models.DistributedLock).filter_by(
                resource_name=resource
            ).first()
            initial_heartbeat = lock_record.last_heartbeat
        
        # Stop heartbeat to simulate crash
        lock_manager.stop_heartbeat(resource)
        
        # Wait for lock to expire
        time.sleep(lock_manager.lock_timeout * 60 + 5)
        
        # Verify new owner can acquire
        new_manager = DistributedLockManager(lock_timeout_minutes=0.1)
        new_lock = new_manager.get_lock(resource)
        assert new_lock.acquire()
        # Verify the lock was indeed expired
        with db.session() as session:
            lock_record = session.query(models.DistributedLock).filter_by(
                resource_name=resource
            ).first()
            current_time = datetime.utcnow()
            time_since_heartbeat = (current_time - initial_heartbeat).total_seconds()
            assert time_since_heartbeat > lock_manager.lock_timeout * 60, (
                f"Lock should be expired (last heartbeat: {initial_heartbeat}, "
                f"current time: {current_time}, timeout: {lock_manager.lock_timeout} minutes)"
            )
        
        new_lock.release()

    def test_graceful_shutdown(self, lock_manager):
        """Test proper lock release on shutdown."""
        resource = "shutdown_test"
        lock = lock_manager.get_lock(resource)
        
        assert lock.acquire()
        
        # Test will expect the SystemExit
        with pytest.raises(SystemExit):
            lock_manager._graceful_shutdown(None, None)
        
        # Verify lock released
        with db.session() as session:
            lock_record = session.query(models.DistributedLock).filter_by(
                resource_name=resource
            ).first()
            assert lock_record.lock_owner is None

    def test_force_release(self, lock_manager):
        """Test manual force release functionality."""
        resource = "force_release_test"
        lock = lock_manager.get_lock(resource)
        
        assert lock.acquire()
        assert lock_manager.force_release_lock(resource)
        
        # Verify release
        assert not lock.is_acquired
        with db.session() as session:
            lock_record = session.query(models.DistributedLock).filter_by(
                resource_name=resource
            ).first()
            assert lock_record.lock_owner is None

    def test_high_contention(self, lock_manager):
        """High-load test with multiple resources."""
        resources = ["high_contention_1", "high_contention_2"]
        stats = {
            'success': 0,
            'failures': 0,
            'timings': [],
            'lock': threading.Lock()
        }
        
        # Run 200 pods across 2 resources
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = [
                executor.submit(
                    self._worker, i, lock_manager, random.choice(resources), stats
                ) for i in range(200)
            ]
            for future in as_completed(futures):
                future.result()
        
        # Verify exclusivity per resource
        for resource in resources:
            entries = sorted(
                [e for e in stats['timings'] if e['resource'] == resource],
                key=lambda x: x['enter']
            )
            for i in range(1, len(entries)):
                assert entries[i-1]['exit'] <= entries[i]['enter'], \
                    f"Concurrent access in {resource}"