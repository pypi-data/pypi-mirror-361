#!/usr/bin/env python3
"""
Test suite for stateen.debugging module.

This module contains comprehensive tests for the debugging functionality
of the Stateen library.
"""

import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, StringIO
import sys

from stateen.debugging import (
    debug_state, get_debugger, StateDebugger, StateChangeEvent,
    debug_context, print_state_info, create_state_monitor
)
from stateen.core import use_state, clear_all_states

class TestStateChangeEvent(unittest.TestCase):
    """Test the StateChangeEvent class."""
    
    def test_basic_event_creation(self):
        """Test basic event creation."""
        event = StateChangeEvent("test_state", "old_value", "new_value")
        
        self.assertEqual(event.state_id, "test_state")
        self.assertEqual(event.old_value, "old_value")
        self.assertEqual(event.new_value, "new_value")
        self.assertIsInstance(event.timestamp, datetime)
        self.assertIsInstance(event.thread_id, str)
    
    def test_event_to_dict(self):
        """Test event serialization to dictionary."""
        event = StateChangeEvent("test_state", 1, 2)
        event_dict = event.to_dict()
        
        self.assertEqual(event_dict["state_id"], "test_state")
        self.assertEqual(event_dict["old_value"], 1)
        self.assertEqual(event_dict["new_value"], 2)
        self.assertIn("timestamp", event_dict)
        self.assertIn("thread_id", event_dict)

