#!/usr/bin/env python3
"""Test text insertion functionality"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.text_inserter import TextInserter
import logging

logging.basicConfig(level=logging.DEBUG)

print("Testing text insertion...")
inserter = TextInserter()

print("\nTest 1: Insert via clipboard")
result = inserter.insert_text("Hello from test!", method="clipboard")
print(f"Result: {result}")

print("\nTest 2: Insert at cursor")
result = inserter.insert_at_cursor("This is a cursor test")
print(f"Result: {result}")

print("\nDone! Check if text was pasted.")
