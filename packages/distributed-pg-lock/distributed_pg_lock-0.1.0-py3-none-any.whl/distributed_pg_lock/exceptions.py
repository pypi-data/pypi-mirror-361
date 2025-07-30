class DistributedLockError(Exception):
    """Base exception for all distributed lock errors"""
    pass

class LockAcquisitionError(DistributedLockError):
    """Failed to acquire lock"""
    pass

class LockReleaseError(DistributedLockError):
    """Failed to release lock"""
    pass