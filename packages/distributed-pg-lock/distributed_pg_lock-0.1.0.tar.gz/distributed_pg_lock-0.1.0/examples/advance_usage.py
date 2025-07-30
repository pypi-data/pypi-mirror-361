"""
Advanced Lock Usage Patterns
---------------------------
Demonstrates concurrent access, error handling, and health monitoring.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dist_lock import DistributedLockManager, LockAcquisitionError

logger = logging.getLogger(__name__)

def process_order(order_id):
    """Order processing with lock contention handling"""
    lock = lock_manager.get_lock(f"order_{order_id}")
    try:
        with lock:
            if lock.is_acquired:
                logger.info(f"Processing order {order_id}")
                # Simulate work
                time.sleep(0.1)
            else:
                logger.warning(f"Order {order_id} already processing")
    except LockAcquisitionError as e:
        logger.error(f"Critical error: {str(e)}")
        # Add your alerting logic here

def run_concurrent_example():
    """Demonstrate thread-safe operation"""
    configure_logging()
    
    global lock_manager
    lock_manager = DistributedLockManager()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_order, range(1, 101))
    
    # Show system status
    status = lock_manager.health_check()
    logger.info(f"Active locks: {len(status['active_locks'])}")
    logger.info(f"Heartbeat status: {status['heartbeats']}")

def configure_logging():
    """Centralized logging setup"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

if __name__ == "__main__":
    run_concurrent_example()