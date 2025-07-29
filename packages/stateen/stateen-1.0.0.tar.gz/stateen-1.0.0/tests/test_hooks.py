#!/usr/bin/env python3
"""
Test suite for stateen.hooks module.

This module contains comprehensive tests for the hooks functionality
including use_effect, use_memo, and use_callback.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch

from stateen.hooks import (
    use_effect, use_memo, use_callback,
    cleanup_effect, cleanup_all_effects,
    clear_memo, clear_all_memos,
    clear_callback, clear_all_callbacks,
    cleanup_all_hooks
)
from stateen.core import use_state, clear_all_states

class TestUseEffect(unittest.TestCase):
    """Test the use_effect hook."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
        cleanup_all_effects()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
        cleanup_all_effects()
    
    def test_basic_effect(self):
        """Test basic effect execution."""
        effect_calls = []
        
        def effect():
            effect_calls.append("effect called")
        
        use_effect(effect)
        
        # Effect should be called immediately
        self.assertEqual(len(effect_calls), 1)
    
    def test_effect_with_dependencies(self):
        """Test effect with dependencies."""
        effect_calls = []
        count, set_count = use_state(0)
        
        def effect():
            effect_calls.append(f"count is {count()}")
        
        # Effect with dependencies
        use_effect(effect, dependencies=[count()])
        self.assertEqual(len(effect_calls), 1)
        self.assertEqual(effect_calls[0], "count is 0")
        
        # Change dependency - should trigger effect
        set_count(1)
        use_effect(effect, dependencies=[count()])
        self.assertEqual(len(effect_calls), 2)
        self.assertEqual(effect_calls[1], "count is 1")
        
        # Same dependency - should not trigger effect
        use_effect(effect, dependencies=[count()])
        self.assertEqual(len(effect_calls), 2)  # No new call
    
    def test_effect_with_cleanup(self):
        """Test effect with cleanup function."""
        effect_calls = []
        cleanup_calls = []
        
        def cleanup():
            cleanup_calls.append("cleanup called")
        
        def effect():
            effect_calls.append("effect called")
            return cleanup
        
        # First effect
        use_effect(effect, effect_id="test_effect")
        self.assertEqual(len(effect_calls), 1)
        self.assertEqual(len(cleanup_calls), 0)
        
        # Second effect with same ID - should cleanup first
        use_effect(effect, effect_id="test_effect")
        self.assertEqual(len(effect_calls), 2)
        self.assertEqual(len(cleanup_calls), 1)
    
    def test_effect_cleanup_on_dependency_change(self):
        """Test that cleanup is called when dependencies change."""
        cleanup_calls = []
        count, set_count = use_state(0)
        
        def effect():
            def cleanup():
                cleanup_calls.append(f"cleanup for count {count()}")
            return cleanup
        
        # First effect
        use_effect(effect, dependencies=[count()], effect_id="counter_effect")
        self.assertEqual(len(cleanup_calls), 0)
        
        # Change dependency - should cleanup previous effect
        set_count(1)
        use_effect(effect, dependencies=[count()], effect_id="counter_effect")
        self.assertEqual(len(cleanup_calls), 1)
        self.assertEqual(cleanup_calls[0], "cleanup for count 0")
    
    def test_effect_error_handling(self):
        """Test that effect errors are handled gracefully."""
        def bad_effect():
            raise ValueError("Test error")
        
        # Should not raise an exception
        use_effect(bad_effect)
        
        # Should still work with other effects
        good_calls = []
        def good_effect():
            good_calls.append("good effect")
        
        use_effect(good_effect)
        self.assertEqual(len(good_calls), 1)
    
    def test_cleanup_effect(self):
        """Test cleanup_effect function."""
        cleanup_calls = []
        
        def effect():
            return lambda: cleanup_calls.append("cleaned up")
        
        use_effect(effect, effect_id="test_effect")
        
        # Cleanup specific effect
        cleanup_effect("test_effect")
        self.assertEqual(len(cleanup_calls), 1)
    
    def test_cleanup_all_effects(self):
        """Test cleanup_all_effects function."""
        cleanup_calls = []
        
        def make_effect(name):
            def effect():
                return lambda: cleanup_calls.append(f"cleaned up {name}")
            return effect
        
        use_effect(make_effect("effect1"), effect_id="effect1")
        use_effect(make_effect("effect2"), effect_id="effect2")
        
        # Cleanup all effects
        cleanup_all_effects()
        self.assertEqual(len(cleanup_calls), 2)
        self.assertIn("cleaned up effect1", cleanup_calls)
        self.assertIn("cleaned up effect2", cleanup_calls)

