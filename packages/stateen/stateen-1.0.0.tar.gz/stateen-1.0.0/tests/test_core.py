#!/usr/bin/env python3
"""
Test suite for stateen.core module.

This module contains comprehensive tests for the core state management
functionality of the Stateen library.
"""

import unittest
import threading
import time
from unittest.mock import Mock, patch

from stateen.core import (
    use_state, StateManager, StateContext, create_context, use_context,
    get_all_states, clear_all_states, get_state_history
)

class TestUseState(unittest.TestCase):
    """Test the use_state function."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
    
    def test_basic_state_creation(self):
        """Test basic state creation and usage."""
        # Create a state
        count, set_count = use_state(0)
        
        # Test initial value
        self.assertEqual(count(), 0)
        
        # Test setting value
        set_count(5)
        self.assertEqual(count(), 5)
        
        # Test updating value
        set_count(count() + 1)
        self.assertEqual(count(), 6)
    
    def test_state_with_different_types(self):
        """Test state with different data types."""
        # String state
        name, set_name = use_state("John")
        self.assertEqual(name(), "John")
        set_name("Jane")
        self.assertEqual(name(), "Jane")
        
        # List state
        items, set_items = use_state([1, 2, 3])
        self.assertEqual(items(), [1, 2, 3])
        set_items([4, 5, 6])
        self.assertEqual(items(), [4, 5, 6])
        
        # Dictionary state
        user, set_user = use_state({"name": "John", "age": 30})
        self.assertEqual(user(), {"name": "John", "age": 30})
        set_user({"name": "Jane", "age": 25})
        self.assertEqual(user(), {"name": "Jane", "age": 25})
    
    def test_state_with_callback(self):
        """Test state with onChange callback."""
        callback_calls = []
        
        def on_change(old_value, new_value):
            callback_calls.append((old_value, new_value))
        
        count, set_count = use_state(0, on_change=on_change)
        
        # Test that callback is called
        set_count(5)
        self.assertEqual(len(callback_calls), 1)
        self.assertEqual(callback_calls[0], (0, 5))
        
        # Test multiple changes
        set_count(10)
        self.assertEqual(len(callback_calls), 2)
        self.assertEqual(callback_calls[1], (5, 10))
    
    def test_state_with_custom_id(self):
        """Test state with custom ID."""
        count, set_count = use_state(0, state_id="counter")
        
        # Test that state can be retrieved by ID
        all_states = get_all_states()
        self.assertIn("counter", all_states)
        self.assertEqual(all_states["counter"], 0)
        
        # Update state
        set_count(42)
        all_states = get_all_states()
        self.assertEqual(all_states["counter"], 42)
    
    def test_multiple_states(self):
        """Test multiple independent states."""
        count1, set_count1 = use_state(0, state_id="count1")
        count2, set_count2 = use_state(10, state_id="count2")
        
        # Test independence
        set_count1(5)
        self.assertEqual(count1(), 5)
        self.assertEqual(count2(), 10)
        
        set_count2(20)
        self.assertEqual(count1(), 5)
        self.assertEqual(count2(), 20)
        
        # Test in all_states
        all_states = get_all_states()
        self.assertEqual(all_states["count1"], 5)
        self.assertEqual(all_states["count2"], 20)
    
    def test_thread_safety(self):
        """Test thread safety of state operations."""
        count, set_count = use_state(0)
        
        def increment():
            for _ in range(100):
                set_count(count() + 1)
        
        # Run multiple threads
        threads = [threading.Thread(target=increment) for _ in range(5)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have incremented 500 times
        self.assertEqual(count(), 500)
    
    def test_callback_error_handling(self):
        """Test that callback errors don't break state updates."""
        def bad_callback(old_value, new_value):
            raise ValueError("Test error")
        
        count, set_count = use_state(0, on_change=bad_callback)
        
        # Should not raise an exception
        set_count(5)
        self.assertEqual(count(), 5)

