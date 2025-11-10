"""
WorkLogManager module for managing work log entries in Weaviate.

This module provides functionality to create, retrieve, update, and delete
work log entries that document daily work activities and accomplishments.
"""

from wasabi import msg
from weaviate.client import WeaviateAsyncClient
from weaviate.classes.query import Filter, Sort
from weaviate.collections.classes.data import DataObject
from datetime import datetime
from typing import List, Dict, Optional, Any
from uuid import UUID
import uuid


class WorkLogEntry:
    """Represents a work log entry with its properties."""
    
    def __init__(
        self,
        content: str,
        user_id: str,
        timestamp: Optional[datetime] = None,
        extracted_skills: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        entry_id: Optional[str] = None
    ):
        self.id = entry_id or str(uuid.uuid4())
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.user_id = user_id
        self.extracted_skills = extracted_skills or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert WorkLogEntry to dictionary for Weaviate storage."""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "extracted_skills": self.extracted_skills,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_weaviate_object(cls, weaviate_obj) -> "WorkLogEntry":
        """Create WorkLogEntry from Weaviate object."""
        props = weaviate_obj.properties
        return cls(
            content=props.get("content", ""),
            user_id=props.get("user_id", ""),
            timestamp=datetime.fromisoformat(props.get("timestamp")) if props.get("timestamp") else datetime.now(),
            extracted_skills=props.get("extracted_skills", []),
            metadata=props.get("metadata", {}),
            entry_id=str(weaviate_obj.uuid)
        )


class WorkLogManager:
    """
    Manages work log entries in Weaviate.
    
    Provides methods to create, retrieve, update, and delete work log entries
    with support for filtering by date range and user ID.
    """
    
    def __init__(self, collection_name: str = "VERBA_WorkLog"):
        """
        Initialize WorkLogManager.
        
        Args:
            collection_name: Name of the Weaviate collection for work logs
        """
        self.collection_name = collection_name
    
    async def create_log_entry(
        self,
        client: WeaviateAsyncClient,
        content: str,
        user_id: str,
        extracted_skills: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkLogEntry:
        """
        Create and store a work log entry in Weaviate.
        
        Args:
            client: Weaviate async client instance
            content: The work log entry content
            user_id: User who created the work log entry
            extracted_skills: Optional list of skills extracted from content
            metadata: Optional additional metadata
            
        Returns:
            WorkLogEntry: The created work log entry with assigned ID
            
        Raises:
            Exception: If Weaviate connection fails or entry creation fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            # Create work log entry
            entry = WorkLogEntry(
                content=content,
                user_id=user_id,
                extracted_skills=extracted_skills,
                metadata=metadata
            )
            
            # Get collection and insert
            collection = client.collections.get(self.collection_name)
            entry_uuid = await collection.data.insert(
                properties=entry.to_dict()
            )
            
            # Update entry with assigned UUID
            entry.id = str(entry_uuid)
            
            msg.good(f"Created work log entry: {entry.id}")
            return entry
            
        except Exception as e:
            msg.fail(f"Failed to create work log entry: {str(e)}")
            raise Exception(f"Failed to create work log entry: {str(e)}")
    
    async def get_log_entries(
        self,
        client: WeaviateAsyncClient,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkLogEntry]:
        """
        Retrieve work log entries with optional filtering.
        
        Args:
            client: Weaviate async client instance
            user_id: Optional filter by user ID
            start_date: Optional filter by start date (inclusive)
            end_date: Optional filter by end date (inclusive)
            limit: Maximum number of entries to return
            offset: Number of entries to skip for pagination
            
        Returns:
            List[WorkLogEntry]: List of matching work log entries
            
        Raises:
            Exception: If Weaviate connection fails or query fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Build filters
            filters = []
            
            if user_id:
                filters.append(Filter.by_property("user_id").equal(user_id))
            
            if start_date:
                filters.append(
                    Filter.by_property("timestamp").greater_or_equal(start_date.isoformat())
                )
            
            if end_date:
                filters.append(
                    Filter.by_property("timestamp").less_or_equal(end_date.isoformat())
                )
            
            # Combine filters with AND logic
            combined_filter = None
            if len(filters) == 1:
                combined_filter = filters[0]
            elif len(filters) > 1:
                combined_filter = filters[0]
                for f in filters[1:]:
                    combined_filter = combined_filter & f
            
            # Query with filters
            if combined_filter:
                response = await collection.query.fetch_objects(
                    filters=combined_filter,
                    limit=limit,
                    offset=offset,
                    sort=Sort.by_property("timestamp", ascending=False)
                )
            else:
                response = await collection.query.fetch_objects(
                    limit=limit,
                    offset=offset,
                    sort=Sort.by_property("timestamp", ascending=False)
                )
            
            # Convert to WorkLogEntry objects
            entries = [
                WorkLogEntry.from_weaviate_object(obj)
                for obj in response.objects
            ]
            
            msg.info(f"Retrieved {len(entries)} work log entries")
            return entries
            
        except Exception as e:
            msg.fail(f"Failed to retrieve work log entries: {str(e)}")
            raise Exception(f"Failed to retrieve work log entries: {str(e)}")
    
    async def update_log_entry(
        self,
        client: WeaviateAsyncClient,
        log_id: str,
        content: Optional[str] = None,
        extracted_skills: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkLogEntry:
        """
        Update an existing work log entry.
        
        Args:
            client: Weaviate async client instance
            log_id: UUID of the work log entry to update
            content: Optional new content
            extracted_skills: Optional new skills list
            metadata: Optional new metadata
            
        Returns:
            WorkLogEntry: The updated work log entry
            
        Raises:
            Exception: If entry not found or update fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Check if entry exists
            if not await collection.data.exists(UUID(log_id)):
                raise Exception(f"Work log entry not found: {log_id}")
            
            # Fetch existing entry
            existing_obj = await collection.query.fetch_object_by_id(UUID(log_id))
            existing_props = existing_obj.properties
            
            # Build updated properties
            updated_props = {
                "content": content if content is not None else existing_props.get("content"),
                "timestamp": existing_props.get("timestamp"),
                "user_id": existing_props.get("user_id"),
                "extracted_skills": extracted_skills if extracted_skills is not None else existing_props.get("extracted_skills", []),
                "metadata": metadata if metadata is not None else existing_props.get("metadata", {})
            }
            
            # Update in Weaviate
            await collection.data.update(
                uuid=UUID(log_id),
                properties=updated_props
            )
            
            # Fetch and return updated entry
            updated_obj = await collection.query.fetch_object_by_id(UUID(log_id))
            updated_entry = WorkLogEntry.from_weaviate_object(updated_obj)
            
            msg.good(f"Updated work log entry: {log_id}")
            return updated_entry
            
        except Exception as e:
            msg.fail(f"Failed to update work log entry: {str(e)}")
            raise Exception(f"Failed to update work log entry: {str(e)}")
    
    async def delete_log_entry(
        self,
        client: WeaviateAsyncClient,
        log_id: str
    ) -> bool:
        """
        Delete a work log entry from Weaviate.
        
        Args:
            client: Weaviate async client instance
            log_id: UUID of the work log entry to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            Exception: If entry not found or deletion fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Check if entry exists
            if not await collection.data.exists(UUID(log_id)):
                raise Exception(f"Work log entry not found: {log_id}")
            
            # Delete entry
            await collection.data.delete_by_id(UUID(log_id))
            
            msg.good(f"Deleted work log entry: {log_id}")
            return True
            
        except Exception as e:
            msg.fail(f"Failed to delete work log entry: {str(e)}")
            raise Exception(f"Failed to delete work log entry: {str(e)}")
    
    async def get_log_entry_by_id(
        self,
        client: WeaviateAsyncClient,
        log_id: str
    ) -> Optional[WorkLogEntry]:
        """
        Retrieve a single work log entry by ID.
        
        Args:
            client: Weaviate async client instance
            log_id: UUID of the work log entry
            
        Returns:
            Optional[WorkLogEntry]: The work log entry if found, None otherwise
            
        Raises:
            Exception: If Weaviate connection fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Check if entry exists
            if not await collection.data.exists(UUID(log_id)):
                msg.warn(f"Work log entry not found: {log_id}")
                return None
            
            # Fetch entry
            obj = await collection.query.fetch_object_by_id(UUID(log_id))
            entry = WorkLogEntry.from_weaviate_object(obj)
            
            return entry
            
        except Exception as e:
            msg.fail(f"Failed to retrieve work log entry: {str(e)}")
            raise Exception(f"Failed to retrieve work log entry: {str(e)}")
    
    async def count_log_entries(
        self,
        client: WeaviateAsyncClient,
        user_id: Optional[str] = None
    ) -> int:
        """
        Count total work log entries, optionally filtered by user.
        
        Args:
            client: Weaviate async client instance
            user_id: Optional filter by user ID
            
        Returns:
            int: Total count of matching entries
            
        Raises:
            Exception: If Weaviate connection fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Build filter if user_id provided
            filter_obj = None
            if user_id:
                filter_obj = Filter.by_property("user_id").equal(user_id)
            
            # Get count
            response = await collection.aggregate.over_all(
                total_count=True,
                filters=filter_obj
            )
            
            return response.total_count
            
        except Exception as e:
            msg.fail(f"Failed to count work log entries: {str(e)}")
            raise Exception(f"Failed to count work log entries: {str(e)}")
