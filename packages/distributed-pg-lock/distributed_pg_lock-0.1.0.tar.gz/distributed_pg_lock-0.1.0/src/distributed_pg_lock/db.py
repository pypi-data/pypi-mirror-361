from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import os
from typing import Generator, Optional

Base = declarative_base()

class Database:
    """A database connection manager with connection pooling and scoped sessions.
    
    Features:
    - Connection pooling with configurable size
    - Automatic connection health checks
    - Thread-safe scoped sessions
    - Context manager for automatic session cleanup
    - Table creation utility
    """
    
    def __init__(self, db_url: Optional[str] = None, **engine_kwargs):
        """Initialize the database connection.
        
        Args:
            db_url: Database connection URL. If None, uses DB_URL environment variable.
            **engine_kwargs: Additional kwargs to pass to create_engine()
        """
        self.db_url = db_url or os.getenv("DB_URL")
        if not self.db_url:
            raise ValueError("No database URL provided and DB_URL environment variable not set")
            
        # Default engine configuration
        default_config = {
            'pool_size': 10,
            'max_overflow': 20,
            'pool_pre_ping': True,
            'pool_recycle': 3600,  # Recycle connections every hour
            'pool_timeout': 30,    # Wait 30 seconds for connection
            'echo': False,         # Don't log all SQL by default
            'future': True,        # Enable SQLAlchemy 2.0 behavior
            'execution_options': {
                'isolation_level': 'READ COMMITTED'
            }
        }
        default_config.update(engine_kwargs)
        
        self.engine = create_engine(self.db_url, **default_config)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            future= True,        # Enable SQLAlchemy 2.0 behavior
        )
        self.ScopedSession = scoped_session(self.session_factory)

    @contextmanager
    def session(self) -> Generator[scoped_session, None, None]:
        """Provide a transactional scope around a series of operations.
        
        Usage:
            with db.session() as session:
                # Do database operations
                session.query(...)
        """
        session = self.ScopedSession()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            self.ScopedSession.remove()

    def create_tables(self, checkfirst: bool = True) -> None:
        """Create all tables defined in your models.
        
        Args:
            checkfirst: If True, will skip tables that already exist
        """
        Base.metadata.create_all(bind=self.engine, checkfirst=checkfirst)

    def drop_tables(self, checkfirst: bool = True) -> None:
        """Drop all tables (useful for testing).
        
        Args:
            checkfirst: If True, will skip tables that don't exist
        """
        Base.metadata.drop_all(bind=self.engine, checkfirst=checkfirst)

    def get_session(self) -> scoped_session:
        """Get a raw session (use with caution - you must close it manually).
        
        Prefer using the session() context manager for most cases.
        """
        return self.ScopedSession()

# Global instance (can be overridden by users)
db = Database()