class TestUseMemo(unittest.TestCase):
    """Test the use_memo hook."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
        clear_all_memos()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
        clear_all_memos()
    
    def test_basic_memo(self):
        """Test basic memoization."""
        computation_calls = []
        
        def expensive_computation():
            computation_calls.append("computed")
            return 42
        
        # First call
        result1 = use_memo(expensive_computation)
        self.assertEqual(result1, 42)
        self.assertEqual(len(computation_calls), 1)
        
        # Second call with same memo_id - should use cached value
        result2 = use_memo(expensive_computation)
        self.assertEqual(result2, 42)
        self.assertEqual(len(computation_calls), 1)  # No new computation
    
    def test_memo_with_dependencies(self):
        """Test memo with dependencies."""
        computation_calls = []
        count, set_count = use_state(0)
        
        def compute():
            computation_calls.append(f"computed for {count()}")
            return count() * 2
        
        # First computation
        result1 = use_memo(compute, dependencies=[count()])
        self.assertEqual(result1, 0)
        self.assertEqual(len(computation_calls), 1)
        
        # Same dependencies - should use cached value
        result2 = use_memo(compute, dependencies=[count()])
        self.assertEqual(result2, 0)
        self.assertEqual(len(computation_calls), 1)  # No new computation
        
        # Change dependency - should recompute
        set_count(5)
        result3 = use_memo(compute, dependencies=[count()])
        self.assertEqual(result3, 10)
        self.assertEqual(len(computation_calls), 2)
    
    def test_memo_with_custom_id(self):
        """Test memo with custom memo_id."""
        computation_calls = []
        
        def compute1():
            computation_calls.append("compute1")
            return "result1"
        
        def compute2():
            computation_calls.append("compute2")
            return "result2"
        
        # Different memo IDs should be independent
        result1 = use_memo(compute1, memo_id="memo1")
        result2 = use_memo(compute2, memo_id="memo2")
        
        self.assertEqual(result1, "result1")
        self.assertEqual(result2, "result2")
        self.assertEqual(len(computation_calls), 2)
        
        # Same memo IDs should use cached values
        result1_cached = use_memo(compute1, memo_id="memo1")
        result2_cached = use_memo(compute2, memo_id="memo2")
        
        self.assertEqual(result1_cached, "result1")
        self.assertEqual(result2_cached, "result2")
        self.assertEqual(len(computation_calls), 2)  # No new computations
    
    def test_memo_error_handling(self):
        """Test memo error handling."""
        def bad_computation():
            raise ValueError("Test error")
        
        # Should raise the error
        with self.assertRaises(ValueError):
            use_memo(bad_computation)
    
    def test_memo_with_complex_dependencies(self):
        """Test memo with complex dependencies."""
        computation_calls = []
        user, set_user = use_state({"name": "John", "age": 30})
        
        def compute():
            computation_calls.append("computed")
            return f"{user()['name']} is {user()['age']} years old"
        
        # First computation
        result1 = use_memo(compute, dependencies=[user()])
        self.assertEqual(result1, "John is 30 years old")
        self.assertEqual(len(computation_calls), 1)
        
        # Same user - should use cached value
        result2 = use_memo(compute, dependencies=[user()])
        self.assertEqual(result2, "John is 30 years old")
        self.assertEqual(len(computation_calls), 1)
        
        # Change user - should recompute
        set_user({"name": "Jane", "age": 25})
        result3 = use_memo(compute, dependencies=[user()])
        self.assertEqual(result3, "Jane is 25 years old")
        self.assertEqual(len(computation_calls), 2)
    
    def test_clear_memo(self):
        """Test clear_memo function."""
        computation_calls = []
        
        def compute():
            computation_calls.append("computed")
            return 42
        
        # Compute and cache
        result1 = use_memo(compute, memo_id="test_memo")
        self.assertEqual(len(computation_calls), 1)
        
        # Clear memo
        clear_memo("test_memo")
        
        # Should recompute
        result2 = use_memo(compute, memo_id="test_memo")
        self.assertEqual(len(computation_calls), 2)
    
    def test_clear_all_memos(self):
        """Test clear_all_memos function."""
        computation_calls = []
        
        def make_compute(name):
            def compute():
                computation_calls.append(f"computed {name}")
                return name
            return compute
        
        # Create multiple memos
        use_memo(make_compute("memo1"), memo_id="memo1")
        use_memo(make_compute("memo2"), memo_id="memo2")
        self.assertEqual(len(computation_calls), 2)
        
        # Clear all memos
        clear_all_memos()
        
        # Should recompute both
        use_memo(make_compute("memo1"), memo_id="memo1")
        use_memo(make_compute("memo2"), memo_id="memo2")
        self.assertEqual(len(computation_calls), 4)

class TestUseCallback(unittest.TestCase):
    """Test the use_callback hook."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
        clear_all_callbacks()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
        clear_all_callbacks()
    
    def test_basic_callback(self):
        """Test basic callback memoization."""
        def callback():
            return "callback result"
        
        # First call
        memoized1 = use_callback(callback)
        self.assertEqual(memoized1(), "callback result")
        
        # Second call - should return same function object
        memoized2 = use_callback(callback)
        self.assertIs(memoized1, memoized2)
    
    def test_callback_with_dependencies(self):
        """Test callback with dependencies."""
        count, set_count = use_state(0)
        
        def callback():
            return f"count is {count()}"
        
        # First callback
        memoized1 = use_callback(callback, dependencies=[count()])
        self.assertEqual(memoized1(), "count is 0")
        
        # Same dependencies - should return same function
        memoized2 = use_callback(callback, dependencies=[count()])
        self.assertIs(memoized1, memoized2)
        
        # Change dependency - should return new function
        set_count(1)
        memoized3 = use_callback(callback, dependencies=[count()])
        self.assertIsNot(memoized1, memoized3)
        self.assertEqual(memoized3(), "count is 1")
    
    def test_callback_with_custom_id(self):
        """Test callback with custom callback_id."""
        def callback1():
            return "callback1"
        
        def callback2():
            return "callback2"
        
        # Different callback IDs should be independent
        memoized1 = use_callback(callback1, callback_id="cb1")
        memoized2 = use_callback(callback2, callback_id="cb2")
        
        self.assertEqual(memoized1(), "callback1")
        self.assertEqual(memoized2(), "callback2")
        
        # Same callback IDs should return cached functions
        memoized1_cached = use_callback(callback1, callback_id="cb1")
        memoized2_cached = use_callback(callback2, callback_id="cb2")
        
        self.assertIs(memoized1, memoized1_cached)
        self.assertIs(memoized2, memoized2_cached)
    
    def test_callback_with_parameters(self):
        """Test callback that takes parameters."""
        multiplier, set_multiplier = use_state(2)
        
        def callback(x):
            return x * multiplier()
        
        # First callback
        memoized1 = use_callback(callback, dependencies=[multiplier()])
        self.assertEqual(memoized1(5), 10)
        
        # Same dependencies - should return same function
        memoized2 = use_callback(callback, dependencies=[multiplier()])
        self.assertIs(memoized1, memoized2)
        
        # Change dependency - should return new function
        set_multiplier(3)
        memoized3 = use_callback(callback, dependencies=[multiplier()])
        self.assertIsNot(memoized1, memoized3)
        self.assertEqual(memoized3(5), 15)
    
    def test_clear_callback(self):
        """Test clear_callback function."""
        def callback():
            return "callback"
        
        # Create and cache callback
        memoized1 = use_callback(callback, callback_id="test_cb")
        
        # Clear callback
        clear_callback("test_cb")
        
        # Should create new callback
        memoized2 = use_callback(callback, callback_id="test_cb")
        self.assertIsNot(memoized1, memoized2)
    
    def test_clear_all_callbacks(self):
        """Test clear_all_callbacks function."""
        def callback1():
            return "callback1"
        
        def callback2():
            return "callback2"
        
        # Create callbacks
        memoized1 = use_callback(callback1, callback_id="cb1")
        memoized2 = use_callback(callback2, callback_id="cb2")
        
        # Clear all callbacks
        clear_all_callbacks()
        
        # Should create new callbacks
        new_memoized1 = use_callback(callback1, callback_id="cb1")
        new_memoized2 = use_callback(callback2, callback_id="cb2")
        
        self.assertIsNot(memoized1, new_memoized1)
        self.assertIsNot(memoized2, new_memoized2)

