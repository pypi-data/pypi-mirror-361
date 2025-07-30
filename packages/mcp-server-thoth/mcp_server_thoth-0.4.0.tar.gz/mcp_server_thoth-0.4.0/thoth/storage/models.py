"""SQLAlchemy models for code analysis data."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Repository(Base):
    """Repository configuration and metadata."""
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    path = Column(String(1024), nullable=False)
    language = Column(String(50))
    last_indexed = Column(DateTime)
    
    # Relationships
    files = relationship("File", back_populates="repository", cascade="all, delete-orphan")
    symbols = relationship("Symbol", back_populates="repository", cascade="all, delete-orphan")


class File(Base):
    """File metadata and content hash."""
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    path = Column(String(1024), nullable=False)
    last_modified = Column(DateTime)
    content_hash = Column(String(64))
    
    # Relationships
    repository = relationship("Repository", back_populates="files")
    symbols = relationship("Symbol", back_populates="file", cascade="all, delete-orphan")
    imports = relationship("Import", foreign_keys="Import.file_id", back_populates="file", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('repository_id', 'path', name='_repo_path_uc'),
        Index('idx_file_path', 'path'),
    )


class Symbol(Base):
    """Code symbols (functions, classes, methods)."""
    __tablename__ = 'symbols'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # function, class, method
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    line = Column(Integer)
    column = Column(Integer)
    parent_id = Column(Integer, ForeignKey('symbols.id'))
    docstring = Column(Text)
    
    # Relationships
    repository = relationship("Repository", back_populates="symbols")
    file = relationship("File", back_populates="symbols")
    parent = relationship("Symbol", remote_side=[id])
    children = relationship("Symbol", back_populates="parent")
    
    # Call relationships
    calls_made = relationship(
        "Call", foreign_keys="Call.caller_symbol_id", back_populates="caller"
    )
    calls_received = relationship(
        "Call", foreign_keys="Call.callee_symbol_id", back_populates="callee"
    )
    
    __table_args__ = (
        Index('idx_symbol_name', 'name'),
        Index('idx_symbol_type', 'type'),
        Index('idx_symbol_repo', 'repository_id'),
    )


class Import(Base):
    """Import statements."""
    __tablename__ = 'imports'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    module = Column(String(255), nullable=False)
    name = Column(String(255))
    alias = Column(String(255))
    line = Column(Integer)
    resolved_repository_id = Column(Integer, ForeignKey('repositories.id'))
    resolved_file_id = Column(Integer, ForeignKey('files.id'))
    
    # Relationships
    file = relationship("File", foreign_keys=[file_id], back_populates="imports")
    resolved_repository = relationship("Repository", foreign_keys=[resolved_repository_id])
    resolved_file = relationship("File", foreign_keys=[resolved_file_id])
    
    __table_args__ = (
        Index('idx_import_module', 'module'),
    )


class Call(Base):
    """Function/method calls."""
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True)
    caller_symbol_id = Column(Integer, ForeignKey('symbols.id'))
    callee_symbol_id = Column(Integer, ForeignKey('symbols.id'))
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    line = Column(Integer)
    column = Column(Integer)
    
    # Relationships
    caller = relationship("Symbol", foreign_keys=[caller_symbol_id], back_populates="calls_made")
    callee = relationship("Symbol", foreign_keys=[callee_symbol_id], back_populates="calls_received")
    file = relationship("File")
    
    __table_args__ = (
        Index('idx_call_caller', 'caller_symbol_id'),
        Index('idx_call_callee', 'callee_symbol_id'),
    )


class Diagram(Base):
    """Cached diagram data."""
    __tablename__ = 'diagrams'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)  # module_deps, class_diagram, etc.
    scope = Column(String(255))  # repository name or 'system'
    content = Column(Text, nullable=False)  # Mermaid diagram content
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_diagram_type_scope', 'type', 'scope'),
    )


class APIEndpoint(Base):
    """API endpoints detected in code."""
    __tablename__ = 'api_endpoints'
    
    id = Column(Integer, primary_key=True)
    method = Column(String(20), nullable=False)  # GET, POST, etc.
    path = Column(String(512), nullable=False)
    handler_symbol_id = Column(Integer, ForeignKey('symbols.id'))
    repository_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    line = Column(Integer)
    
    # Relationships
    handler = relationship("Symbol", foreign_keys=[handler_symbol_id])
    repository = relationship("Repository")
    file = relationship("File")
    
    __table_args__ = (
        Index('idx_endpoint_method_path', 'method', 'path'),
        Index('idx_endpoint_repo', 'repository_id'),
    )


class DevelopmentSession(Base):
    """Claude development session tracking."""
    __tablename__ = 'development_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)  # UUID for session
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    task_description = Column(Text)  # What the user asked for
    outcome = Column(String(50))  # success, failure, partial, abandoned
    
    # Relationships
    repository = relationship("Repository")
    attempts = relationship("DevelopmentAttempt", back_populates="session", cascade="all, delete-orphan")


class DevelopmentAttempt(Base):
    """Individual development attempts within a session."""
    __tablename__ = 'development_attempts'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('development_sessions.id'), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action_type = Column(String(50), nullable=False)  # edit, create, delete, refactor, test
    target_file = Column(String(1024))
    target_symbol = Column(String(255))
    approach_description = Column(Text)  # What approach was tried
    code_before = Column(Text)
    code_after = Column(Text)
    error_message = Column(Text)
    error_type = Column(String(100))  # syntax, type, runtime, test_failure, etc.
    success = Column(Integer, default=0)  # Boolean: 0 or 1
    reverted = Column(Integer, default=0)  # Boolean: was this change reverted?
    
    # Relationships
    session = relationship("DevelopmentSession", back_populates="attempts")
    
    __table_args__ = (
        Index('idx_attempt_session', 'session_id'),
        Index('idx_attempt_action', 'action_type'),
        Index('idx_attempt_success', 'success'),
    )


class FailurePattern(Base):
    """Recognized patterns of failures for learning."""
    __tablename__ = 'failure_patterns'
    
    id = Column(Integer, primary_key=True)
    pattern_type = Column(String(100), nullable=False)  # import_error, type_mismatch, etc.
    description = Column(Text)
    detection_rule = Column(Text)  # JSON or regex pattern to detect this failure
    suggested_solution = Column(Text)
    occurrences = Column(Integer, default=1)
    last_seen = Column(DateTime, default=datetime.utcnow)
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    
    # Relationships
    repository = relationship("Repository")
    
    __table_args__ = (
        Index('idx_pattern_type', 'pattern_type'),
        Index('idx_pattern_repo', 'repository_id'),
    )


class LearnedSolution(Base):
    """Successful solutions to common problems."""
    __tablename__ = 'learned_solutions'
    
    id = Column(Integer, primary_key=True)
    problem_description = Column(Text, nullable=False)
    solution_description = Column(Text, nullable=False)
    code_example = Column(Text)
    success_rate = Column(Integer, default=100)  # Percentage
    times_used = Column(Integer, default=1)
    last_used = Column(DateTime, default=datetime.utcnow)
    repository_id = Column(Integer, ForeignKey('repositories.id'))
    tags = Column(String(500))  # Comma-separated tags
    
    # Relationships
    repository = relationship("Repository")
    
    __table_args__ = (
        Index('idx_solution_repo', 'repository_id'),
        Index('idx_solution_tags', 'tags'),
    )