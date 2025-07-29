"""
Additional hooks for enhanced state management functionality.

This module provides additional hooks similar to React's useEffect, useMemo, etc.
adapted for Python applications.
"""

import threading
import weakref
from typing import Any, Callable, Optional, List, Dict, TypeVar
from functools import wraps
import hashlib
import time

T = TypeVar('T')

class EffectManager:
    """Manager for side effects similar to React's useEffect."""
    
    def __init__(self):
        self._effects: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def add_effect(self, effect_id: str, effect: Callable[[], Optional[Callable[[], None]]], 
                   dependencies: Optional[List[Any]] = None):
        """Add an effect to be managed."""
        with self._lock:
            # Calculate dependency hash
            dep_hash = self._hash_dependencies(dependencies) if dependencies else None
            
            # Check if we should run the effect
            should_run = True
            if effect_id in self._effects:
                old_hash = self._effects[effect_id].get('dep_hash')
                should_run = dep_hash != old_hash
            
            if should_run:
                # Cleanup previous effect if exists
                if effect_id in self._effects and 'cleanup' in self._effects[effect_id]:
                    try:
                        self._effects[effect_id]['cleanup']()
                    except Exception as e:
                        print(f"Error in effect cleanup: {e}")
                
                # Run the new effect
                try:
                    cleanup = effect()
                    self._effects[effect_id] = {
                        'effect': effect,
                        'cleanup': cleanup,
                        'dep_hash': dep_hash,
                        'dependencies': dependencies
                    }
                except Exception as e:
                    print(f"Error in effect: {e}")
    
    def cleanup_effect(self, effect_id: str):
        """Cleanup a specific effect."""
        with self._lock:
            if effect_id in self._effects and 'cleanup' in self._effects[effect_id]:
                try:
                    self._effects[effect_id]['cleanup']()
                except Exception as e:
                    print(f"Error in effect cleanup: {e}")
                del self._effects[effect_id]
    
    def cleanup_all_effects(self):
        """Cleanup all effects."""
        with self._lock:
            for effect_id in list(self._effects.keys()):
                self.cleanup_effect(effect_id)
    
    def _hash_dependencies(self, dependencies: List[Any]) -> str:
        """Create a hash of dependencies for comparison."""
        dep_str = str(dependencies)
        return hashlib.md5(dep_str.encode()).hexdigest()


class MemoManager:
    """Manager for memoized values similar to React's useMemo."""
    
    def __init__(self):
        self._memos: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def get_memo(self, memo_id: str, compute_fn: Callable[[], T], 
                 dependencies: Optional[List[Any]] = None) -> T:
        """Get a memoized value."""
        with self._lock:
            dep_hash = self._hash_dependencies(dependencies) if dependencies else None
            
            # Check if we have a cached value with same dependencies
            if memo_id in self._memos:
                cached = self._memos[memo_id]
                if cached.get('dep_hash') == dep_hash:
                    return cached['value']
            
            # Compute new value
            try:
                value = compute_fn()
                self._memos[memo_id] = {
                    'value': value,
                    'dep_hash': dep_hash,
                    'dependencies': dependencies
                }
                return value
            except Exception as e:
                print(f"Error in memo computation: {e}")
                # Return cached value if available
                if memo_id in self._memos:
                    return self._memos[memo_id]['value']
                raise
    
    def clear_memo(self, memo_id: str):
        """Clear a specific memo."""
        with self._lock:
            if memo_id in self._memos:
                del self._memos[memo_id]
    
    def clear_all_memos(self):
        """Clear all memos."""
        with self._lock:
            self._memos.clear()
    
    def _hash_dependencies(self, dependencies: List[Any]) -> str:
        """Create a hash of dependencies for comparison."""
        dep_str = str(dependencies)
        return hashlib.md5(dep_str.encode()).hexdigest()


