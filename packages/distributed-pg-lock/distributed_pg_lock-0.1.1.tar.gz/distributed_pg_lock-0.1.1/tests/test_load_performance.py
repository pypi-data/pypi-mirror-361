"""
Distributed Lock Load Tests
--------------------------
Performance and stress testing for distributed lock system.

Run with:

     PYTHONPATH=src pytest tests/test_load_performance.py -v --log-cli-level=INFO
"""

import threading
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from collections import defaultdict
import pytest

from distributed_pg_lock import DistributedLockManager, db

logger = logging.getLogger(__name__)

class TestLoadScenarios:
    """Load and performance test cases for distributed locks."""

    # Test Configuration
    NUM_PODS = 200
    RESOURCES = ["resource_A", "resource_B"]
    LOCK_TIMEOUT_MINUTES = 1

    @pytest.fixture(autouse=True)
    def setup(self):
        """Test setup and teardown."""
        db.create_tables()
        self.stats = {
            'successful_acquires': 0,
            'failed_acquires': 0,
            'concurrent_access': defaultdict(int),
            'concurrency_history': defaultdict(list),
            'timings': [],
            'lock': threading.Lock()
        }
        yield
        db.drop_tables()

    class PodSimulator:
        """Simulates individual pod behavior."""
        
        def __init__(self, pod_id, lock_manager, stats):
            self.pod_id = pod_id
            self.lock_manager = lock_manager
            self.resource = random.choice(TestLoadScenarios.RESOURCES)
            self.lock = lock_manager.get_lock(self.resource)
            self.stats = stats

        def run(self):
            """Execute pod simulation."""
            start_time = time.time()
            attempt_time = datetime.now()

            try:
                with self.lock:
                    if self.lock.is_acquired:
                        with self.stats['lock']:
                            self._record_acquire()
                        
                        work_duration = self._get_work_duration()
                        time.sleep(work_duration)

                        with self.stats['lock']:
                            self._record_release()
                    else:
                        with self.stats['lock']:
                            self.stats['failed_acquires'] += 1
            except Exception as e:
                logger.error(f"Pod {self.pod_id} failed: {str(e)}")
            finally:
                return time.time() - start_time

        def _record_acquire(self):
            """Record lock acquisition metrics."""
            acquire_time = datetime.now()
            self.stats['successful_acquires'] += 1
            self.stats['concurrent_access'][self.resource] += 1
            self.stats['concurrency_history'][self.resource].append(
                self.stats['concurrent_access'][self.resource]
            )
            self.stats['timings'].append({
                'pod_id': self.pod_id,
                'resource': self.resource,
                'acquire_time': acquire_time,
                'release_time': None,
                'work_duration': None
            })

        def _record_release(self):
            """Record lock release metrics."""
            release_time = datetime.now()
            self.stats['concurrent_access'][self.resource] -= 1
            self.stats['concurrency_history'][self.resource].append(
                self.stats['concurrent_access'][self.resource]
            )
            # Update the last timing record
            if self.stats['timings']:
                last_entry = self.stats['timings'][-1]
                if last_entry['pod_id'] == self.pod_id:
                    last_entry['release_time'] = release_time
                    last_entry['work_duration'] = (
                        release_time - last_entry['acquire_time']
                    ).total_seconds()

        def _get_work_duration(self):
            """Determine work duration for this pod."""
            if self.pod_id == 0:  # Special long-running pod
                return (TestLoadScenarios.LOCK_TIMEOUT_MINUTES * 60) + 10
            return random.uniform(0.05, 0.15)

    def test_high_concurrency(self):
        """Test system under high concurrent load."""
        lock_manager = DistributedLockManager(
            lock_timeout_minutes=self.LOCK_TIMEOUT_MINUTES,
            owner_id="load_test"
        )

        logger.info(
            f"Starting load test with {self.NUM_PODS} pods "
            f"and {len(self.RESOURCES)} resources"
        )
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.NUM_PODS) as executor:
            futures = [
                executor.submit(self.PodSimulator(i, lock_manager, self.stats).run)
                for i in range(self.NUM_PODS)
            ]
            for future in as_completed(futures):
                duration = future.result()
                logger.debug(f"Pod completed in {duration:.2f}s")

        test_duration = time.time() - start_time
        self._analyze_results(test_duration)
        self._validate_exclusive_access()

    def _analyze_results(self, test_duration):
        """Analyze and log test results."""
        throughput = self.stats['successful_acquires'] / test_duration
        contention_rate = self.stats['failed_acquires'] / self.NUM_PODS

        max_concurrent = {
            res: max(self.stats['concurrency_history'][res], default=0)
            for res in self.RESOURCES
        }

        logger.info("\n=== LOAD TEST RESULTS ===")
        logger.info(f"Total pods: {self.NUM_PODS}")
        logger.info(f"Test duration: {test_duration:.2f} seconds")
        logger.info(f"Successful acquires: {self.stats['successful_acquires']}")
        logger.info(f"Failed acquires: {self.stats['failed_acquires']}")
        logger.info(f"Throughput: {throughput:.2f} locks/sec")
        logger.info(f"Contention rate: {contention_rate:.1%}")
        for res in self.RESOURCES:
            logger.info(f"Max concurrent for {res}: {max_concurrent[res]}")

    def _validate_exclusive_access(self):
        """Verify no overlapping access to resources."""
        violations = 0

        for resource in self.RESOURCES:
            resource_entries = [
                e for e in self.stats['timings']
                if e['resource'] == resource and e['release_time']
            ]
            resource_entries.sort(key=lambda x: x['acquire_time'])

            for i in range(1, len(resource_entries)):
                prev = resource_entries[i - 1]
                curr = resource_entries[i]

                if prev['release_time'] > curr['acquire_time']:
                    violations += 1
                    logger.warning(
                        f"Violation in {resource}: "
                        f"Pod {prev['pod_id']} released at {prev['release_time']}, "
                        f"Pod {curr['pod_id']} acquired at {curr['acquire_time']}"
                    )

        assert violations == 0, f"Found {violations} lock violations"