class TestStateManager(unittest.TestCase):
    """Test the StateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = StateManager()
    
    def test_create_state(self):
        """Test state creation."""
        getter, setter = self.manager.create_state(42)
        
        self.assertEqual(getter(), 42)
        
        setter(100)
        self.assertEqual(getter(), 100)
    
    def test_get_all_states(self):
        """Test getting all states."""
        self.manager.create_state(1, "state1")
        self.manager.create_state(2, "state2")
        
        all_states = self.manager.get_all_states()
        self.assertEqual(all_states["state1"], 1)
        self.assertEqual(all_states["state2"], 2)
    
    def test_remove_state(self):
        """Test removing a state."""
        self.manager.create_state(42, "test_state")
        
        # Verify state exists
        self.assertIn("test_state", self.manager.get_all_states())
        
        # Remove state
        self.manager.remove_state("test_state")
        
        # Verify state is gone
        self.assertNotIn("test_state", self.manager.get_all_states())
    
    def test_clear_all_states(self):
        """Test clearing all states."""
        self.manager.create_state(1, "state1")
        self.manager.create_state(2, "state2")
        
        # Verify states exist
        self.assertEqual(len(self.manager.get_all_states()), 2)
        
        # Clear all
        self.manager.clear_all_states()
        
        # Verify all states are gone
        self.assertEqual(len(self.manager.get_all_states()), 0)

class TestStateContext(unittest.TestCase):
    """Test the StateContext class."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
    
    def test_context_creation(self):
        """Test context creation and usage."""
        ctx = create_context("test_context")
        
        self.assertEqual(ctx.name, "test_context")
        self.assertFalse(ctx._active)
    
    def test_context_manager(self):
        """Test using context as context manager."""
        with create_context("test") as ctx:
            self.assertTrue(ctx._active)
            
            # Create state within context
            count, set_count = ctx.use_state(0)
            set_count(42)
            
            # Verify state
            self.assertEqual(count(), 42)
            
            # Verify context has the state
            ctx_states = ctx.get_all_states()
            self.assertEqual(len(ctx_states), 1)
    
    def test_context_isolation(self):
        """Test that contexts are isolated."""
        with create_context("ctx1") as ctx1:
            count1, set_count1 = ctx1.use_state(10)
            
            with create_context("ctx2") as ctx2:
                count2, set_count2 = ctx2.use_state(20)
                
                # Both states should exist independently
                self.assertEqual(count1(), 10)
                self.assertEqual(count2(), 20)
                
                # Contexts should have different states
                self.assertEqual(len(ctx1.get_all_states()), 1)
                self.assertEqual(len(ctx2.get_all_states()), 1)
    
    def test_context_clearing(self):
        """Test clearing context states."""
        with create_context("test") as ctx:
            ctx.use_state(1)
            ctx.use_state(2)
            
            # Verify states exist
            self.assertEqual(len(ctx.get_all_states()), 2)
            
            # Clear states
            ctx.clear_states()
            
            # Verify states are gone
            self.assertEqual(len(ctx.get_all_states()), 0)

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
    
    def test_get_all_states(self):
        """Test get_all_states function."""
        # Create some states
        use_state(1, state_id="state1")
        use_state(2, state_id="state2")
        
        all_states = get_all_states()
        
        self.assertEqual(all_states["state1"], 1)
        self.assertEqual(all_states["state2"], 2)
    
    def test_clear_all_states(self):
        """Test clear_all_states function."""
        # Create some states
        use_state(1, state_id="state1")
        use_state(2, state_id="state2")
        
        # Verify states exist
        self.assertEqual(len(get_all_states()), 2)
        
        # Clear all states
        clear_all_states()
        
        # Verify states are gone
        self.assertEqual(len(get_all_states()), 0)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
    
    def test_none_initial_value(self):
        """Test using None as initial value."""
        value, set_value = use_state(None)
        
        self.assertIsNone(value())
        
        set_value("not none")
        self.assertEqual(value(), "not none")
        
        set_value(None)
        self.assertIsNone(value())
    
    def test_mutable_state_references(self):
        """Test that mutable state values are handled correctly."""
        original_list = [1, 2, 3]
        items, set_items = use_state(original_list)
        
        # Modifying the original list should not affect the state
        original_list.append(4)
        self.assertEqual(items(), [1, 2, 3])
        
        # Setting a new list should work
        set_items([5, 6, 7])
        self.assertEqual(items(), [5, 6, 7])
    
    def test_rapid_state_changes(self):
        """Test rapid state changes."""
        count, set_count = use_state(0)
        
        # Rapid changes
        for i in range(100):
            set_count(i)
        
        self.assertEqual(count(), 99)
    
    def test_callback_with_multiple_parameters(self):
        """Test callbacks with proper parameter passing."""
        callback_data = []
        
        def callback(old, new):
            callback_data.append({
                'old': old,
                'new': new,
                'old_type': type(old),
                'new_type': type(new)
            })
        
        value, set_value = use_state(0, on_change=callback)
        
        set_value("string")
        set_value([1, 2, 3])
        set_value({'key': 'value'})
        
        self.assertEqual(len(callback_data), 3)
        self.assertEqual(callback_data[0]['old'], 0)
        self.assertEqual(callback_data[0]['new'], "string")
        self.assertEqual(callback_data[1]['old'], "string")
        self.assertEqual(callback_data[1]['new'], [1, 2, 3])

if __name__ == '__main__':
    unittest.main()