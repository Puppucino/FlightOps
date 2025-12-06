"""
Database type definitions that work with both SQLite and PostgreSQL
"""
from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type when available, otherwise uses String(36).
    """
    impl = String
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID())
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            # For SQLite, convert UUID to string
            # For PostgreSQL, the UUID type handles UUID objects directly
            if dialect.name == 'postgresql':
                return value  # PostgreSQL can handle UUID objects
            else:
                return str(value)  # SQLite needs string
        # Convert string/bytes to UUID first, then to appropriate format
        if isinstance(value, str):
            uuid_val = uuid.UUID(value)
            return uuid_val if dialect.name == 'postgresql' else str(uuid_val)
        if isinstance(value, bytes):
            uuid_val = uuid.UUID(value.decode('ascii'))
            return uuid_val if dialect.name == 'postgresql' else str(uuid_val)
        # Try to convert other types
        try:
            uuid_val = uuid.UUID(str(value))
            return uuid_val if dialect.name == 'postgresql' else str(uuid_val)
        except (TypeError, ValueError):
            return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        if isinstance(value, str):
            return uuid.UUID(value)
        if isinstance(value, bytes):
            return uuid.UUID(value.decode('ascii'))
        return uuid.UUID(str(value))
