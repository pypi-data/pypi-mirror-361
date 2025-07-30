"""
Distributed locking system using database-backed locks with heartbeating.
"""

import os
import threading
import uuid
import logging
import socket
import sys
from signal import signal, SIGTERM, SIGINT
from typing import Set, Optional, Dict
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from tenacity import retry, stop_after_attempt, wait_exponential

from . import models
from .exceptions import LockAcquisitionError, LockReleaseError
from .db import db

logger = logging.getLogger(__name__)

class HeartbeatManager:
    """Manages the heartbeat thread for a locked resource."""
    
    def __init__(self, resource_name: str, lock_timeout: int):
        self.resource_name = resource_name
        self.lock_timeout = lock_timeout
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

    def is_active(self) -> bool:
        """Check if heartbeat thread is running."""
        return self.heartbeat_thread is not None and self.heartbeat_thread.is_alive()
    
    def start(self, owner_id: str) -> None:
        """Start the heartbeat thread."""
        with self.lock:
            if self.is_active():
                return

            self.stop_event.clear()
            self.heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop,
                args=(owner_id,),
                daemon=True,
                name=f"Heartbeat-{self.resource_name}"
            )
            self.heartbeat_thread.start()

    def _heartbeat_loop(self, owner_id: str) -> None:
        """Main heartbeat loop."""
        interval = max(self.lock_timeout * 20, 10)  # More frequent heartbeats
        while not self.stop_event.wait(interval):
            with db.session() as session:
                if not self._update_heartbeat(session, owner_id):
                    logger.warning(f"Lost ownership of {self.resource_name}")
                    self.stop_event.set()
                    break

    def _update_heartbeat(self, session: Session, owner_id: str) -> bool:
        """Update the heartbeat timestamp in the database."""
        result = session.execute(text("""
            UPDATE distributed_lock 
            SET last_heartbeat = NOW() AT TIME ZONE 'UTC'
            WHERE resource_name = :resource 
            AND lock_owner = :owner
            RETURNING 1
        """), {
            'resource': self.resource_name,
            'owner': owner_id
        })
        return bool(result.scalar())
    
    def stop(self) -> None:
        """Stop the heartbeat thread."""
        with self.lock:
            self.stop_event.set()
            if self.heartbeat_thread:
                self.heartbeat_thread.join(timeout=1.5)
                self.heartbeat_thread = None


class LockRegistry:
    """Registry for managing heartbeat managers."""
    
    def __init__(self):
        self.managers: Dict[str, HeartbeatManager] = {}
        self.lock = threading.Lock()

    def get_manager(self, resource_name: str, lock_timeout: int) -> HeartbeatManager:
        """Get or create a heartbeat manager for a resource."""
        with self.lock:
            if resource_name not in self.managers:
                self.managers[resource_name] = HeartbeatManager(resource_name, lock_timeout)
            return self.managers[resource_name]


class DistributedLock:
    """Context manager for distributed lock."""
    
    def __init__(self, manager: 'DistributedLockManager', resource_name: str):
        self.manager = manager
        self.resource_name = resource_name
        self._acquired = False  # Use protected attribute

    @property
    def is_acquired(self) -> bool:
        """Check if lock is currently acquired with database verification."""
        if not self._acquired:
            return False
            
        # Verify with database if the lock is still held
        try:
            with db.session() as session:
                record = session.query(models.DistributedLock).filter(
                    models.DistributedLock.resource_name == self.resource_name,
                    models.DistributedLock.lock_owner == self.manager.owner_id
                ).first()
                
                if not record:
                    self._acquired = False
        except Exception as e:
            logger.warning(f"Lock verification failed for {self.resource_name}: {str(e)}")
            # If verification fails, trust the local state
            return self._acquired
            
        return self._acquired
    
    def __enter__(self) -> 'DistributedLock':
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()

    def acquire(self) -> bool:
        """Acquire the lock."""
        self._acquired = self.manager._acquire_lock(self.resource_name)
        return self._acquired

    
    def release(self) -> None:
        """Release the lock."""
        if self._acquired:
            self.manager.release(self.resource_name)
            self._acquired = False


