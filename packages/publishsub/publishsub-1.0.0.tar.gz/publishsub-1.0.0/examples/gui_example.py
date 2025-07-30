#!/usr/bin/env python3
"""
GUI application example using publishsub library
Simulates a simple GUI application with events
"""

import publishsub as pubsub
import time
import threading

class GUIApplication:
    def __init__(self):
        self.window_width = 800
        self.window_height = 600
        self.widgets = {}
        self.app_running = False
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup GUI event handlers"""
        pubsub.subscribe("app_start", self.on_app_start)
        pubsub.subscribe("app_close", self.on_app_close)
        pubsub.subscribe("button_click", self.on_button_click)
        pubsub.subscribe("menu_select", self.on_menu_select)
        pubsub.subscribe("window_resize", self.on_window_resize)
        pubsub.subscribe("widget_focus", self.on_widget_focus)
        pubsub.subscribe("text_input", self.on_text_input)
        pubsub.subscribe("file_open", self.on_file_open)
        pubsub.subscribe("file_save", self.on_file_save)
    
    def on_app_start(self, data):
        self.app_running = True
        print(f"🚀 Application started: {data['app_name']}")
        print(f"   Window size: {self.window_width}x{self.window_height}")
        
        # Initialize widgets
        self.widgets = {
            "main_menu": {"type": "menu", "items": ["File", "Edit", "View", "Help"]},
            "toolbar": {"type": "toolbar", "buttons": ["New", "Open", "Save", "Exit"]},
            "text_area": {"type": "text", "content": ""},
            "status_bar": {"type": "status", "text": "Ready"}
        }
        
        print(f"   Initialized {len(self.widgets)} widgets")
    
    def on_app_close(self, data):
        self.app_running = False
        print(f"🔚 Application closing: {data.get('reason', 'User request')}")
        if data.get('save_prompt'):
            print("   💾 Prompting user to save changes...")
    
    def on_button_click(self, data):
        button_id = data['button_id']
        print(f"🔘 Button clicked: {button_id}")
        
        # Handle specific button actions
        if button_id == "New":
            self.widgets["text_area"]["content"] = ""
            pubsub.publish("status_update", {"text": "New document created"})
        elif button_id == "Open":
            pubsub.publish("file_open", {"filters": ["*.txt", "*.md"]})
        elif button_id == "Save":
            pubsub.publish("file_save", {"content": self.widgets["text_area"]["content"]})
        elif button_id == "Exit":
            pubsub.publish("app_close", {"reason": "Exit button clicked"})
    
    def on_menu_select(self, data):
        menu_item = data['item']
        submenu = data.get('submenu')
        
        if submenu:
            print(f"📋 Menu selected: {menu_item} -> {submenu}")
        else:
            print(f"📋 Menu selected: {menu_item}")
        
        # Handle menu actions
        if menu_item == "File":
            if submenu == "New":
                pubsub.publish("button_click", {"button_id": "New"})
            elif submenu == "Open":
                pubsub.publish("file_open", {"filters": ["*.txt"]})
            elif submenu == "Exit":
                pubsub.publish("app_close", {"reason": "File menu exit"})
    
    def on_window_resize(self, data):
        self.window_width = data['width']
        self.window_height = data['height']
        print(f"🪟 Window resized to {self.window_width}x{self.window_height}")
        
        # Update status bar
        pubsub.publish("status_update", {"text": f"Window: {self.window_width}x{self.window_height}"})
    
    def on_widget_focus(self, data):
        widget_id = data['widget_id']
        print(f"🎯 Widget focused: {widget_id}")
        
        if widget_id == "text_area":
            pubsub.publish("status_update", {"text": "Text editor active"})
    
    def on_text_input(self, data):
        text = data['text']
        widget_id = data['widget_id']
        
        if widget_id == "text_area":
            self.widgets["text_area"]["content"] += text
            char_count = len(self.widgets["text_area"]["content"])
            print(f"⌨️  Text input: '{text}' (Total characters: {char_count})")
            
            # Update status with character count
            pubsub.publish("status_update", {"text": f"Characters: {char_count}"})
    
    def on_file_open(self, data):
        filename = data.get('filename', 'example.txt')
        print(f"📂 Opening file: {filename}")
        
        # Simulate file content
        content = f"Content of {filename}\nThis is a sample file.\nLoaded at {time.strftime('%H:%M:%S')}"
        self.widgets["text_area"]["content"] = content
        
        pubsub.publish("status_update", {"text": f"Opened: {filename}"})
    
    def on_file_save(self, data):
        filename = data.get('filename', 'document.txt')
        content = data['content']
        
        print(f"💾 Saving file: {filename}")
        print(f"   Content length: {len(content)} characters")
        
        # Simulate save operation
        pubsub.publish("status_update", {"text": f"Saved: {filename}"})

class StatusBar:
    def __init__(self):
        self.current_text = "Ready"
        pubsub.subscribe("status_update", self.on_status_update)
    
    def on_status_update(self, data):
        self.current_text = data['text']
        print(f"📊 Status: {self.current_text}")

def simulate_gui_session():
    """Simulate a GUI application session"""
    print("=== GUI Application Simulation ===\n")
    
    # Create application and components
    app = GUIApplication()
    status_bar = StatusBar()
    
    # Start application
    pubsub.publish("app_start", {"app_name": "Text Editor Pro"})
    
    time.sleep(0.5)
    
    # Simulate user interactions
    print("\n🖱️  User Interactions:")
    print("-" * 30)
    
    # Focus on text area
    pubsub.publish("widget_focus", {"widget_id": "text_area"})
    time.sleep(0.3)
    
    # Type some text
    text_inputs = ["Hello", " ", "World", "!", "\n", "This is a test."]
    for text in text_inputs:
        pubsub.publish("text_input", {"text": text, "widget_id": "text_area"})
        time.sleep(0.2)
    
    # Use menu
    pubsub.publish("menu_select", {"item": "File", "submenu": "Open"})
    time.sleep(0.5)
    
    # Simulate file operations
    pubsub.publish("file_open", {"filename": "sample.txt"})
    time.sleep(0.5)
    
    # Resize window
    pubsub.publish("window_resize", {"width": 1024, "height": 768})
    time.sleep(0.3)
    
    # Use toolbar buttons
    pubsub.publish("button_click", {"button_id": "Save"})
    time.sleep(0.5)
    
    # Type more text
    pubsub.publish("text_input", {"text": "\n\nAdditional content added!", "widget_id": "text_area"})
    time.sleep(0.3)
    
    # Close application
    pubsub.publish("app_close", {"reason": "User finished session", "save_prompt": True})
    
    print("\n=== GUI Simulation Complete ===")

if __name__ == "__main__":
    simulate_gui_session()