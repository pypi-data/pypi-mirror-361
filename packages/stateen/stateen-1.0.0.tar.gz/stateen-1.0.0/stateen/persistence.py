"""
State persistence functionality for Stateen.

This module provides functionality to persist state across sessions,
useful for applications that need to maintain state between runs.
"""

import json
import pickle
import os
from typing import Any, Optional, Callable, TypeVar, Dict
from pathlib import Path
import threading
from .core import use_state

T = TypeVar('T')


class StatePersistence:
    """Handle state persistence to various storage backends."""
    
    def __init__(self, storage_path: str = ".stateen_state"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self._lock = threading.Lock()
    
    def save_state(self, state_id: str, value: Any, format: str = "json"):
        """Save state to persistent storage."""
        with self._lock:
            file_path = self.storage_path / f"{state_id}.{format}"
            
            try:
                if format == "json":
                    with open(file_path, 'w') as f:
                        json.dump(value, f, indent=2)
                elif format == "pickle":
                    with open(file_path, 'wb') as f:
                        pickle.dump(value, f)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            except Exception as e:
                print(f"Error saving state {state_id}: {e}")
    
    def load_state(self, state_id: str, default_value: Any = None, format: str = "json") -> Any:
        """Load state from persistent storage."""
        with self._lock:
            file_path = self.storage_path / f"{state_id}.{format}"
            
            if not file_path.exists():
                return default_value
            
            try:
                if format == "json":
                    with open(file_path, 'r') as f:
                        return json.load(f)
                elif format == "pickle":
                    with open(file_path, 'rb') as f:
                        return pickle.load(f)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            except Exception as e:
                print(f"Error loading state {state_id}: {e}")
                return default_value
    
    def delete_state(self, state_id: str, format: str = "json"):
        """Delete persisted state."""
        with self._lock:
            file_path = self.storage_path / f"{state_id}.{format}"
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    print(f"Error deleting state {state_id}: {e}")
    
    def list_states(self) -> list[str]:
        """List all persisted state IDs."""
        with self._lock:
            states = []
            for file_path in self.storage_path.iterdir():
                if file_path.is_file():
                    state_id = file_path.stem
                    states.append(state_id)
            return states
    
    def clear_all_states(self):
        """Clear all persisted states."""
        with self._lock:
            for file_path in self.storage_path.iterdir():
                if file_path.is_file():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")


# Global persistence manager
_default_persistence = StatePersistence()


def use_persistent_state(initial_value: T, 
                        state_id: str,
                        storage_path: Optional[str] = None,
                        format: str = "json",
                        auto_save: bool = True,
                        on_change: Optional[Callable[[T, T], None]] = None) -> tuple[Callable[[], T], Callable[[T], None]]:
    """
    Create a persistent state that survives between sessions.
    
    Args:
        initial_value: Default value if no persisted state exists
        state_id: Unique identifier for the state
        storage_path: Optional custom storage path
        format: Storage format ("json" or "pickle")
        auto_save: Whether to automatically save state changes
        on_change: Optional callback called when state changes
    
    Returns:
        Tuple of (getter_function, setter_function)
    
    Example:
        # Basic persistent state
        count, set_count = use_persistent_state(0, "app_counter")
        
        # Custom storage location
        user_prefs, set_user_prefs = use_persistent_state(
            {"theme": "dark"}, 
            "user_preferences",
            storage_path="./config"
        )
        
        # With callback
        def on_settings_change(old, new):
            print(f"Settings updated: {old} -> {new}")
        
        settings, set_settings = use_persistent_state(
            {"debug": False},
            "app_settings",
            on_change=on_settings_change
        )
    """
    
    # Use custom persistence manager if storage_path is provided
    if storage_path:
        persistence = StatePersistence(storage_path)
    else:
        persistence = _default_persistence
    
    # Load initial value from storage
    loaded_value = persistence.load_state(state_id, initial_value, format)
    
    def combined_on_change(old_value: T, new_value: T):
        """Combined callback that handles persistence and user callback."""
        if auto_save:
            persistence.save_state(state_id, new_value, format)
        
        if on_change:
            on_change(old_value, new_value)
    
    # Create the state with the loaded value
    return use_state(loaded_value, state_id, combined_on_change)


def save_state_to_file(state_id: str, value: Any, file_path: str, format: str = "json"):
    """Save a specific state value to a file."""
    persistence = StatePersistence()
    
    # Temporarily save to custom location
    original_path = persistence.storage_path
    persistence.storage_path = Path(file_path).parent
    
    try:
        persistence.save_state(Path(file_path).stem, value, format)
    finally:
        persistence.storage_path = original_path


def load_state_from_file(file_path: str, default_value: Any = None, format: str = "json") -> Any:
    """Load a state value from a file."""
    persistence = StatePersistence()
    
    # Temporarily load from custom location
    original_path = persistence.storage_path
    persistence.storage_path = Path(file_path).parent
    
    try:
        return persistence.load_state(Path(file_path).stem, default_value, format)
    finally:
        persistence.storage_path = original_path


def clear_persistent_state(state_id: str, storage_path: Optional[str] = None, format: str = "json"):
    """Clear a specific persistent state."""
    if storage_path:
        persistence = StatePersistence(storage_path)
    else:
        persistence = _default_persistence
    
    persistence.delete_state(state_id, format)


def list_persistent_states(storage_path: Optional[str] = None) -> list[str]:
    """List all persistent state IDs."""
    if storage_path:
        persistence = StatePersistence(storage_path)
    else:
        persistence = _default_persistence
    
    return persistence.list_states()


def clear_all_persistent_states(storage_path: Optional[str] = None):
    """Clear all persistent states."""
    if storage_path:
        persistence = StatePersistence(storage_path)
    else:
        persistence = _default_persistence
    
    persistence.clear_all_states()


# Export the default persistence manager for advanced usage
def get_default_persistence() -> StatePersistence:
    """Get the default persistence manager."""
    return _default_persistence