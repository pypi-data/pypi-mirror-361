#!/usr/bin/env python3
"""
Test suite for stateen.persistence module.

This module contains comprehensive tests for the persistence functionality
of the Stateen library.
"""

import unittest
import tempfile
import shutil
import os
import json
import pickle
from pathlib import Path

from stateen.persistence import (
    use_persistent_state, StatePersistence, save_state_to_file, 
    load_state_from_file, clear_persistent_state, 
    list_persistent_states, clear_all_persistent_states,
    get_default_persistence
)
from stateen.core import clear_all_states

class TestStatePersistence(unittest.TestCase):
    """Test the StatePersistence class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = StatePersistence(self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_json(self):
        """Test saving and loading JSON data."""
        test_data = {"name": "John", "age": 30, "active": True}
        
        # Save data
        self.persistence.save_state("user", test_data, "json")
        
        # Load data
        loaded_data = self.persistence.load_state("user", format="json")
        
        self.assertEqual(loaded_data, test_data)
    
    def test_save_and_load_pickle(self):
        """Test saving and loading pickle data."""
        test_data = {"name": "John", "numbers": [1, 2, 3], "nested": {"key": "value"}}
        
        # Save data
        self.persistence.save_state("user", test_data, "pickle")
        
        # Load data
        loaded_data = self.persistence.load_state("user", format="pickle")
        
        self.assertEqual(loaded_data, test_data)
    
    def test_load_nonexistent_state(self):
        """Test loading a state that doesn't exist."""
        default_value = "default"
        
        loaded_data = self.persistence.load_state("nonexistent", default_value)
        
        self.assertEqual(loaded_data, default_value)
    
    def test_delete_state(self):
        """Test deleting a state."""
        test_data = {"test": "data"}
        
        # Save data
        self.persistence.save_state("test", test_data)
        
        # Verify it exists
        loaded_data = self.persistence.load_state("test")
        self.assertEqual(loaded_data, test_data)
        
        # Delete it
        self.persistence.delete_state("test")
        
        # Verify it's gone
        loaded_data = self.persistence.load_state("test", "default")
        self.assertEqual(loaded_data, "default")
    
    def test_list_states(self):
        """Test listing all states."""
        # Save multiple states
        self.persistence.save_state("state1", "data1")
        self.persistence.save_state("state2", "data2")
        self.persistence.save_state("state3", "data3")
        
        # List states
        states = self.persistence.list_states()
        
        self.assertEqual(len(states), 3)
        self.assertIn("state1", states)
        self.assertIn("state2", states)
        self.assertIn("state3", states)
    
    def test_clear_all_states(self):
        """Test clearing all states."""
        # Save multiple states
        self.persistence.save_state("state1", "data1")
        self.persistence.save_state("state2", "data2")
        
        # Verify states exist
        states = self.persistence.list_states()
        self.assertEqual(len(states), 2)
        
        # Clear all states
        self.persistence.clear_all_states()
        
        # Verify all states are gone
        states = self.persistence.list_states()
        self.assertEqual(len(states), 0)
    
    def test_invalid_format(self):
        """Test using an invalid format."""
        with self.assertRaises(ValueError):
            self.persistence.save_state("test", "data", "invalid_format")
        
        with self.assertRaises(ValueError):
            self.persistence.load_state("test", format="invalid_format")
    
    def test_json_serialization_error(self):
        """Test JSON serialization error handling."""
        # Create non-serializable object
        class NonSerializable:
            pass
        
        non_serializable = NonSerializable()
        
        # Should handle the error gracefully
        self.persistence.save_state("test", non_serializable, "json")
        
        # Should return default value
        loaded_data = self.persistence.load_state("test", "default", "json")
        self.assertEqual(loaded_data, "default")

