#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script to fix the corrupted emoji in chat_interface.py

import re

def fix_emoji():
    try:
        # Read the file
        with open('ui/chat_interface.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the corrupted emoji pattern
        # Look for the pattern: "?\\nHabit/Reminder" or similar corrupted character
        pattern = r'"[^\w\n💭🎨🧘‍♀️]*\\nHabit/Reminder"'
        replacement = '"💎\\nHabit/Reminder"'
        
        # Replace the pattern
        content = re.sub(pattern, replacement, content)
        
        # Also try direct replacement of common corrupted characters
        content = content.replace('"�\\nHabit/Reminder"', '"💎\\nHabit/Reminder"')
        content = content.replace('"?\\nHabit/Reminder"', '"💎\\nHabit/Reminder"')
        content = content.replace('"\\nHabit/Reminder"', '"💎\\nHabit/Reminder"')
        
        # Write back the corrected content
        with open('ui/chat_interface.py', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("✅ Fixed emoji character in chat_interface.py")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing emoji: {e}")
        return False

if __name__ == "__main__":
    fix_emoji()
