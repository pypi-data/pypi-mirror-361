#!/usr/bin/env python3
"""Test the init command service checks."""

import subprocess
import sys
import os

def test_init_output():
    """Run init and check output."""
    print("Testing thoth-cli init --no-start-services...\n")
    
    # Run init without starting services
    result = subprocess.run(
        [sys.executable, "-m", "thoth.cli.main", "init", "--no-start-services"],
        capture_output=True,
        text=True
    )
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    # Check for expected messages
    expected_messages = [
        "Database initialized",
        "Created directories",
        "ChromaDB server not running",
        "Thoth will use embedded ChromaDB",
        "Created environment file",
        "All modules loaded successfully"
    ]
    
    for msg in expected_messages:
        if msg in result.stdout:
            print(f"✓ Found: {msg}")
        else:
            print(f"✗ Missing: {msg}")
    
    # Check environment file
    env_file = os.path.expanduser("~/.thoth/env")
    if os.path.exists(env_file):
        print(f"\n✓ Environment file created: {env_file}")
        with open(env_file) as f:
            content = f.read()
            print("Contents:")
            print(content)
    else:
        print(f"\n✗ Environment file not found: {env_file}")

if __name__ == "__main__":
    test_init_output()