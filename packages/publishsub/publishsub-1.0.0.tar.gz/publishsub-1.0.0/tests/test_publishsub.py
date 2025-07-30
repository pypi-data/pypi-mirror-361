#!/usr/bin/env python3
"""
Unit tests for publishsub library
"""

import unittest
import threading
import time
import weakref
from unittest.mock import Mock, patch

# Import from the publishsub library
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from publishsub import PubSub, subscribe, unsubscribe, publish, clear, subscribers_count, list_events

class TestPubSub(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.pubsub = PubSub()
        # Clear global instance
        clear()
    
    def tearDown(self):
        """Clean up after each test method."""
        clear()
    
    def test_basic_subscribe_publish(self):
        """Test basic subscribe and publish functionality"""
        received_data = []
        
        def handler(data):
            received_data.append(data)
        
        # Subscribe to event
        sub_id = self.pubsub.subscribe("test_event", handler)
        self.assertIsInstance(sub_id, str)
        
        # Publish event
        count = self.pubsub.publish("test_event", "test_data")
        self.assertEqual(count, 1)
        self.assertEqual(received_data, ["test_data"])
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers for the same event"""
        received_data1 = []
        received_data2 = []
        
        def handler1(data):
            received_data1.append(data)
        
        def handler2(data):
            received_data2.append(data)
        
        # Subscribe multiple handlers
        sub1 = self.pubsub.subscribe("test_event", handler1)
        sub2 = self.pubsub.subscribe("test_event", handler2)
        
        # Publish event
        count = self.pubsub.publish("test_event", "test_data")
        self.assertEqual(count, 2)
        self.assertEqual(received_data1, ["test_data"])
        self.assertEqual(received_data2, ["test_data"])
    
    def test_unsubscribe(self):
        """Test unsubscribe functionality"""
        received_data = []
        
        def handler(data):
            received_data.append(data)
        
        # Subscribe and unsubscribe
        sub_id = self.pubsub.subscribe("test_event", handler)
        result = self.pubsub.unsubscribe("test_event", sub_id)
        self.assertTrue(result)
        
        # Publish should not reach handler
        count = self.pubsub.publish("test_event", "test_data")
        self.assertEqual(count, 0)
        self.assertEqual(received_data, [])
    
    def test_unsubscribe_invalid(self):
        """Test unsubscribe with invalid subscription ID"""
        result = self.pubsub.unsubscribe("test_event", "invalid_id")
        self.assertFalse(result)
    
    def test_publish_no_subscribers(self):
        """Test publishing to event with no subscribers"""
        count = self.pubsub.publish("nonexistent_event", "data")
        self.assertEqual(count, 0)
    
    def test_subscribers_count(self):
        """Test subscribers count functionality"""
        def handler1(data): pass
        def handler2(data): pass
        
        # Initially no subscribers
        self.assertEqual(self.pubsub.subscribers_count("test_event"), 0)
        
        # Add subscribers
        sub1 = self.pubsub.subscribe("test_event", handler1)
        self.assertEqual(self.pubsub.subscribers_count("test_event"), 1)
        
        sub2 = self.pubsub.subscribe("test_event", handler2)
        self.assertEqual(self.pubsub.subscribers_count("test_event"), 2)
        
        # Remove subscriber
        self.pubsub.unsubscribe("test_event", sub1)
        self.assertEqual(self.pubsub.subscribers_count("test_event"), 1)
    
    def test_list_events(self):
        """Test list events functionality"""
        def handler(data): pass
        
        # Initially no events
        self.assertEqual(self.pubsub.list_events(), [])
        
        # Add events
        self.pubsub.subscribe("event1", handler)
        self.pubsub.subscribe("event2", handler)
        
        events = self.pubsub.list_events()
        self.assertEqual(set(events), {"event1", "event2"})
    
    def test_clear_specific_event(self):
        """Test clearing specific event"""
        def handler(data): pass
        
        self.pubsub.subscribe("event1", handler)
        self.pubsub.subscribe("event2", handler)
        
        # Clear specific event
        self.pubsub.clear("event1")
        
        events = self.pubsub.list_events()
        self.assertEqual(events, ["event2"])
    
    def test_clear_all_events(self):
        """Test clearing all events"""
        def handler(data): pass
        
        self.pubsub.subscribe("event1", handler)
        self.pubsub.subscribe("event2", handler)
        
        # Clear all events
        self.pubsub.clear()
        
        events = self.pubsub.list_events()
        self.assertEqual(events, [])
    
    def test_weak_references(self):
        """Test that weak references work correctly"""
        received_data = []
        
        class TestHandler:
            def __call__(self, data):
                received_data.append(data)
        
        # Create handler object
        handler = TestHandler()
        sub_id = self.pubsub.subscribe("test_event", handler)
        
        # Publish event - should work
        count = self.pubsub.publish("test_event", "test_data")
        self.assertEqual(count, 1)
        self.assertEqual(received_data, ["test_data"])
        
        # Delete handler reference
        del handler
        
        # Publish again - weak reference should be cleaned up
        count = self.pubsub.publish("test_event", "test_data2")
        self.assertEqual(count, 0)  # Handler was garbage collected
    
    def test_thread_safety(self):
        """Test thread safety of the pub/sub system"""
        received_data = []
        lock = threading.Lock()
        
        def handler(data):
            with lock:
                received_data.append(data)
        
        # Subscribe from main thread
        sub_id = self.pubsub.subscribe("test_event", handler)
        
        # Publish from multiple threads
        def publish_worker(worker_id):
            for i in range(10):
                self.pubsub.publish("test_event", f"worker_{worker_id}_msg_{i}")
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=publish_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check that all messages were received
        self.assertEqual(len(received_data), 50)  # 5 workers * 10 messages each
    
    def test_error_handling_in_callback(self):
        """Test that errors in callbacks don't break the system"""
        received_data = []
        
        def good_handler(data):
            received_data.append(data)
        
        def bad_handler(data):
            raise ValueError("Test error")
        
        # Subscribe both handlers
        self.pubsub.subscribe("test_event", good_handler)
        self.pubsub.subscribe("test_event", bad_handler)
        
        # Publish event - should not raise exception
        count = self.pubsub.publish("test_event", "test_data")
        self.assertEqual(count, 2)  # Both handlers were called
        self.assertEqual(received_data, ["test_data"])  # Good handler worked
    
    def test_global_instance_functions(self):
        """Test global instance functions"""
        received_data = []
        
        def handler(data):
            received_data.append(data)
        
        # Use global functions
        sub_id = subscribe("global_event", handler)
        count = publish("global_event", "global_data")
        
        self.assertEqual(count, 1)
        self.assertEqual(received_data, ["global_data"])
        
        # Test other global functions
        self.assertEqual(subscribers_count("global_event"), 1)
        self.assertIn("global_event", list_events())
        
        # Unsubscribe
        result = unsubscribe("global_event", sub_id)
        self.assertTrue(result)
        self.assertEqual(subscribers_count("global_event"), 0)
    
    def test_publish_with_none_data(self):
        """Test publishing with None data"""
        received_data = []
        
        def handler(data):
            received_data.append(data)
        
        self.pubsub.subscribe("test_event", handler)
        
        # Publish with None data
        count = self.pubsub.publish("test_event", None)
        self.assertEqual(count, 1)
        self.assertEqual(received_data, [None])
        
        # Publish with no data argument
        count = self.pubsub.publish("test_event")
        self.assertEqual(count, 1)
        self.assertEqual(received_data, [None, None])
    
    def test_debug_mode(self):
        """Test debug mode functionality"""
        with patch('builtins.print') as mock_print:
            self.pubsub.enable_debug(True)
            
            def handler(data): pass
            
            # Subscribe should log
            sub_id = self.pubsub.subscribe("test_event", handler)
            self.assertTrue(any("Subscribed to" in str(call) for call in mock_print.call_args_list))
            
            # Publish should log
            mock_print.reset_mock()
            self.pubsub.publish("test_event", "data")
            self.assertTrue(any("Publishing" in str(call) for call in mock_print.call_args_list))
            
            # Unsubscribe should log
            mock_print.reset_mock()
            self.pubsub.unsubscribe("test_event", sub_id)
            self.assertTrue(any("Unsubscribed from" in str(call) for call in mock_print.call_args_list))

if __name__ == '__main__':
    unittest.main()