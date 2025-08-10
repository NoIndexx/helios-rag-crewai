#!/usr/bin/env python3
"""
Test script to verify that the LLM is using tools correctly and not hallucinating data.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.crew.run_agent import kickoff_example

def test_highest_risk_cocoa():
    """Test that the highest risk query returns India (from actual database data)"""
    print("🧪 Testing: What country has the highest current climate risk for Cocoa beans?")
    print("Expected: India (based on database query showing 45.7 WAPR)")
    print("=" * 70)
    
    result = kickoff_example("What country has the highest current climate risk for Cocoa beans?")
    
    print(f"Answer: {result.answer}")
    print(f"Source: {result.source}")
    print(f"Query: {result.query}")
    
    # Check if the result mentions India
    if "India" in result.answer or "IN" in str(result.source):
        print("✅ PASS: Result mentions India (correct)")
    else:
        print("❌ FAIL: Result does not mention India (incorrect/hallucinated)")
        
    # Check if tool was actually called
    if hasattr(result, 'query') and result.query.get('tool') == 'get_highest_current_risk':
        print("✅ PASS: Tool was called correctly")
    else:
        print("❌ FAIL: Tool was not called or incorrect tool used")

if __name__ == "__main__":
    test_highest_risk_cocoa()
