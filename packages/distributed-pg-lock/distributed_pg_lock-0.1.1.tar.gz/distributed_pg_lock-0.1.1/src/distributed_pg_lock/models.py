from sqlalchemy import Column, String, DateTime, func
from .db import Base

class DistributedLock(Base):
    __tablename__ = 'distributed_lock'
    
    resource_name = Column(String(120), primary_key=True, unique=True)
    lock_owner = Column(String(80), nullable=True)
    last_heartbeat = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), 
                       onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<DistributedLock(resource='{self.resource_name}', owner='{self.lock_owner}')>"