class DistributedLockManager:
    """Main distributed lock manager."""
    
    def __init__(
        self, 
        lock_timeout_minutes: int = 1,
        owner_id: Optional[str] = None
    ):
        self.lock_timeout = lock_timeout_minutes
        self.owner_id = owner_id or self._generate_owner_id()
        self.registry = LockRegistry()
        self.active_locks: Set[str] = set()
        self._register_signal_handlers()
        logger.info(f"Lock manager initialized for owner: {self.owner_id}")

    def _generate_owner_id(self) -> str:
        """Generate a unique owner ID."""
        host_id = os.getenv('HOSTNAME', socket.gethostname())
        return f"{host_id}-{uuid.uuid4()}"

    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        signal(SIGTERM, self._graceful_shutdown)
        signal(SIGINT, self._graceful_shutdown)

    def _graceful_shutdown(self, signum, frame) -> None:
        """Handle graceful shutdown."""
        logger.info("Graceful shutdown initiated")
        for resource in list(self.active_locks):
            try:
                self.release(resource)
            except LockReleaseError as e:
                logger.error(f"Shutdown error: {str(e)}")
        sys.exit(0)

    def health_check(self) -> dict:
        """Get current health status."""
        return {
            "active_locks": list(self.active_locks),
            "owner_id": self.owner_id,
            "heartbeats": {
                resource: manager.is_active()
                for resource, manager in self.registry.managers.items()
            }
        }

    def get_lock(self, resource_name: str) -> DistributedLock:
        """Get a distributed lock instance."""
        return DistributedLock(self, resource_name)

    def _initialize_resource(self, session: Session, resource_name: str) -> None:
        """Initialize a new lock resource if it doesn't exist."""
        stmt = text("""
            INSERT INTO distributed_lock (resource_name, lock_owner, last_heartbeat)
            VALUES (:resource_name, NULL, NOW() AT TIME ZONE 'UTC')
            ON CONFLICT (resource_name) DO NOTHING
        """)
        session.execute(stmt, {"resource_name": resource_name})

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True
    )
    def _acquire_lock(self, resource_name: str) -> bool:
        """Internal method to acquire a lock."""
        try:
            with db.session() as session:
                if session.in_transaction():
                    session.rollback()
                
                session.execute(text("SET TIME ZONE 'UTC'"))
                session.execute(text("SET lock_timeout = '2s'"))
                
                self._initialize_resource(session, resource_name)
                self._release_stale_locks(session, resource_name)
                
                threshold = text(
                    f"NOW() AT TIME ZONE 'UTC' - INTERVAL '{self.lock_timeout} MINUTES'"
                )
                
                lock = session.query(models.DistributedLock).filter(
                    and_(
                        models.DistributedLock.resource_name == resource_name,
                        or_(
                            models.DistributedLock.lock_owner.is_(None),
                            models.DistributedLock.last_heartbeat < threshold
                        )
                    )
                ).with_for_update(skip_locked=True).first()

                if lock:
                    lock.lock_owner = self.owner_id
                    lock.last_heartbeat = func.now()
                    
                    manager = self.registry.get_manager(resource_name, self.lock_timeout)
                    manager.start(self.owner_id)
                    self.active_locks.add(resource_name)
                    
                    logger.info(f"Acquired lock for {resource_name}")
                    return True
                    
                return False
        except Exception as e:
            logger.exception("Lock acquisition failed")
            if "in failed sql transaction" in str(e).lower():
                logger.warning("Detected aborted transaction - retrying may help")
            raise LockAcquisitionError(f"Acquisition error: {str(e)}")

    def release(self, resource_name: str) -> None:
        """Release a lock."""
        if resource_name not in self.active_locks:
            logger.warning(f"Lock not active: {resource_name}")
            return

        try:
            manager = self.registry.get_manager(resource_name, self.lock_timeout)
            manager.stop()

            with db.session() as session:
                session.execute(text("SET TIME ZONE 'UTC'"))
                result = session.execute(text("""
                    UPDATE distributed_lock
                    SET lock_owner = NULL,
                        last_heartbeat = NOW() AT TIME ZONE 'UTC'
                    WHERE resource_name = :resource
                    AND lock_owner = :owner
                """), {
                    "resource": resource_name,
                    "owner": self.owner_id
                })
                
                if result.rowcount > 0:
                    self.active_locks.discard(resource_name)
                    logger.info(f"Released lock for {resource_name}")
        except Exception as e:
            logger.exception("Lock release failed")
            raise LockReleaseError(f"Release error: {str(e)}")

    def _release_stale_locks(self, session: Session, resource_name: str) -> None:
        """Release stale locks that have expired."""
        try:
            session.execute(text(f"""
                UPDATE distributed_lock
                SET lock_owner = NULL
                WHERE resource_name = :resource
                AND lock_owner IS NOT NULL
                AND last_heartbeat < NOW() AT TIME ZONE 'UTC' - INTERVAL '{self.lock_timeout} MINUTES'
            """), {"resource": resource_name})
        except Exception as e:
            logger.warning(f"Stale lock cleanup failed: {str(e)}")

    def force_release_lock(self, resource_name: str) -> bool:
        """Force release a lock (admin function)."""
        try:
            if resource_name in self.registry.managers:
                self.registry.managers[resource_name].stop()
                
            with db.session() as session:
                session.execute(text("""
                    UPDATE distributed_lock
                    SET lock_owner = NULL
                    WHERE resource_name = :resource
                """), {"resource": resource_name})
                session.commit() #  # REQUIRED Manual/admin intervention
                
            self.active_locks.discard(resource_name)
            logger.warning(f"Force released lock for {resource_name}")
            return True
        except Exception as e:
            logger.error(f"Force release failed: {str(e)}")
            return False

    def stop_heartbeat(self, resource_name: str) -> None:
        """Stop heartbeat for testing purposes."""
        if resource_name in self.registry.managers:
            self.registry.managers[resource_name].stop()