class TestHookIntegration(unittest.TestCase):
    """Test integration between different hooks."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
        cleanup_all_hooks()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
        cleanup_all_hooks()
    
    def test_effect_with_memo(self):
        """Test using use_effect with use_memo."""
        computation_calls = []
        effect_calls = []
        
        count, set_count = use_state(0)
        
        def expensive_computation():
            computation_calls.append("computed")
            return count() * count()
        
        def effect():
            square = use_memo(expensive_computation, dependencies=[count()])
            effect_calls.append(f"square of {count()} is {square}")
        
        # First effect
        use_effect(effect, dependencies=[count()])
        self.assertEqual(len(computation_calls), 1)
        self.assertEqual(len(effect_calls), 1)
        
        # Change count - should trigger effect and recompute memo
        set_count(3)
        use_effect(effect, dependencies=[count()])
        self.assertEqual(len(computation_calls), 2)
        self.assertEqual(len(effect_calls), 2)
        self.assertEqual(effect_calls[1], "square of 3 is 9")
    
    def test_callback_with_effect(self):
        """Test using use_callback with use_effect."""
        callback_calls = []
        effect_calls = []
        
        count, set_count = use_state(0)
        
        def increment():
            callback_calls.append("increment called")
            set_count(count() + 1)
        
        def effect():
            memoized_increment = use_callback(increment, dependencies=[count()])
            effect_calls.append(f"effect with count {count()}")
            return memoized_increment
        
        # First effect
        use_effect(effect, dependencies=[count()])
        self.assertEqual(len(effect_calls), 1)
    
    def test_cleanup_all_hooks(self):
        """Test cleanup_all_hooks function."""
        # Create various hooks
        use_effect(lambda: lambda: None, effect_id="effect1")
        use_memo(lambda: "memo", memo_id="memo1")
        use_callback(lambda: "callback", callback_id="callback1")
        
        # Cleanup all hooks
        cleanup_all_hooks()
        
        # All hooks should be cleared (this is mainly for cleanup, 
        # so we just verify no errors occur)
        self.assertTrue(True)  # If we get here, cleanup worked

if __name__ == '__main__':
    unittest.main()