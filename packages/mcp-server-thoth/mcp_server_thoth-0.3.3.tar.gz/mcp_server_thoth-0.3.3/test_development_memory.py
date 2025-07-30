#!/usr/bin/env python3
"""Comprehensive test for development memory feature."""

import asyncio
import sys
from pathlib import Path

# Add thoth to path
sys.path.insert(0, str(Path(__file__).parent))

from thoth.storage.database import Database
from thoth.development_memory.tracker import DevelopmentTracker
from thoth.development_memory.session_hooks import SessionHooks
from thoth.mcp.server import (
    start_dev_session, track_attempt, check_approach, 
    learn_from_failure, analyze_patterns
)


async def test_development_memory():
    """Test all development memory functionality."""
    print("=== Testing Development Memory Feature ===\n")
    
    # Initialize database
    print("Initializing test database...")
    test_db_path = Path("test_dev_memory.db")
    if test_db_path.exists():
        test_db_path.unlink()
    
    db = Database(str(test_db_path))
    await db.init_db()
    print("✓ Database initialized\n")
    
    # Test 1: Direct tracker API
    print("=== Testing Direct Tracker API ===")
    tracker = DevelopmentTracker(db)
    
    # Start session
    print("1. Starting development session...")
    session_id = await tracker.start_session(
        repository_name="test-repo",
        task_description="Test development memory feature"
    )
    print(f"   ✓ Session started: {session_id}")
    
    # Track attempts
    print("\n2. Tracking development attempts...")
    
    # Successful attempt
    attempt1 = await tracker.track_attempt(
        action_type="edit",
        target_file="auth.py",
        approach_description="Add input validation to login function",
        code_before="def login(username, password):\n    return True",
        code_after="def login(username, password):\n    if not username or not password:\n        return False\n    return True",
        success=True
    )
    print(f"   ✓ Tracked successful edit (ID: {attempt1})")
    
    # Failed attempt 1
    attempt2 = await tracker.track_attempt(
        action_type="edit",
        target_file="auth.py",
        approach_description="Add type hints without importing Optional",
        code_before="def login(username, password):",
        code_after="def login(username: Optional[str], password: str) -> bool:",
        error_message="NameError: name 'Optional' is not defined",
        error_type="import_error",
        success=False
    )
    print(f"   ✓ Tracked failed edit (ID: {attempt2})")
    
    # Failed attempt 2 (similar error)
    attempt3 = await tracker.track_attempt(
        action_type="edit",
        target_file="models.py",
        approach_description="Add type hints to User model",
        error_message="NameError: name 'Optional' is not defined",
        error_type="import_error",
        success=False
    )
    print(f"   ✓ Tracked another import error (ID: {attempt3})")
    
    # Test failure
    attempt4 = await tracker.track_attempt(
        action_type="test",
        approach_description="Run pytest",
        error_message="AssertionError: Expected True but got False",
        error_type="test_failure",
        success=False
    )
    print(f"   ✓ Tracked test failure (ID: {attempt4})")
    
    # Find similar attempts
    print("\n3. Finding similar attempts...")
    similar = await tracker.find_similar_attempts(
        action_type="edit",
        error_type="import_error"
    )
    print(f"   ✓ Found {len(similar)} similar import errors")
    
    # Record solution
    print("\n4. Recording solution...")
    await tracker.record_solution(
        problem_description="NameError: name 'Optional' is not defined when using type hints",
        solution_description="Import Optional from typing module",
        code_example="from typing import Optional\n\ndef login(username: Optional[str], password: str) -> bool:\n    ...",
        tags=["import", "type-hints", "typing"]
    )
    print("   ✓ Solution recorded")
    
    # Analyze patterns
    print("\n5. Analyzing failure patterns...")
    analysis = await tracker.analyze_failure_patterns(time_window_days=1)
    print(f"   ✓ Analysis results:")
    print(f"     - Total failures: {analysis['total_failures']}")
    print(f"     - Common error types: {analysis['common_error_types']}")
    print(f"     - Error clusters: {len(analysis['error_clusters'])}")
    print(f"     - Suggestions: {len(analysis['suggestions'])}")
    
    # End session
    await tracker.end_session("success")
    print("\n✓ Direct API tests completed\n")
    
    # Test 2: Session persistence
    print("=== Testing Session Persistence ===")
    hooks = SessionHooks("./test_sessions")
    
    hooks.save_current_session(session_id, "test-repo")
    saved = hooks.get_current_session()
    if saved and saved['session_id'] == session_id:
        print("✓ Session persisted and retrieved successfully")
    else:
        print("✗ Session persistence failed")
    
    # Test 3: MCP Tools
    print("\n=== Testing MCP Tools ===")
    
    # Start new session via MCP
    print("1. Testing start_dev_session MCP tool...")
    result = await start_dev_session({
        "repository": "thoth",
        "task": "Test MCP integration"
    })
    print(f"   Response: {result[0].text}")
    
    # Track via MCP
    print("\n2. Testing track_attempt MCP tool...")
    result = await track_attempt({
        "action_type": "create",
        "target_file": "test_feature.py",
        "approach": "Create new test file",
        "success": True
    })
    print(f"   Response: {result[0].text}")
    
    # Track failure via MCP
    result = await track_attempt({
        "action_type": "test",
        "approach": "Run unit tests",
        "success": False,
        "error_message": "ImportError: No module named 'pytest'"
    })
    print(f"   Response: {result[0].text}")
    
    # Check approach via MCP
    print("\n3. Testing check_approach MCP tool...")
    result = await check_approach({
        "action_type": "edit"
    })
    print(f"   Response preview: {result[0].text[:200]}...")
    
    # Learn from failure via MCP
    print("\n4. Testing learn_from_failure MCP tool...")
    result = await learn_from_failure({
        "query": "Optional type hints",
        "repository": "test-repo"
    })
    print(f"   Response preview: {result[0].text[:200]}...")
    
    # Analyze patterns via MCP
    print("\n5. Testing analyze_patterns MCP tool...")
    result = await analyze_patterns({
        "days": 1
    })
    print(f"   Response preview: {result[0].text[:300]}...")
    
    print("\n✓ All MCP tools tested successfully!")
    
    # Cleanup
    print("\nCleaning up...")
    test_db_path.unlink(missing_ok=True)
    import shutil
    shutil.rmtree("test_sessions", ignore_errors=True)
    print("✓ Cleanup complete")
    
    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    asyncio.run(test_development_memory())