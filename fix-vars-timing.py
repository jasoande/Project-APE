#!/usr/bin/env python3
"""
Quick fix for vars.py timing values that are incorrectly stored as strings
"""

import re
from pathlib import Path

vars_file = Path('vars.py')

if not vars_file.exists():
    print("❌ vars.py not found")
    exit(1)

content = vars_file.read_text()

# Fix timing string values - convert "[8, 12]" to (8, 12)
fixes = [
    (r"'ask_prompt_delay': \"\[8, 12\]\"", "'ask_prompt_delay': (8, 12)"),
    (r"'chat_prompt_delay': \"\[5, 8\]\"", "'chat_prompt_delay': (5, 8)"),
    (r"'ask_prompt_delay': \"\[15, 25\]\"", "'ask_prompt_delay': (15, 25)"),
    (r"'chat_prompt_delay': \"\[10, 15\]\"", "'chat_prompt_delay': (10, 15)"),
    (r"'source_add_delay': \"\[2, 4\]\"", "'source_add_delay': (2, 4)"),
]

for pattern, replacement in fixes:
    content = re.sub(pattern, replacement, content)

# Write back
vars_file.write_text(content)

print("✅ Fixed vars.py timing values")
print("\nPlease restart the dashboard:")
print("  pkill -f 'python.*server.py'")
print("  python3 launch-project-ape.py")
