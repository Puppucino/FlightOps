"""Base domain event"""
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events"""
    
    event_id: UUID
    occurred_at: datetime
    event_type: str
    
    def __init__(self, event_type: str, occurred_at: Optional[datetime] = None):
        self.event_id = uuid4()
        self.occurred_at = occurred_at or datetime.now()
        self.event_type = event_type

