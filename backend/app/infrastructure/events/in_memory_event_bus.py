"""In-memory event bus"""
from typing import Dict, List, Callable, Any
from ...domain.events.base_event import DomainEvent


class InMemoryEventBus:
    """In-memory event bus for publishing and subscribing to events"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._all_subscribers: List[Callable] = []  # Subscribers to all events
    
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe to a specific event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def subscribe_all(self, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe to all events"""
        self._all_subscribers.append(handler)
    
    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers"""
        event_type = getattr(event, 'event_type', type(event).__name__)
        
        # Notify type-specific subscribers
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Error in event handler for {event_type}: {e}")
        
        # Notify all-event subscribers
        for handler in self._all_subscribers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in all-events handler: {e}")
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """Publish multiple events"""
        for event in events:
            self.publish(event)

