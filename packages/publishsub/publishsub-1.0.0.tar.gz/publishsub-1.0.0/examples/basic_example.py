#!/usr/bin/env python3
"""
Basic example of using publishsub library
"""

import publishsub as pubsub

def main():
    print("=== Basic publishsub Example ===\n")
    
    # Enable debug mode to see what's happening
    pubsub.enable_debug(True)
    
    # Define event handlers
    def on_message(data):
        print(f"📧 Message received: {data}")
    
    def on_user_action(data):
        print(f"👤 User {data['user']} performed action: {data['action']}")
    
    def on_system_alert(data):
        print(f"🚨 ALERT: {data['message']} (Level: {data['level']})")
    
    # Subscribe to events
    print("Subscribing to events...")
    msg_sub = pubsub.subscribe("message", on_message)
    user_sub = pubsub.subscribe("user_action", on_user_action)
    alert_sub = pubsub.subscribe("system_alert", on_system_alert)
    
    # Multiple subscribers for the same event
    def on_message_backup(data):
        print(f"📋 Backup handler also received: {data}")
    
    backup_sub = pubsub.subscribe("message", on_message_backup)
    
    print(f"\nSubscription IDs:")
    print(f"  - Message: {msg_sub}")
    print(f"  - User Action: {user_sub}")
    print(f"  - System Alert: {alert_sub}")
    print(f"  - Backup: {backup_sub}")
    
    # Check subscribers count
    print(f"\nSubscribers count for 'message': {pubsub.subscribers_count('message')}")
    print(f"All events: {pubsub.list_events()}")
    
    print("\n" + "="*50)
    print("Publishing events...")
    print("="*50)
    
    # Publish events
    pubsub.publish("message", "Hello, World!")
    pubsub.publish("user_action", {"user": "Alice", "action": "login"})
    pubsub.publish("system_alert", {"message": "High CPU usage detected", "level": "warning"})
    
    # Publish to event with no subscribers
    result = pubsub.publish("unknown_event", "This won't be received")
    print(f"\nPublished to unknown_event, reached {result} subscribers")
    
    print("\n" + "="*50)
    print("Unsubscribing...")
    print("="*50)
    
    # Unsubscribe backup handler
    pubsub.unsubscribe("message", backup_sub)
    print(f"Subscribers count for 'message' after unsubscribe: {pubsub.subscribers_count('message')}")
    
    # Publish message again - should only reach main handler
    pubsub.publish("message", "This should only reach the main handler")
    
    print("\n" + "="*50)
    print("Cleaning up...")
    print("="*50)
    
    # Clear all subscribers
    pubsub.clear()
    print(f"All events after clear: {pubsub.list_events()}")
    
    # Try publishing after clearing
    result = pubsub.publish("message", "This won't be received")
    print(f"Published after clear, reached {result} subscribers")
    
    print("\n=== Example completed ===")

if __name__ == "__main__":
    main()