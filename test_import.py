#!/usr/bin/env python
"""Test import to verify Pydantic v2 compatibility"""
import sys

try:
    print("Testing import...")
    from app.main import app
    print("✅ SUCCESS: app.main imported correctly (Pydantic v2 compatible)")
    sys.exit(0)
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
