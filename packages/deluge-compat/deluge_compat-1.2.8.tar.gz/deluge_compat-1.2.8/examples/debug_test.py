#!/usr/bin/env python3
"""Debug conditional logic."""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from deluge_compat import run_deluge_script


def test_simple_conditional():
    """Test a simple conditional."""
    print("=== Testing Simple Conditional ===")

    script = """
    score = 85;
    if(score >= 90) {
        grade = "A";
    } else {
        grade = "B";
    }
    return grade;
    """

    try:
        result = run_deluge_script(script)
        print("Result:", result)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_simple_conditional()
