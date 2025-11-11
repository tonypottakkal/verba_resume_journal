"""
ConversationManager module for managing conversation context during resume generation.

This module provides functionality to store, retrieve, and manage conversation
history for iterative resume refinement sessions.
"""

from wasabi import msg
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import uuid


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ConversationSession:
    """Represents a conversation session for resume generation."""
    session_id: str
    messages: List[ConversationMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_exchanges: int = 10  # Maximum number of exchanges to keep
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "max_exchanges": self.max_exchanges
        }


class ConversationManager:
    """
    Manages conversation context for resume generation sessions.
    
    Provides methods to create sessions, append messages, retrieve history,
    and prune old messages to maintain token limits.
    """
    
    def __init__(self, max_exchanges: int = 10):
        """
        Initialize ConversationManager.
        
        Args:
            max_exchanges: Maximum number of user-assistant exchanges to keep (default: 10)
        """
        self.max_exchanges = max_exchanges
        self.sessions: Dict[str, ConversationSession] = {}
        msg.info(f"ConversationManager initialized with max_exchanges={max_exchanges}")
    
    def create_session(
        self,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation session.
        
        Args:
            session_id: Optional custom session ID (generates UUID if not provided)
            metadata: Optional metadata to attach to the session
            
        Returns:
            str: The session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id in self.sessions:
            msg.warn(f"Session {session_id} already exists, returning existing session")
            return session_id
        
        session = ConversationSession(
            session_id=session_id,
            metadata=metadata or {},
            max_exchanges=self.max_exchanges
        )
        
        self.sessions[session_id] = session
        msg.good(f"Created conversation session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Get a conversation session by ID.
        
        Args:
            session_id: The session ID to retrieve
            
        Returns:
            ConversationSession or None if not found
        """
        return self.sessions.get(session_id)
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: The session ID to check
            
        Returns:
            bool: True if session exists, False otherwise
        """
        return session_id in self.sessions
    
    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Append a message to a conversation session.
        
        Args:
            session_id: The session ID
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata for the message
            
        Returns:
            bool: True if successful, False if session not found
        """
        if session_id not in self.sessions:
            msg.warn(f"Session {session_id} not found, cannot append message")
            return False
        
        if role not in ["user", "assistant"]:
            msg.warn(f"Invalid role '{role}', must be 'user' or 'assistant'")
            return False
        
        session = self.sessions[session_id]
        
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.updated_at = datetime.now()
        
        # Prune if necessary
        self._prune_session(session_id)
        
        msg.info(f"Appended {role} message to session {session_id} ({len(session.messages)} total messages)")
        
        return True
    
    def append_user_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Append a user message to a conversation session.
        
        Args:
            session_id: The session ID
            content: Message content
            metadata: Optional metadata for the message
            
        Returns:
            bool: True if successful, False if session not found
        """
        return self.append_message(session_id, "user", content, metadata)
    
    def append_assistant_message(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Append an assistant message to a conversation session.
        
        Args:
            session_id: The session ID
            content: Message content
            metadata: Optional metadata for the message
            
        Returns:
            bool: True if successful, False if session not found
        """
        return self.append_message(session_id, "assistant", content, metadata)
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[ConversationMessage]:
        """
        Get messages from a conversation session.
        
        Args:
            session_id: The session ID
            limit: Optional limit on number of messages to return (most recent)
            
        Returns:
            List[ConversationMessage]: List of messages (empty if session not found)
        """
        if session_id not in self.sessions:
            msg.warn(f"Session {session_id} not found")
            return []
        
        session = self.sessions[session_id]
        messages = session.messages
        
        if limit is not None and limit > 0:
            messages = messages[-limit:]
        
        return messages
    
    def get_conversation_history(
        self,
        session_id: str,
        format: str = "list"
    ) -> Any:
        """
        Get conversation history in various formats.
        
        Args:
            session_id: The session ID
            format: Output format - "list" (default), "dict", or "openai"
            
        Returns:
            Conversation history in requested format
        """
        messages = self.get_messages(session_id)
        
        if format == "list":
            return messages
        
        elif format == "dict":
            return [msg.to_dict() for msg in messages]
        
        elif format == "openai":
            # Format for OpenAI API
            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
        
        else:
            msg.warn(f"Unknown format '{format}', returning list")
            return messages
    
    def _prune_session(self, session_id: str):
        """
        Prune old messages from a session to maintain token limits.
        
        Keeps only the last N exchanges (2N messages where N = max_exchanges).
        
        Args:
            session_id: The session ID to prune
        """
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        max_messages = session.max_exchanges * 2  # Each exchange = user + assistant
        
        if len(session.messages) > max_messages:
            removed_count = len(session.messages) - max_messages
            session.messages = session.messages[-max_messages:]
            msg.info(f"Pruned {removed_count} old messages from session {session_id}")
    
    def reset_session(self, session_id: str) -> bool:
        """
        Clear all messages from a conversation session.
        
        Args:
            session_id: The session ID to reset
            
        Returns:
            bool: True if successful, False if session not found
        """
        if session_id not in self.sessions:
            msg.warn(f"Session {session_id} not found, cannot reset")
            return False
        
        session = self.sessions[session_id]
        message_count = len(session.messages)
        session.messages = []
        session.updated_at = datetime.now()
        
        msg.good(f"Reset session {session_id} (removed {message_count} messages)")
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session entirely.
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            bool: True if successful, False if session not found
        """
        if session_id not in self.sessions:
            msg.warn(f"Session {session_id} not found, cannot delete")
            return False
        
        del self.sessions[session_id]
        msg.good(f"Deleted conversation session: {session_id}")
        
        return True
    
    def get_session_count(self) -> int:
        """
        Get the total number of active sessions.
        
        Returns:
            int: Number of active sessions
        """
        return len(self.sessions)
    
    def get_all_session_ids(self) -> List[str]:
        """
        Get all active session IDs.
        
        Returns:
            List[str]: List of session IDs
        """
        return list(self.sessions.keys())
    
    def update_session_metadata(
        self,
        session_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for a session.
        
        Args:
            session_id: The session ID
            metadata: Metadata to update (merged with existing)
            
        Returns:
            bool: True if successful, False if session not found
        """
        if session_id not in self.sessions:
            msg.warn(f"Session {session_id} not found, cannot update metadata")
            return False
        
        session = self.sessions[session_id]
        session.metadata.update(metadata)
        session.updated_at = datetime.now()
        
        msg.info(f"Updated metadata for session {session_id}")
        
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dict with session info or None if not found
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_id": session.session_id,
            "message_count": len(session.messages),
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "metadata": session.metadata,
            "max_exchanges": session.max_exchanges
        }
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Remove sessions that haven't been updated in a specified time.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            int: Number of sessions cleaned up
        """
        now = datetime.now()
        sessions_to_delete = []
        
        for session_id, session in self.sessions.items():
            age_hours = (now - session.updated_at).total_seconds() / 3600
            if age_hours > max_age_hours:
                sessions_to_delete.append(session_id)
        
        for session_id in sessions_to_delete:
            del self.sessions[session_id]
        
        if sessions_to_delete:
            msg.good(f"Cleaned up {len(sessions_to_delete)} old sessions")
        
        return len(sessions_to_delete)