class TestStateDebugger(unittest.TestCase):
    """Test the StateDebugger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.debugger = StateDebugger()
        self.debugger.enable()
    
    def tearDown(self):
        """Clean up after tests."""
        self.debugger.clear_events()
    
    def test_enable_disable(self):
        """Test enabling and disabling debugger."""
        self.debugger.enable()
        self.assertTrue(self.debugger.enabled)
        
        self.debugger.disable()
        self.assertFalse(self.debugger.enabled)
    
    def test_log_change(self):
        """Test logging state changes."""
        # Log a change
        self.debugger.log_change("test_state", "old", "new")
        
        events = self.debugger.get_events()
        self.assertEqual(len(events), 1)
        
        event = events[0]
        self.assertEqual(event.state_id, "test_state")
        self.assertEqual(event.old_value, "old")
        self.assertEqual(event.new_value, "new")
    
    def test_log_change_disabled(self):
        """Test that logging is disabled when debugger is disabled."""
        self.debugger.disable()
        
        # Log a change
        self.debugger.log_change("test_state", "old", "new")
        
        events = self.debugger.get_events()
        self.assertEqual(len(events), 0)
    
    def test_get_events_with_filters(self):
        """Test getting events with filters."""
        # Log multiple changes
        self.debugger.log_change("state1", "old1", "new1")
        self.debugger.log_change("state2", "old2", "new2")
        self.debugger.log_change("state1", "new1", "newer1")
        
        # Get all events
        all_events = self.debugger.get_events()
        self.assertEqual(len(all_events), 3)
        
        # Get events for specific state
        state1_events = self.debugger.get_events(state_id="state1")
        self.assertEqual(len(state1_events), 2)
        
        # Get events with limit
        limited_events = self.debugger.get_events(limit=2)
        self.assertEqual(len(limited_events), 2)
    
    def test_get_events_with_time_filter(self):
        """Test getting events with time filter."""
        import time
        
        # Log first change
        self.debugger.log_change("state1", "old1", "new1")
        
        # Wait a bit
        time.sleep(0.1)
        since_time = datetime.now()
        time.sleep(0.1)
        
        # Log second change
        self.debugger.log_change("state2", "old2", "new2")
        
        # Get events since specific time
        recent_events = self.debugger.get_events(since=since_time)
        self.assertEqual(len(recent_events), 1)
        self.assertEqual(recent_events[0].state_id, "state2")
    
    def test_get_state_history(self):
        """Test getting state history."""
        # Log changes for specific state
        self.debugger.log_change("counter", 0, 1)
        self.debugger.log_change("counter", 1, 2)
        self.debugger.log_change("other", "a", "b")
        
        # Get history for counter
        history = self.debugger.get_state_history("counter")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].old_value, 0)
        self.assertEqual(history[1].old_value, 1)
    
    def test_clear_events(self):
        """Test clearing events."""
        # Log some changes
        self.debugger.log_change("state1", "old", "new")
        self.debugger.log_change("state2", "old", "new")
        
        # Verify events exist
        events = self.debugger.get_events()
        self.assertEqual(len(events), 2)
        
        # Clear events
        self.debugger.clear_events()
        
        # Verify events are cleared
        events = self.debugger.get_events()
        self.assertEqual(len(events), 0)
    
    def test_add_filter(self):
        """Test adding event filters."""
        # Add filter for specific state
        def state_filter(event):
            return event.state_id == "important"
        
        self.debugger.add_filter(state_filter)
        
        # Log changes
        self.debugger.log_change("important", "old", "new")
        self.debugger.log_change("unimportant", "old", "new")
        
        # Only filtered events should be logged
        events = self.debugger.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].state_id, "important")
    
    def test_add_listener(self):
        """Test adding event listeners."""
        listener_calls = []
        
        def listener(event):
            listener_calls.append(event)
        
        self.debugger.add_listener(listener)
        
        # Log a change
        self.debugger.log_change("test_state", "old", "new")
        
        # Listener should be called
        self.assertEqual(len(listener_calls), 1)
        self.assertEqual(listener_calls[0].state_id, "test_state")
    
    def test_remove_filter(self):
        """Test removing event filters."""
        def state_filter(event):
            return event.state_id == "important"
        
        self.debugger.add_filter(state_filter)
        
        # Log changes with filter
        self.debugger.log_change("important", "old", "new")
        self.debugger.log_change("unimportant", "old", "new")
        
        events = self.debugger.get_events()
        self.assertEqual(len(events), 1)
        
        # Remove filter
        self.debugger.remove_filter(state_filter)
        
        # Clear events and log again
        self.debugger.clear_events()
        self.debugger.log_change("important", "old", "new")
        self.debugger.log_change("unimportant", "old", "new")
        
        # Both events should be logged now
        events = self.debugger.get_events()
        self.assertEqual(len(events), 2)
    
    def test_remove_listener(self):
        """Test removing event listeners."""
        listener_calls = []
        
        def listener(event):
            listener_calls.append(event)
        
        self.debugger.add_listener(listener)
        
        # Log a change
        self.debugger.log_change("test_state", "old", "new")
        self.assertEqual(len(listener_calls), 1)
        
        # Remove listener
        self.debugger.remove_listener(listener)
        
        # Log another change
        self.debugger.log_change("test_state", "new", "newer")
        
        # Listener should not be called again
        self.assertEqual(len(listener_calls), 1)
    
    def test_get_statistics(self):
        """Test getting statistics."""
        # Log some changes
        self.debugger.log_change("state1", "old1", "new1")
        self.debugger.log_change("state2", "old2", "new2")
        self.debugger.log_change("state1", "new1", "newer1")
        
        # Get statistics
        stats = self.debugger.get_statistics()
        
        self.assertEqual(stats["total_events"], 3)
        self.assertEqual(stats["state_counts"]["state1"], 2)
        self.assertEqual(stats["state_counts"]["state2"], 1)
        self.assertEqual(stats["most_changed_state"], "state1")
        self.assertIn("first_event", stats)
        self.assertIn("last_event", stats)
    
    def test_get_statistics_empty(self):
        """Test getting statistics with no events."""
        stats = self.debugger.get_statistics()
        
        self.assertEqual(stats["total_events"], 0)
    
    def test_export_events(self):
        """Test exporting events to JSON."""
        import tempfile
        import json
        
        # Log some changes
        self.debugger.log_change("state1", "old1", "new1")
        self.debugger.log_change("state2", "old2", "new2")
        
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            self.debugger.export_events(temp_file)
            
            # Load and verify exported data
            with open(temp_file, 'r') as f:
                exported_data = json.load(f)
            
            self.assertEqual(len(exported_data), 2)
            self.assertEqual(exported_data[0]["state_id"], "state1")
            self.assertEqual(exported_data[1]["state_id"], "state2")
        
        finally:
            import os
            os.unlink(temp_file)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_events(self, mock_stdout):
        """Test printing events."""
        # Log some changes
        self.debugger.log_change("counter", 0, 1)
        self.debugger.log_change("counter", 1, 2)
        
        # Print events
        self.debugger.print_events()
        
        output = mock_stdout.getvalue()
        self.assertIn("State Change Events", output)
        self.assertIn("counter", output)
        self.assertIn("0 -> 1", output)
        self.assertIn("1 -> 2", output)
    
    def test_listener_error_handling(self):
        """Test that listener errors are handled gracefully."""
        def bad_listener(event):
            raise ValueError("Test error")
        
        self.debugger.add_listener(bad_listener)
        
        # Should not raise an exception
        self.debugger.log_change("test_state", "old", "new")
        
        # Event should still be logged
        events = self.debugger.get_events()
        self.assertEqual(len(events), 1)

class TestDebugFunctions(unittest.TestCase):
    """Test debug utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
    
    def test_debug_state_enable(self):
        """Test debug_state function."""
        debugger = debug_state(True)
        
        self.assertIsInstance(debugger, StateDebugger)
        self.assertTrue(debugger.enabled)
        
        # Disable
        debugger2 = debug_state(False)
        self.assertFalse(debugger2.enabled)
        
        # Should be same instance
        self.assertIs(debugger, debugger2)
    
    def test_get_debugger(self):
        """Test get_debugger function."""
        debugger = get_debugger()
        
        self.assertIsInstance(debugger, StateDebugger)
        
        # Should be same instance as debug_state returns
        debugger2 = debug_state(True)
        self.assertIs(debugger, debugger2)
    
    def test_debug_context(self):
        """Test debug_context context manager."""
        # Get original state
        original_state = get_debugger().enabled
        
        # Use context with debugging enabled
        with debug_context(True) as debugger:
            self.assertTrue(debugger.enabled)
            
            # Log a change
            debugger.log_change("test", "old", "new")
            events = debugger.get_events()
            self.assertEqual(len(events), 1)
        
        # Should restore original state
        self.assertEqual(get_debugger().enabled, original_state)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_state_info(self, mock_stdout):
        """Test print_state_info function."""
        # Create some states
        count, set_count = use_state(42, state_id="counter")
        name, set_name = use_state("John", state_id="name")
        
        # Print state info
        print_state_info()
        
        output = mock_stdout.getvalue()
        self.assertIn("Current State Information", output)
        self.assertIn("counter: 42", output)
        self.assertIn("name: John", output)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_state_info_empty(self, mock_stdout):
        """Test print_state_info with no states."""
        print_state_info()
        
        output = mock_stdout.getvalue()
        self.assertIn("No states found", output)
    
    def test_create_state_monitor(self):
        """Test create_state_monitor function."""
        monitor_calls = []
        
        def callback(old, new):
            monitor_calls.append((old, new))
        
        # Create monitor
        monitor = create_state_monitor("test_state", callback)
        
        # Should have filter and listener
        self.assertIn('filter', monitor)
        self.assertIn('listener', monitor)
        self.assertIn('remove', monitor)
        
        # Enable debugging
        debug_state(True)
        
        # Log a change for monitored state
        debugger = get_debugger()
        debugger.log_change("test_state", "old", "new")
        
        # Callback should be called
        self.assertEqual(len(monitor_calls), 1)
        self.assertEqual(monitor_calls[0], ("old", "new"))
        
        # Log a change for different state
        debugger.log_change("other_state", "old", "new")
        
        # Callback should not be called
        self.assertEqual(len(monitor_calls), 1)
        
        # Remove monitor
        monitor['remove']()
        
        # Log another change for monitored state
        debugger.log_change("test_state", "new", "newer")
        
        # Callback should not be called
        self.assertEqual(len(monitor_calls), 1)
    
    def test_create_state_monitor_default_callback(self):
        """Test create_state_monitor with default callback."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Create monitor without callback
            monitor = create_state_monitor("test_state")
            
            # Enable debugging
            debug_state(True)
            
            # Log a change
            debugger = get_debugger()
            debugger.log_change("test_state", "old", "new")
            
            # Should print to stdout
            output = mock_stdout.getvalue()
            self.assertIn("[MONITOR] test_state: old -> new", output)
            
            # Clean up
            monitor['remove']()

class TestDebuggingIntegration(unittest.TestCase):
    """Test debugging integration with state management."""
    
    def setUp(self):
        """Set up test fixtures."""
        clear_all_states()
        debug_state(True)
        get_debugger().clear_events()
    
    def tearDown(self):
        """Clean up after tests."""
        clear_all_states()
        get_debugger().clear_events()
    
    def test_debugging_with_use_state(self):
        """Test debugging integration with use_state."""
        # Create state with callback that triggers debugging
        def on_change(old, new):
            get_debugger().log_change("counter", old, new)
        
        count, set_count = use_state(0, state_id="counter", on_change=on_change)
        
        # Update state
        set_count(1)
        set_count(2)
        
        # Check debug events
        events = get_debugger().get_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].old_value, 0)
        self.assertEqual(events[0].new_value, 1)
        self.assertEqual(events[1].old_value, 1)
        self.assertEqual(events[1].new_value, 2)
    
    def test_debugging_with_multiple_states(self):
        """Test debugging with multiple states."""
        def make_debug_callback(state_name):
            def callback(old, new):
                get_debugger().log_change(state_name, old, new)
            return callback
        
        # Create multiple states
        count, set_count = use_state(0, on_change=make_debug_callback("counter"))
        name, set_name = use_state("John", on_change=make_debug_callback("name"))
        
        # Update states
        set_count(5)
        set_name("Jane")
        set_count(10)
        
        # Check debug events
        events = get_debugger().get_events()
        self.assertEqual(len(events), 3)
        
        # Check specific state history
        counter_history = get_debugger().get_state_history("counter")
        self.assertEqual(len(counter_history), 2)
        
        name_history = get_debugger().get_state_history("name")
        self.assertEqual(len(name_history), 1)

if __name__ == '__main__':
    unittest.main()