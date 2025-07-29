"""
Debugging and development tools for Stateen.

This module provides tools for debugging state changes, inspecting state,
and monitoring state management during development.
"""

import time
import threading
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
from contextlib import contextmanager

from .core import _global_state_manager


@dataclass
class StateChangeEvent:
    """Represents a state change event."""
    state_id: str
    old_value: Any
    new_value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    thread_id: str = field(default_factory=lambda: str(threading.current_thread().ident))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'state_id': self.state_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'timestamp': self.timestamp.isoformat(),
            'thread_id': self.thread_id
        }


class StateDebugger:
    """Debug and monitor state changes."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._events: List[StateChangeEvent] = []
        self._lock = threading.Lock()
        self._max_events = 1000
        self._filters: List[Callable[[StateChangeEvent], bool]] = []
        self._listeners: List[Callable[[StateChangeEvent], None]] = []
    
    def enable(self):
        """Enable debugging."""
        self.enabled = True
    
    def disable(self):
        """Disable debugging."""
        self.enabled = False
    
    def add_filter(self, filter_fn: Callable[[StateChangeEvent], bool]):
        """Add a filter for events."""
        self._filters.append(filter_fn)
    
    def remove_filter(self, filter_fn: Callable[[StateChangeEvent], bool]):
        """Remove a filter."""
        if filter_fn in self._filters:
            self._filters.remove(filter_fn)
    
    def add_listener(self, listener: Callable[[StateChangeEvent], None]):
        """Add a listener for state change events."""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[StateChangeEvent], None]):
        """Remove a listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def log_change(self, state_id: str, old_value: Any, new_value: Any):
        """Log a state change."""
        if not self.enabled:
            return
        
        event = StateChangeEvent(state_id, old_value, new_value)
        
        # Apply filters
        for filter_fn in self._filters:
            if not filter_fn(event):
                return
        
        with self._lock:
            self._events.append(event)
            
            # Limit event history
            if len(self._events) > self._max_events:
                self._events.pop(0)
        
        # Notify listeners
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"Error in debug listener: {e}")
    
    def get_events(self, 
                   state_id: Optional[str] = None,
                   since: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[StateChangeEvent]:
        """Get logged events with optional filtering."""
        with self._lock:
            events = self._events.copy()
        
        # Filter by state_id
        if state_id:
            events = [e for e in events if e.state_id == state_id]
        
        # Filter by timestamp
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # Apply limit
        if limit:
            events = events[-limit:]
        
        return events
    
    def get_state_history(self, state_id: str) -> List[StateChangeEvent]:
        """Get the history of changes for a specific state."""
        return self.get_events(state_id=state_id)
    
    def clear_events(self):
        """Clear all logged events."""
        with self._lock:
            self._events.clear()
    
    def print_events(self, 
                     state_id: Optional[str] = None,
                     since: Optional[datetime] = None,
                     limit: Optional[int] = 10):
        """Print events to console."""
        events = self.get_events(state_id, since, limit)
        
        if not events:
            print("No events found")
            return
        
        print(f"\n{'='*60}")
        print(f"State Change Events ({len(events)} events)")
        print(f"{'='*60}")
        
        for event in events:
            print(f"[{event.timestamp.strftime('%H:%M:%S.%f')[:-3]}] "
                  f"{event.state_id}: {event.old_value} -> {event.new_value}")
        
        print(f"{'='*60}\n")
    
    def export_events(self, file_path: str, 
                      state_id: Optional[str] = None,
                      since: Optional[datetime] = None):
        """Export events to a JSON file."""
        events = self.get_events(state_id, since)
        
        with open(file_path, 'w') as f:
            json.dump([event.to_dict() for event in events], f, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about state changes."""
        with self._lock:
            events = self._events.copy()
        
        if not events:
            return {"total_events": 0}
        
        state_counts = {}
        for event in events:
            state_counts[event.state_id] = state_counts.get(event.state_id, 0) + 1
        
        return {
            "total_events": len(events),
            "state_counts": state_counts,
            "most_changed_state": max(state_counts.items(), key=lambda x: x[1])[0],
            "first_event": events[0].timestamp.isoformat(),
            "last_event": events[-1].timestamp.isoformat()
        }


# Global debugger instance
_global_debugger = StateDebugger()


def debug_state(enabled: bool = True) -> StateDebugger:
    """
    Enable or disable state debugging.
    
    Args:
        enabled: Whether to enable debugging
    
    Returns:
        The global debugger instance
    
    Example:
        # Enable debugging
        debugger = debug_state(True)
        
        # Create some state
        count, set_count = use_state(0, state_id="counter")
        set_count(5)
        set_count(10)
        
        # View events
        debugger.print_events()
        
        # Get statistics
        stats = debugger.get_statistics()
        print(stats)
    """
    _global_debugger.enabled = enabled
    return _global_debugger


def get_debugger() -> StateDebugger:
    """Get the global debugger instance."""
    return _global_debugger


@contextmanager
def debug_context(enabled: bool = True):
    """
    Context manager for temporary debugging.
    
    Example:
        with debug_context(True):
            count, set_count = use_state(0)
            set_count(5)
            # Debugging is enabled only within this context
    """
    original_state = _global_debugger.enabled
    _global_debugger.enabled = enabled
    try:
        yield _global_debugger
    finally:
        _global_debugger.enabled = original_state


def print_state_info():
    """Print information about all current states."""
    all_states = _global_state_manager.get_all_states()
    
    print(f"\n{'='*60}")
    print(f"Current State Information")
    print(f"{'='*60}")
    
    if not all_states:
        print("No states found")
        return
    
    for state_id, value in all_states.items():
        print(f"{state_id}: {value}")
    
    print(f"{'='*60}\n")


def create_state_monitor(state_id: str, callback: Optional[Callable[[Any, Any], None]] = None):
    """
    Create a monitor for a specific state.
    
    Args:
        state_id: The state to monitor
        callback: Optional callback for state changes
    
    Example:
        # Monitor with default logging
        monitor = create_state_monitor("counter")
        
        # Monitor with custom callback
        def on_change(old, new):
            print(f"Counter changed: {old} -> {new}")
        
        monitor = create_state_monitor("counter", on_change)
    """
    def default_callback(old_value, new_value):
        print(f"[MONITOR] {state_id}: {old_value} -> {new_value}")
    
    actual_callback = callback or default_callback
    
    def monitor_filter(event: StateChangeEvent) -> bool:
        return event.state_id == state_id
    
    def monitor_listener(event: StateChangeEvent):
        actual_callback(event.old_value, event.new_value)
    
    _global_debugger.add_filter(monitor_filter)
    _global_debugger.add_listener(monitor_listener)
    
    return {
        'filter': monitor_filter,
        'listener': monitor_listener,
        'remove': lambda: (
            _global_debugger.remove_filter(monitor_filter),
            _global_debugger.remove_listener(monitor_listener)
        )
    }


# Hook into state changes to enable debugging
def _patch_state_manager():
    """Patch the state manager to enable debugging."""
    # For now, we'll rely on the callback system in StateEntry
    # This is a placeholder for future implementation
    pass


# Initialize debugging
_patch_state_manager()