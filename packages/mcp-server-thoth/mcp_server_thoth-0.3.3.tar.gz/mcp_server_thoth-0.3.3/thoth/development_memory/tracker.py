"""
Development memory tracker for capturing and learning from all development attempts.
"""

import uuid
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from ..storage.database import Database
from ..storage.models import (
    DevelopmentSession, DevelopmentAttempt, FailurePattern, 
    LearnedSolution, Repository
)

logger = logging.getLogger(__name__)


class DevelopmentTracker:
    """Track all development attempts and learn from failures."""
    
    def __init__(self, db: Database):
        """Initialize the development tracker.
        
        Args:
            db: Database instance
        """
        self.db = db
        self.current_session_id: Optional[str] = None
        self._session = None
        self._attempt_counter = 0
        
    async def start_session(
        self, 
        repository_name: str, 
        task_description: str
    ) -> str:
        """Start a new development session.
        
        Args:
            repository_name: Name of the repository being worked on
            task_description: Description of what the user wants to achieve
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        async with self.db.get_session() as db_session:
            # Get repository
            result = await db_session.execute(
                select(Repository).where(Repository.name == repository_name)
            )
            repo = result.scalar_one_or_none()
            
            # Create session
            self._session = DevelopmentSession(
                session_id=session_id,
                repository_id=repo.id if repo else None,
                task_description=task_description,
                started_at=datetime.utcnow()
            )
            db_session.add(self._session)
            await db_session.commit()
            
        self.current_session_id = session_id
        self._attempt_counter = 0
        logger.info(f"Started development session {session_id}")
        
        return session_id
    
    async def end_session(self, outcome: str = "success") -> None:
        """End the current development session.
        
        Args:
            outcome: Session outcome (success, failure, partial, abandoned)
        """
        if not self.current_session_id:
            return
            
        async with self.db.get_session() as db_session:
            result = await db_session.execute(
                select(DevelopmentSession).where(
                    DevelopmentSession.session_id == self.current_session_id
                )
            )
            session = result.scalar_one_or_none()
            
            if session:
                session.ended_at = datetime.utcnow()
                session.outcome = outcome
                await db_session.commit()
                
        logger.info(f"Ended session {self.current_session_id} with outcome: {outcome}")
        self.current_session_id = None
        self._session = None
        
    async def track_attempt(
        self,
        action_type: str,
        target_file: Optional[str] = None,
        target_symbol: Optional[str] = None,
        approach_description: str = "",
        code_before: Optional[str] = None,
        code_after: Optional[str] = None,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None,
        success: bool = True
    ) -> int:
        """Track a development attempt.
        
        Args:
            action_type: Type of action (edit, create, delete, refactor, test)
            target_file: File being modified
            target_symbol: Symbol being modified
            approach_description: Description of the approach
            code_before: Code before the change
            code_after: Code after the change
            error_message: Error message if failed
            error_type: Type of error
            success: Whether the attempt succeeded
            
        Returns:
            Attempt ID
        """
        if not self.current_session_id:
            logger.warning("No active session, creating anonymous attempt")
            await self.start_session("unknown", "anonymous task")
            
        self._attempt_counter += 1
        
        async with self.db.get_session() as db_session:
            # Get session
            result = await db_session.execute(
                select(DevelopmentSession).where(
                    DevelopmentSession.session_id == self.current_session_id
                )
            )
            session = result.scalar_one()
            
            # Create attempt
            attempt = DevelopmentAttempt(
                session_id=session.id,
                attempt_number=self._attempt_counter,
                action_type=action_type,
                target_file=target_file,
                target_symbol=target_symbol,
                approach_description=approach_description,
                code_before=code_before,
                code_after=code_after,
                error_message=error_message,
                error_type=error_type,
                success=1 if success else 0,
                timestamp=datetime.utcnow()
            )
            db_session.add(attempt)
            await db_session.commit()
            
            # If failed, check for patterns
            if not success and error_message:
                await self._check_failure_pattern(
                    db_session, 
                    error_type or "unknown",
                    error_message,
                    session.repository_id
                )
                
            return attempt.id
            
    async def _check_failure_pattern(
        self,
        db_session,
        error_type: str,
        error_message: str,
        repository_id: Optional[int]
    ) -> None:
        """Check if this failure matches a known pattern.
        
        Args:
            db_session: Database session
            error_type: Type of error
            error_message: Error message
            repository_id: Repository ID
        """
        # Look for existing patterns
        result = await db_session.execute(
            select(FailurePattern).where(
                and_(
                    FailurePattern.pattern_type == error_type,
                    or_(
                        FailurePattern.repository_id == repository_id,
                        FailurePattern.repository_id.is_(None)
                    )
                )
            )
        )
        patterns = result.scalars().all()
        
        # Check if error matches any pattern
        matched = False
        for pattern in patterns:
            if pattern.detection_rule:
                try:
                    # Simple regex matching for now
                    if re.search(pattern.detection_rule, error_message, re.IGNORECASE):
                        pattern.occurrences += 1
                        pattern.last_seen = datetime.utcnow()
                        matched = True
                        break
                except:
                    pass
                    
        # Create new pattern if not matched
        if not matched and error_type != "unknown":
            # Extract key parts of error for pattern
            error_key = self._extract_error_key(error_type, error_message)
            if error_key:
                new_pattern = FailurePattern(
                    pattern_type=error_type,
                    description=f"Pattern: {error_key}",
                    detection_rule=re.escape(error_key),
                    repository_id=repository_id,
                    occurrences=1,
                    last_seen=datetime.utcnow()
                )
                db_session.add(new_pattern)
                
    def _extract_error_key(self, error_type: str, error_message: str) -> Optional[str]:
        """Extract key pattern from error message.
        
        Args:
            error_type: Type of error
            error_message: Full error message
            
        Returns:
            Key pattern or None
        """
        # Extract meaningful patterns based on error type
        if error_type == "import_error":
            match = re.search(r"No module named ['\"](\w+)['\"]", error_message)
            if match:
                return f"No module named '{match.group(1)}'"
            match = re.search(r"cannot import name ['\"](\w+)['\"]", error_message)
            if match:
                return f"cannot import name '{match.group(1)}'"
                
        elif error_type == "attribute_error":
            match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_message)
            if match:
                return f"'{match.group(1)}' object has no attribute '{match.group(2)}'"
                
        elif error_type == "type_error":
            # Look for common type error patterns
            if "expected" in error_message and "got" in error_message:
                match = re.search(r"expected .+ got .+", error_message)
                if match:
                    return match.group(0)
            # Missing required arguments
            match = re.search(r"missing \d+ required positional argument", error_message)
            if match:
                return match.group(0)
            # Wrong number of arguments
            match = re.search(r"takes \d+ positional arguments but \d+ were given", error_message)
            if match:
                return match.group(0)
                
        elif error_type == "syntax_error":
            match = re.search(r"(invalid syntax|unexpected EOF|unexpected indent)", error_message)
            if match:
                return match.group(1)
                
        elif error_type == "test_failure":
            # Extract assertion patterns
            match = re.search(r"AssertionError: (.+)", error_message)
            if match:
                return f"AssertionError: {match.group(1)[:100]}"
            # Failed test names
            match = re.search(r"FAILED (.+)::", error_message)
            if match:
                return f"FAILED {match.group(1)}"
                
        # Generic pattern: first line of error
        first_line = error_message.split('\n')[0].strip()
        if len(first_line) < 200:
            return first_line
            
        return None
        
    async def analyze_failure_patterns(
        self,
        repository_id: Optional[int] = None,
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze failure patterns to identify common issues.
        
        Args:
            repository_id: Repository to analyze
            time_window_days: Time window for analysis
            
        Returns:
            Analysis results with patterns and suggestions
        """
        async with self.db.get_session() as db_session:
            # Get recent failed attempts
            since_date = datetime.utcnow() - timedelta(days=time_window_days)
            
            query = select(DevelopmentAttempt).where(
                and_(
                    DevelopmentAttempt.success == 0,
                    DevelopmentAttempt.timestamp >= since_date
                )
            ).options(selectinload(DevelopmentAttempt.session))
            
            if repository_id:
                query = query.join(DevelopmentSession).where(
                    DevelopmentSession.repository_id == repository_id
                )
                
            result = await db_session.execute(query)
            failed_attempts = result.scalars().all()
            
            # Analyze patterns
            error_type_counts = {}
            file_failure_counts = {}
            action_failure_counts = {}
            error_messages = []
            
            for attempt in failed_attempts:
                # Count by error type
                if attempt.error_type:
                    error_type_counts[attempt.error_type] = error_type_counts.get(attempt.error_type, 0) + 1
                    
                # Count by file
                if attempt.target_file:
                    file_failure_counts[attempt.target_file] = file_failure_counts.get(attempt.target_file, 0) + 1
                    
                # Count by action type
                action_failure_counts[attempt.action_type] = action_failure_counts.get(attempt.action_type, 0) + 1
                
                # Collect error messages for clustering
                if attempt.error_message:
                    error_messages.append({
                        'message': attempt.error_message,
                        'type': attempt.error_type,
                        'file': attempt.target_file
                    })
                    
            # Find most problematic files
            problematic_files = sorted(
                file_failure_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Find most common error types
            common_errors = sorted(
                error_type_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Cluster similar errors
            error_clusters = self._cluster_errors(error_messages)
            
            # Generate suggestions based on patterns
            suggestions = await self._generate_pattern_suggestions(
                db_session,
                common_errors,
                problematic_files,
                error_clusters
            )
            
            return {
                'total_failures': len(failed_attempts),
                'common_error_types': common_errors,
                'problematic_files': problematic_files,
                'action_failure_distribution': action_failure_counts,
                'error_clusters': error_clusters[:5],  # Top 5 clusters
                'suggestions': suggestions
            }
            
    def _cluster_errors(self, error_messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Cluster similar error messages.
        
        Args:
            error_messages: List of error message dicts
            
        Returns:
            List of error clusters
        """
        if not error_messages:
            return []
            
        # Simple clustering by extracting key patterns
        clusters = {}
        
        for error in error_messages:
            msg = error['message']
            error_type = error['type']
            
            # Extract key pattern
            key = self._extract_error_key(error_type, msg)
            if not key:
                key = error_type or 'unknown'
                
            if key not in clusters:
                clusters[key] = {
                    'pattern': key,
                    'count': 0,
                    'examples': [],
                    'files': set()
                }
                
            clusters[key]['count'] += 1
            if len(clusters[key]['examples']) < 3:
                clusters[key]['examples'].append(msg[:200])
            if error['file']:
                clusters[key]['files'].add(error['file'])
                
        # Convert to list and sort by frequency
        cluster_list = []
        for key, cluster in clusters.items():
            cluster['files'] = list(cluster['files'])[:5]  # Limit files
            cluster_list.append(cluster)
            
        cluster_list.sort(key=lambda x: x['count'], reverse=True)
        
        return cluster_list
        
    async def _generate_pattern_suggestions(
        self,
        db_session,
        common_errors: List[Tuple[str, int]],
        problematic_files: List[Tuple[str, int]],
        error_clusters: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate suggestions based on failure patterns.
        
        Args:
            db_session: Database session
            common_errors: Most common error types
            problematic_files: Files with most failures
            error_clusters: Clustered error patterns
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Suggestions for common error types
        for error_type, count in common_errors[:3]:
            if error_type == "import_error" and count > 3:
                suggestions.append(
                    f"High number of import errors ({count}). "
                    "Consider checking dependencies and import paths."
                )
            elif error_type == "type_error" and count > 3:
                suggestions.append(
                    f"Frequent type errors ({count}). "
                    "Consider adding type hints and validation."
                )
            elif error_type == "test_failure" and count > 5:
                suggestions.append(
                    f"Many test failures ({count}). "
                    "Consider running tests before making changes."
                )
                
        # Suggestions for problematic files
        if problematic_files and problematic_files[0][1] > 5:
            file_path, fail_count = problematic_files[0]
            suggestions.append(
                f"File '{file_path}' has failed {fail_count} times. "
                "Consider refactoring or adding better error handling."
            )
            
        # Suggestions from error clusters
        for cluster in error_clusters[:2]:
            if cluster['count'] > 3:
                if "No module named" in cluster['pattern']:
                    module = cluster['pattern'].split("'")[1]
                    suggestions.append(
                        f"Module '{module}' import failed {cluster['count']} times. "
                        "Check if it's installed or spelled correctly."
                    )
                elif "has no attribute" in cluster['pattern']:
                    suggestions.append(
                        f"Attribute errors occurred {cluster['count']} times: {cluster['pattern']}. "
                        "Check API documentation or object structure."
                    )
                    
        # Look for existing solutions
        if error_clusters:
            top_pattern = error_clusters[0]['pattern']
            result = await db_session.execute(
                select(LearnedSolution).where(
                    LearnedSolution.problem_description.like(f"%{top_pattern[:50]}%")
                ).order_by(desc(LearnedSolution.success_rate))
            )
            solution = result.scalar_one_or_none()
            
            if solution:
                suggestions.append(
                    f"Found a solution for similar issue: {solution.solution_description}"
                )
                
        return suggestions
        
    async def record_solution(
        self,
        problem_description: str,
        solution_description: str,
        code_example: Optional[str] = None,
        tags: List[str] = None
    ) -> None:
        """Record a successful solution for future reference.
        
        Args:
            problem_description: Description of the problem
            solution_description: Description of the solution
            code_example: Example code
            tags: Tags for categorization
        """
        async with self.db.get_session() as db_session:
            # Check if similar solution exists
            result = await db_session.execute(
                select(LearnedSolution).where(
                    LearnedSolution.problem_description == problem_description
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing solution
                existing.times_used += 1
                existing.last_used = datetime.utcnow()
                if code_example:
                    existing.code_example = code_example
            else:
                # Get repository from current session
                repo_id = None
                if self._session:
                    repo_id = self._session.repository_id
                    
                # Create new solution
                solution = LearnedSolution(
                    problem_description=problem_description,
                    solution_description=solution_description,
                    code_example=code_example,
                    repository_id=repo_id,
                    tags=",".join(tags) if tags else None,
                    last_used=datetime.utcnow()
                )
                db_session.add(solution)
                
            await db_session.commit()
            
    async def find_similar_attempts(
        self,
        action_type: str,
        target_file: Optional[str] = None,
        error_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar past attempts.
        
        Args:
            action_type: Type of action to search for
            target_file: Target file pattern
            error_type: Error type to filter by
            limit: Maximum results
            
        Returns:
            List of similar attempts
        """
        async with self.db.get_session() as db_session:
            query = select(DevelopmentAttempt).where(
                DevelopmentAttempt.action_type == action_type
            )
            
            if target_file:
                query = query.where(
                    DevelopmentAttempt.target_file.like(f"%{target_file}%")
                )
                
            if error_type:
                query = query.where(
                    DevelopmentAttempt.error_type == error_type
                )
                
            query = query.order_by(desc(DevelopmentAttempt.timestamp)).limit(limit)
            
            result = await db_session.execute(
                query.options(selectinload(DevelopmentAttempt.session))
            )
            attempts = result.scalars().all()
            
            return [
                {
                    "id": attempt.id,
                    "timestamp": attempt.timestamp.isoformat(),
                    "action_type": attempt.action_type,
                    "target_file": attempt.target_file,
                    "approach": attempt.approach_description,
                    "success": bool(attempt.success),
                    "error_type": attempt.error_type,
                    "error_message": attempt.error_message,
                    "task": attempt.session.task_description
                }
                for attempt in attempts
            ]
            
    async def get_failure_patterns(
        self,
        repository_name: Optional[str] = None,
        min_occurrences: int = 2
    ) -> List[Dict[str, Any]]:
        """Get common failure patterns.
        
        Args:
            repository_name: Filter by repository
            min_occurrences: Minimum occurrence count
            
        Returns:
            List of failure patterns
        """
        async with self.db.get_session() as db_session:
            query = select(FailurePattern).where(
                FailurePattern.occurrences >= min_occurrences
            )
            
            if repository_name:
                result = await db_session.execute(
                    select(Repository).where(Repository.name == repository_name)
                )
                repo = result.scalar_one_or_none()
                if repo:
                    query = query.where(
                        or_(
                            FailurePattern.repository_id == repo.id,
                            FailurePattern.repository_id.is_(None)
                        )
                    )
                    
            query = query.order_by(desc(FailurePattern.occurrences))
            
            result = await db_session.execute(query)
            patterns = result.scalars().all()
            
            return [
                {
                    "pattern_type": pattern.pattern_type,
                    "description": pattern.description,
                    "occurrences": pattern.occurrences,
                    "last_seen": pattern.last_seen.isoformat(),
                    "suggested_solution": pattern.suggested_solution
                }
                for pattern in patterns
            ]
            
    async def search_solutions(
        self,
        query: str,
        repository_name: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search for learned solutions.
        
        Args:
            query: Search query
            repository_name: Filter by repository
            tags: Filter by tags
            
        Returns:
            List of matching solutions
        """
        async with self.db.get_session() as db_session:
            conditions = []
            
            # Text search in problem and solution descriptions
            if query:
                conditions.append(
                    or_(
                        LearnedSolution.problem_description.ilike(f"%{query}%"),
                        LearnedSolution.solution_description.ilike(f"%{query}%")
                    )
                )
                
            # Repository filter
            if repository_name:
                result = await db_session.execute(
                    select(Repository).where(Repository.name == repository_name)
                )
                repo = result.scalar_one_or_none()
                if repo:
                    conditions.append(
                        or_(
                            LearnedSolution.repository_id == repo.id,
                            LearnedSolution.repository_id.is_(None)
                        )
                    )
                    
            # Tag filter
            if tags:
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(
                        LearnedSolution.tags.like(f"%{tag}%")
                    )
                conditions.append(or_(*tag_conditions))
                
            # Build query
            if conditions:
                query = select(LearnedSolution).where(and_(*conditions))
            else:
                query = select(LearnedSolution)
                
            query = query.order_by(
                desc(LearnedSolution.success_rate),
                desc(LearnedSolution.times_used)
            )
            
            result = await db_session.execute(query)
            solutions = result.scalars().all()
            
            return [
                {
                    "problem": solution.problem_description,
                    "solution": solution.solution_description,
                    "code_example": solution.code_example,
                    "success_rate": solution.success_rate,
                    "times_used": solution.times_used,
                    "last_used": solution.last_used.isoformat(),
                    "tags": solution.tags.split(",") if solution.tags else []
                }
                for solution in solutions
            ]
            
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a development session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session summary
        """
        async with self.db.get_session() as db_session:
            result = await db_session.execute(
                select(DevelopmentSession)
                .where(DevelopmentSession.session_id == session_id)
                .options(selectinload(DevelopmentSession.attempts))
            )
            session = result.scalar_one_or_none()
            
            if not session:
                return {}
                
            # Calculate statistics
            total_attempts = len(session.attempts)
            successful_attempts = sum(1 for a in session.attempts if a.success)
            failed_attempts = total_attempts - successful_attempts
            
            # Group by action type
            action_counts = {}
            error_types = {}
            
            for attempt in session.attempts:
                action_counts[attempt.action_type] = action_counts.get(attempt.action_type, 0) + 1
                if not attempt.success and attempt.error_type:
                    error_types[attempt.error_type] = error_types.get(attempt.error_type, 0) + 1
                    
            return {
                "session_id": session.session_id,
                "task": session.task_description,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "duration": str(session.ended_at - session.started_at) if session.ended_at else None,
                "outcome": session.outcome,
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "failed_attempts": failed_attempts,
                "success_rate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
                "action_breakdown": action_counts,
                "error_breakdown": error_types
            }