class TestUsePersistentState(unittest.TestCase):
    """Test the use_persistent_state function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
        clear_all_states()
    
    def test_basic_persistent_state(self):
        """Test basic persistent state functionality."""
        # Create persistent state
        count, set_count = use_persistent_state(0, "counter", self.temp_dir)
        
        # Test initial value
        self.assertEqual(count(), 0)
        
        # Update value
        set_count(42)
        self.assertEqual(count(), 42)
        
        # Create new instance with same ID - should load persisted value
        count2, set_count2 = use_persistent_state(999, "counter", self.temp_dir)
        self.assertEqual(count2(), 42)  # Should load persisted value, not default
    
    def test_persistent_state_with_callback(self):
        """Test persistent state with callback."""
        callback_calls = []
        
        def on_change(old_value, new_value):
            callback_calls.append((old_value, new_value))
        
        count, set_count = use_persistent_state(
            0, "counter", self.temp_dir, on_change=on_change
        )
        
        # Update value
        set_count(5)
        
        # Verify callback was called
        self.assertEqual(len(callback_calls), 1)
        self.assertEqual(callback_calls[0], (0, 5))
    
    def test_persistent_state_no_auto_save(self):
        """Test persistent state with auto_save=False."""
        count, set_count = use_persistent_state(
            0, "counter", self.temp_dir, auto_save=False
        )
        
        # Update value
        set_count(42)
        
        # Create new instance - should not load persisted value
        count2, set_count2 = use_persistent_state(999, "counter", self.temp_dir)
        self.assertEqual(count2(), 999)  # Should use default, not persisted
    
    def test_persistent_state_pickle_format(self):
        """Test persistent state with pickle format."""
        test_data = {"name": "John", "items": [1, 2, 3]}
        
        user, set_user = use_persistent_state(
            {}, "user", self.temp_dir, format="pickle"
        )
        
        # Update value
        set_user(test_data)
        
        # Create new instance - should load persisted value
        user2, set_user2 = use_persistent_state(
            {}, "user", self.temp_dir, format="pickle"
        )
        self.assertEqual(user2(), test_data)
    
    def test_persistent_state_different_storage_paths(self):
        """Test persistent state with different storage paths."""
        temp_dir2 = tempfile.mkdtemp()
        
        try:
            # Create states in different paths
            count1, set_count1 = use_persistent_state(0, "counter", self.temp_dir)
            count2, set_count2 = use_persistent_state(0, "counter", temp_dir2)
            
            # Update values
            set_count1(10)
            set_count2(20)
            
            # Values should be independent
            self.assertEqual(count1(), 10)
            self.assertEqual(count2(), 20)
            
            # Create new instances in same paths
            count1_new, _ = use_persistent_state(999, "counter", self.temp_dir)
            count2_new, _ = use_persistent_state(999, "counter", temp_dir2)
            
            # Should load respective persisted values
            self.assertEqual(count1_new(), 10)
            self.assertEqual(count2_new(), 20)
        
        finally:
            shutil.rmtree(temp_dir2)

class TestPersistenceUtilities(unittest.TestCase):
    """Test persistence utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
        clear_all_states()
    
    def test_save_and_load_state_to_file(self):
        """Test save_state_to_file and load_state_from_file."""
        test_data = {"name": "John", "age": 30}
        file_path = os.path.join(self.temp_dir, "test_state.json")
        
        # Save to file
        save_state_to_file("test", test_data, file_path)
        
        # Load from file
        loaded_data = load_state_from_file(file_path)
        
        self.assertEqual(loaded_data, test_data)
    
    def test_clear_persistent_state(self):
        """Test clear_persistent_state function."""
        # Create persistent state
        count, set_count = use_persistent_state(0, "counter", self.temp_dir)
        set_count(42)
        
        # Verify it's persisted
        count2, _ = use_persistent_state(999, "counter", self.temp_dir)
        self.assertEqual(count2(), 42)
        
        # Clear persistent state
        clear_persistent_state("counter", self.temp_dir)
        
        # Verify it's cleared
        count3, _ = use_persistent_state(999, "counter", self.temp_dir)
        self.assertEqual(count3(), 999)  # Should use default
    
    def test_list_persistent_states(self):
        """Test list_persistent_states function."""
        # Create multiple persistent states
        use_persistent_state(1, "state1", self.temp_dir)
        use_persistent_state(2, "state2", self.temp_dir)
        use_persistent_state(3, "state3", self.temp_dir)
        
        # List states
        states = list_persistent_states(self.temp_dir)
        
        self.assertEqual(len(states), 3)
        self.assertIn("state1", states)
        self.assertIn("state2", states)
        self.assertIn("state3", states)
    
    def test_clear_all_persistent_states(self):
        """Test clear_all_persistent_states function."""
        # Create multiple persistent states
        use_persistent_state(1, "state1", self.temp_dir)
        use_persistent_state(2, "state2", self.temp_dir)
        
        # Verify states exist
        states = list_persistent_states(self.temp_dir)
        self.assertEqual(len(states), 2)
        
        # Clear all persistent states
        clear_all_persistent_states(self.temp_dir)
        
        # Verify all states are cleared
        states = list_persistent_states(self.temp_dir)
        self.assertEqual(len(states), 0)
    
    def test_get_default_persistence(self):
        """Test get_default_persistence function."""
        persistence = get_default_persistence()
        
        self.assertIsInstance(persistence, StatePersistence)
        
        # Test that it works
        persistence.save_state("test", "data")
        loaded = persistence.load_state("test")
        self.assertEqual(loaded, "data")
        
        # Clean up
        persistence.delete_state("test")