class CallbackManager:
    """Manager for memoized callbacks similar to React's useCallback."""
    
    def __init__(self):
        self._callbacks: Dict[str, Dict] = {}
        self._lock = threading.Lock()
    
    def get_callback(self, callback_id: str, callback: Callable, 
                     dependencies: Optional[List[Any]] = None) -> Callable:
        """Get a memoized callback."""
        with self._lock:
            dep_hash = self._hash_dependencies(dependencies) if dependencies else None
            
            # Check if we have a cached callback with same dependencies
            if callback_id in self._callbacks:
                cached = self._callbacks[callback_id]
                if cached.get('dep_hash') == dep_hash:
                    return cached['callback']
            
            # Cache new callback
            self._callbacks[callback_id] = {
                'callback': callback,
                'dep_hash': dep_hash,
                'dependencies': dependencies
            }
            return callback
    
    def clear_callback(self, callback_id: str):
        """Clear a specific callback."""
        with self._lock:
            if callback_id in self._callbacks:
                del self._callbacks[callback_id]
    
    def clear_all_callbacks(self):
        """Clear all callbacks."""
        with self._lock:
            self._callbacks.clear()
    
    def _hash_dependencies(self, dependencies: List[Any]) -> str:
        """Create a hash of dependencies for comparison."""
        dep_str = str(dependencies)
        return hashlib.md5(dep_str.encode()).hexdigest()


# Global managers
_effect_manager = EffectManager()
_memo_manager = MemoManager()
_callback_manager = CallbackManager()


def use_effect(effect: Callable[[], Optional[Callable[[], None]]], 
               dependencies: Optional[List[Any]] = None,
               effect_id: Optional[str] = None):
    """
    Run side effects similar to React's useEffect.
    
    Args:
        effect: Function to run. Can return a cleanup function.
        dependencies: List of dependencies. Effect runs when these change.
        effect_id: Optional unique identifier for the effect.
    
    Example:
        # Run once
        use_effect(lambda: print("Component mounted"))
        
        # Run when count changes
        count, set_count = use_state(0)
        use_effect(
            lambda: print(f"Count is now {count()}"),
            dependencies=[count()]
        )
        
        # With cleanup
        def setup_timer():
            timer = threading.Timer(1.0, lambda: print("Timer fired"))
            timer.start()
            return lambda: timer.cancel()  # Cleanup function
        
        use_effect(setup_timer, dependencies=[])
    """
    if effect_id is None:
        effect_id = str(id(effect))
    
    _effect_manager.add_effect(effect_id, effect, dependencies)


def use_memo(compute_fn: Callable[[], T], 
             dependencies: Optional[List[Any]] = None,
             memo_id: Optional[str] = None) -> T:
    """
    Memoize expensive computations similar to React's useMemo.
    
    Args:
        compute_fn: Function that computes the value
        dependencies: List of dependencies. Recomputes when these change.
        memo_id: Optional unique identifier for the memo.
    
    Returns:
        The memoized value
    
    Example:
        count, set_count = use_state(0)
        
        expensive_value = use_memo(
            lambda: sum(range(count() * 1000)),
            dependencies=[count()]
        )
    """
    if memo_id is None:
        memo_id = str(id(compute_fn))
    
    return _memo_manager.get_memo(memo_id, compute_fn, dependencies)


def use_callback(callback: Callable, 
                 dependencies: Optional[List[Any]] = None,
                 callback_id: Optional[str] = None) -> Callable:
    """
    Memoize callbacks similar to React's useCallback.
    
    Args:
        callback: The callback function to memoize
        dependencies: List of dependencies. Callback changes when these change.
        callback_id: Optional unique identifier for the callback.
    
    Returns:
        The memoized callback
    
    Example:
        count, set_count = use_state(0)
        
        increment = use_callback(
            lambda: set_count(count() + 1),
            dependencies=[count()]
        )
    """
    if callback_id is None:
        callback_id = str(id(callback))
    
    return _callback_manager.get_callback(callback_id, callback, dependencies)


# Cleanup functions
def cleanup_effect(effect_id: str):
    """Cleanup a specific effect."""
    _effect_manager.cleanup_effect(effect_id)


def cleanup_all_effects():
    """Cleanup all effects."""
    _effect_manager.cleanup_all_effects()


def clear_memo(memo_id: str):
    """Clear a specific memo."""
    _memo_manager.clear_memo(memo_id)


def clear_all_memos():
    """Clear all memos."""
    _memo_manager.clear_all_memos()


def clear_callback(callback_id: str):
    """Clear a specific callback."""
    _callback_manager.clear_callback(callback_id)


def clear_all_callbacks():
    """Clear all callbacks."""
    _callback_manager.clear_all_callbacks()


def cleanup_all_hooks():
    """Cleanup all hooks (effects, memos, callbacks)."""
    cleanup_all_effects()
    clear_all_memos()
    clear_all_callbacks()