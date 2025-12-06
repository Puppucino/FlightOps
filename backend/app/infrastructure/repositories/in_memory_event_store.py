"""In-memory event store"""
from typing import List, Dict
from uuid import UUID
from ...domain.interfaces.repositories import IEventStore


class InMemoryEventStore(IEventStore):
    """In-memory implementation of event store"""
    
    def __init__(self):
        self._events: List = []
        self._events_by_aggregate: Dict[UUID, List] = {}
        self._events_by_type: Dict[str, List] = {}
    
    def append(self, event) -> None:
        """Append event to store"""
        self._events.append(event)
        
        # Index by event type
        event_type = getattr(event, 'event_type', type(event).__name__)
        if event_type not in self._events_by_type:
            self._events_by_type[event_type] = []
        self._events_by_type[event_type].append(event)
        
        # Index by aggregate ID if available
        aggregate_id = self._extract_aggregate_id(event)
        if aggregate_id:
            if aggregate_id not in self._events_by_aggregate:
                self._events_by_aggregate[aggregate_id] = []
            self._events_by_aggregate[aggregate_id].append(event)
    
    def get_events_by_aggregate_id(self, aggregate_id: UUID) -> List:
        """Get all events for an aggregate"""
        return self._events_by_aggregate.get(aggregate_id, []).copy()
    
    def get_events_by_type(self, event_type: str) -> List:
        """Get all events of a specific type"""
        return self._events_by_type.get(event_type, []).copy()
    
    def get_all_events(self) -> List:
        """Get all events"""
        return self._events.copy()
    
    def _extract_aggregate_id(self, event) -> Optional[UUID]:
        """Extract aggregate ID from event"""
        # Try common attribute names
        for attr in ['flight_id', 'airport_id', 'aggregate_id']:
            if hasattr(event, attr):
                value = getattr(event, attr)
                if isinstance(value, UUID):
                    return value
        return None

