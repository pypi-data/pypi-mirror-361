"""
Core state management implementation for Stateen.

This module provides the fundamental state management functionality
similar to React's useState but adapted for Python applications.
"""

import threading
import weakref
from typing import Any, Callable, Optional, Dict, List, TypeVar, Generic
from dataclasses import dataclass, field
from contextlib import contextmanager
import uuid

T = TypeVar('T')

@dataclass
class StateEntry:
    """Internal representation of a state entry."""
    value: Any
    setter: Callable[[Any], None]
    callbacks: List[Callable[[Any, Any], None]] = field(default_factory=list)
    history: List[Any] = field(default_factory=list)
    max_history: int = 100
    
    def add_callback(self, callback: Callable[[Any, Any], None]):
        """Add a callback to be called when state changes."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Any, Any], None]):
        """Remove a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def set_value(self, new_value: Any):
        """Set the value and trigger callbacks."""
        old_value = self.value
        self.value = new_value
        
        # Add to history
        self.history.append(old_value)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Trigger callbacks
        for callback in self.callbacks:
            try:
                callback(old_value, new_value)
            except Exception as e:
                print(f"Error in state callback: {e}")


class StateManager:
    """Global state manager for the application."""
    
    def __init__(self):
        self._states: Dict[str, StateEntry] = {}
        self._lock = threading.Lock()
        self._context_stack: List['StateContext'] = []
    
    def create_state(self, 
                    initial_value: T, 
                    state_id: Optional[str] = None,
                    on_change: Optional[Callable[[T, T], None]] = None) -> tuple[Callable[[], T], Callable[[T], None]]:
        """Create a new state with getter and setter functions."""
        
        if state_id is None:
            state_id = str(uuid.uuid4())
        
        with self._lock:
            # Create the state entry
            def setter(new_value: T):
                with self._lock:
                    if state_id in self._states:
                        self._states[state_id].set_value(new_value)
            
            state_entry = StateEntry(value=initial_value, setter=setter)
            
            # Add the onChange callback if provided
            if on_change:
                state_entry.add_callback(on_change)
            
            self._states[state_id] = state_entry
            
            # Create getter function
            def getter() -> T:
                with self._lock:
                    if state_id in self._states:
                        return self._states[state_id].value
                    return initial_value
            
            return getter, setter
    
    def get_state(self, state_id: str) -> Optional[StateEntry]:
        """Get a state entry by ID."""
        with self._lock:
            return self._states.get(state_id)
    
    def remove_state(self, state_id: str):
        """Remove a state entry."""
        with self._lock:
            if state_id in self._states:
                del self._states[state_id]
    
    def clear_all_states(self):
        """Clear all states."""
        with self._lock:
            self._states.clear()
    
    def get_all_states(self) -> Dict[str, Any]:
        """Get all current state values."""
        with self._lock:
            return {state_id: entry.value for state_id, entry in self._states.items()}
    
    def push_context(self, context: 'StateContext'):
        """Push a new context onto the stack."""
        self._context_stack.append(context)
    
    def pop_context(self) -> Optional['StateContext']:
        """Pop the current context from the stack."""
        if self._context_stack:
            return self._context_stack.pop()
        return None
    
    def get_current_context(self) -> Optional['StateContext']:
        """Get the current context."""
        return self._context_stack[-1] if self._context_stack else None


# Global state manager instance
_global_state_manager = StateManager()


def use_state(initial_value: T, 
              state_id: Optional[str] = None,
              on_change: Optional[Callable[[T, T], None]] = None) -> tuple[Callable[[], T], Callable[[T], None]]:
    """
    Create a state similar to React's useState.
    
    Args:
        initial_value: The initial value for the state
        state_id: Optional unique identifier for the state
        on_change: Optional callback called when state changes (old_value, new_value)
    
    Returns:
        Tuple of (getter_function, setter_function)
        
    Example:
        count, set_count = use_state(0)
        print(count())  # 0
        set_count(5)
        print(count())  # 5
        
        # With callback
        def on_count_change(old, new):
            print(f"Count: {old} -> {new}")
        
        count, set_count = use_state(0, on_change=on_count_change)
        set_count(10)  # Prints: Count: 0 -> 10
    """
    return _global_state_manager.create_state(initial_value, state_id, on_change)


class StateContext:
    """Context for scoped state management."""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self._manager = StateManager()
        self._active = False
    
    def __enter__(self):
        self._active = True
        _global_state_manager.push_context(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._active = False
        _global_state_manager.pop_context()
    
    def use_state(self, initial_value: T, 
                  state_id: Optional[str] = None,
                  on_change: Optional[Callable[[T, T], None]] = None) -> tuple[Callable[[], T], Callable[[T], None]]:
        """Create a state within this context."""
        return self._manager.create_state(initial_value, state_id, on_change)
    
    def clear_states(self):
        """Clear all states in this context."""
        self._manager.clear_all_states()
    
    def get_all_states(self) -> Dict[str, Any]:
        """Get all states in this context."""
        return self._manager.get_all_states()


def create_context(name: str = "default") -> StateContext:
    """Create a new state context."""
    return StateContext(name)


def use_context() -> Optional[StateContext]:
    """Get the current state context."""
    return _global_state_manager.get_current_context()


# Utility functions for debugging and management
def get_all_states() -> Dict[str, Any]:
    """Get all current state values from the global state manager."""
    return _global_state_manager.get_all_states()


def clear_all_states():
    """Clear all states from the global state manager."""
    _global_state_manager.clear_all_states()


def get_state_history(state_id: str) -> List[Any]:
    """Get the history of a specific state."""
    state_entry = _global_state_manager.get_state(state_id)
    return state_entry.history if state_entry else []