class TestPersistenceIntegration(unittest.TestCase):
    """Test integration scenarios for persistence."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
        clear_all_states()
    
    def test_persistence_with_complex_data(self):
        """Test persistence with complex data structures."""
        complex_data = {
            "user": {
                "name": "John",
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                },
                "history": [
                    {"action": "login", "timestamp": "2023-01-01"},
                    {"action": "purchase", "timestamp": "2023-01-02"}
                ]
            },
            "settings": {
                "language": "en",
                "timezone": "UTC"
            }
        }
        
        app_state, set_app_state = use_persistent_state(
            {}, "app_state", self.temp_dir
        )
        
        # Set complex data
        set_app_state(complex_data)
        
        # Create new instance - should load complex data
        app_state2, _ = use_persistent_state({}, "app_state", self.temp_dir)
        
        self.assertEqual(app_state2(), complex_data)
        self.assertEqual(app_state2()["user"]["name"], "John")
        self.assertEqual(app_state2()["user"]["preferences"]["theme"], "dark")
        self.assertEqual(len(app_state2()["user"]["history"]), 2)
    
    def test_persistence_with_state_updates(self):
        """Test persistence with multiple state updates."""
        counter, set_counter = use_persistent_state(0, "counter", self.temp_dir)
        
        # Multiple updates
        for i in range(1, 6):
            set_counter(i)
        
        # Verify final value
        self.assertEqual(counter(), 5)
        
        # Create new instance - should load latest value
        counter2, _ = use_persistent_state(999, "counter", self.temp_dir)
        self.assertEqual(counter2(), 5)
    
    def test_persistence_across_multiple_sessions(self):
        """Test persistence across multiple 'sessions'."""
        # Session 1
        todos, set_todos = use_persistent_state([], "todos", self.temp_dir)
        set_todos(["Task 1", "Task 2"])
        
        # Session 2 (simulate app restart)
        todos2, set_todos2 = use_persistent_state([], "todos", self.temp_dir)
        self.assertEqual(todos2(), ["Task 1", "Task 2"])
        
        # Add more todos
        current_todos = todos2()
        set_todos2(current_todos + ["Task 3"])
        
        # Session 3 (simulate another app restart)
        todos3, _ = use_persistent_state([], "todos", self.temp_dir)
        self.assertEqual(todos3(), ["Task 1", "Task 2", "Task 3"])
    
    def test_persistence_error_recovery(self):
        """Test persistence error recovery."""
        # Create a state
        data, set_data = use_persistent_state("initial", "data", self.temp_dir)
        set_data("updated")
        
        # Corrupt the persistence file
        persistence_file = Path(self.temp_dir) / "data.json"
        if persistence_file.exists():
            with open(persistence_file, 'w') as f:
                f.write("invalid json content")
        
        # Should fall back to default value
        data2, _ = use_persistent_state("fallback", "data", self.temp_dir)
        self.assertEqual(data2(), "fallback")

if __name__ == '__main__':
    unittest.main()