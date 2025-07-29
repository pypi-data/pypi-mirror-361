"""
Stateen - Minimal State Management Library

A minimal state management tool similar to React's useState for Python applications.
Supports GUI, CLI, games, and reproduction experiments.

Example usage:
    from stateen import use_state
    
    # Basic usage
    count, set_count = use_state(0)
    print(count())  # 0
    set_count(5)
    print(count())  # 5
    
    # With callback
    def on_change(old_value, new_value):
        print(f"Count changed from {old_value} to {new_value}")
    
    count, set_count = use_state(0, on_change=on_change)
    set_count(10)  # Prints: Count changed from 0 to 10
"""

from .core import use_state, StateContext, create_context, use_context
from .hooks import use_effect, use_memo, use_callback
from .persistence import use_persistent_state
from .debugging import debug_state, StateDebugger

__version__ = "1.0.0"
__author__ = "Stateen Team"
__email__ = "contact@stateen.dev"

__all__ = [
    "use_state",
    "StateContext", 
    "create_context",
    "use_context",
    "use_effect",
    "use_memo", 
    "use_callback",
    "use_persistent_state",
    "debug_state",
    "StateDebugger"
]