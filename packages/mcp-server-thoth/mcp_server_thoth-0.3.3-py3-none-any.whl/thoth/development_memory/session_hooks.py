"""
Hooks for integrating development memory with Claude sessions.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionHooks:
    """Manage session persistence for Claude development memory."""
    
    def __init__(self, session_dir: str = "~/.thoth/sessions"):
        """Initialize session hooks.
        
        Args:
            session_dir: Directory to store session data
        """
        self.session_dir = Path(session_dir).expanduser()
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_file = self.session_dir / ".current_session"
        
    def save_current_session(self, session_id: str, repository: str) -> None:
        """Save current session ID for later retrieval.
        
        Args:
            session_id: Current session ID
            repository: Repository name
        """
        session_data = {
            "session_id": session_id,
            "repository": repository,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(self.current_session_file, 'w') as f:
            json.dump(session_data, f)
            
        logger.info(f"Saved current session: {session_id}")
        
    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get the current session if one exists.
        
        Returns:
            Session data or None
        """
        if not self.current_session_file.exists():
            return None
            
        try:
            with open(self.current_session_file, 'r') as f:
                data = json.load(f)
                
            # Check if session is recent (within 24 hours)
            timestamp = datetime.fromisoformat(data['timestamp'])
            age = datetime.utcnow() - timestamp
            
            if age.total_seconds() > 86400:  # 24 hours
                logger.info("Session expired, clearing")
                self.clear_current_session()
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Error reading session: {e}")
            return None
            
    def clear_current_session(self) -> None:
        """Clear the current session."""
        if self.current_session_file.exists():
            self.current_session_file.unlink()
            
    def create_attempt_hook(self, tracker) -> callable:
        """Create a hook function for Claude's edit/write operations.
        
        Args:
            tracker: DevelopmentTracker instance
            
        Returns:
            Hook function
        """
        async def hook(action: str, file_path: str, content_before: str = None, 
                      content_after: str = None, error: str = None) -> None:
            """Hook to track development attempts.
            
            Args:
                action: Action type (edit, create, delete)
                file_path: File being modified
                content_before: Content before change
                content_after: Content after change
                error: Error message if failed
            """
            # Map Claude actions to our action types
            action_map = {
                "edit": "edit",
                "write": "create",
                "create": "create",
                "delete": "delete"
            }
            
            action_type = action_map.get(action.lower(), "edit")
            success = error is None
            
            # Get current session
            session_data = self.get_current_session()
            if not session_data:
                # Auto-start session if needed
                logger.info("No active session, auto-starting")
                session_id = await tracker.start_session(
                    repository_name="unknown",
                    task_description="Auto-started session"
                )
                self.save_current_session(session_id, "unknown")
            else:
                # Restore session in tracker if needed
                if tracker.current_session_id != session_data['session_id']:
                    tracker.current_session_id = session_data['session_id']
                    logger.info(f"Restored session: {session_data['session_id']}")
            
            # Track the attempt
            await tracker.track_attempt(
                action_type=action_type,
                target_file=file_path,
                approach_description=f"Claude {action} operation",
                code_before=content_before,
                code_after=content_after,
                error_message=error,
                success=success
            )
            
        return hook
        
    def create_test_hook(self, tracker) -> callable:
        """Create a hook for test execution tracking.
        
        Args:
            tracker: DevelopmentTracker instance
            
        Returns:
            Hook function
        """
        async def hook(test_command: str, output: str, exit_code: int) -> None:
            """Hook to track test executions.
            
            Args:
                test_command: Test command that was run
                output: Test output
                exit_code: Exit code (0 = success)
            """
            success = exit_code == 0
            error_message = output if not success else None
            
            # Get current session
            session_data = self.get_current_session()
            if session_data:
                # Restore session in tracker if needed
                if tracker.current_session_id != session_data['session_id']:
                    tracker.current_session_id = session_data['session_id']
            
            # Track test attempt
            await tracker.track_attempt(
                action_type="test",
                approach_description=f"Run: {test_command}",
                error_message=error_message,
                error_type="test_failure" if not success else None,
                success=success
            )
            
        return hook
        
    def export_session_data(self, session_id: str, export_path: str) -> None:
        """Export session data for analysis.
        
        Args:
            session_id: Session ID to export
            export_path: Path to export file
        """
        # This would connect to database and export full session data
        # Implementation depends on having access to the database
        pass