"""
ResumeTracker module for managing resume records in Weaviate.

This module provides functionality to save, retrieve, and manage resume records
along with their associated job descriptions and metadata.
"""

from wasabi import msg
from weaviate.client import WeaviateAsyncClient
from weaviate.classes.query import Filter, Sort
from weaviate.collections.classes.data import DataObject
from datetime import datetime
from typing import List, Dict, Optional, Any
from uuid import UUID
import uuid


class ResumeRecord:
    """Represents a resume record with its properties."""
    
    def __init__(
        self,
        resume_content: str,
        job_description: str,
        target_role: str,
        generated_at: Optional[datetime] = None,
        format: str = "markdown",
        source_log_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None
    ):
        self.id = record_id or str(uuid.uuid4())
        self.resume_content = resume_content
        self.job_description = job_description
        self.target_role = target_role
        self.generated_at = generated_at or datetime.now()
        self.format = format
        self.source_log_ids = source_log_ids or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ResumeRecord to dictionary for Weaviate storage."""
        return {
            "resume_content": self.resume_content,
            "job_description": self.job_description,
            "target_role": self.target_role,
            "generated_at": self.generated_at.isoformat(),
            "format": self.format,
            "source_log_ids": self.source_log_ids,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_weaviate_object(cls, weaviate_obj) -> "ResumeRecord":
        """Create ResumeRecord from Weaviate object."""
        props = weaviate_obj.properties
        return cls(
            resume_content=props.get("resume_content", ""),
            job_description=props.get("job_description", ""),
            target_role=props.get("target_role", ""),
            generated_at=datetime.fromisoformat(props.get("generated_at")) if props.get("generated_at") else datetime.now(),
            format=props.get("format", "markdown"),
            source_log_ids=props.get("source_log_ids", []),
            metadata=props.get("metadata", {}),
            record_id=str(weaviate_obj.uuid)
        )


class ResumeTracker:
    """
    Manages resume records in Weaviate.
    
    Provides methods to save, retrieve, and manage resume records with their
    associated job descriptions and metadata for tracking application history.
    """
    
    def __init__(self, collection_name: str = "VERBA_ResumeRecord"):
        """
        Initialize ResumeTracker.
        
        Args:
            collection_name: Name of the Weaviate collection for resume records
        """
        self.collection_name = collection_name
    
    async def save_resume_record(
        self,
        client: WeaviateAsyncClient,
        resume_content: str,
        job_description: str,
        target_role: str,
        format: str = "markdown",
        source_log_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ResumeRecord:
        """
        Store a resume record with associated job description in Weaviate.
        
        Args:
            client: Weaviate async client instance
            resume_content: The generated resume content
            job_description: The job description used to generate the resume
            target_role: The target job role for this resume
            format: The resume format (markdown, pdf, docx)
            source_log_ids: Optional list of work log entry UUIDs used
            metadata: Optional additional metadata
            
        Returns:
            ResumeRecord: The created resume record with assigned ID
            
        Raises:
            Exception: If Weaviate connection fails or record creation fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            # Create resume record
            record = ResumeRecord(
                resume_content=resume_content,
                job_description=job_description,
                target_role=target_role,
                format=format,
                source_log_ids=source_log_ids,
                metadata=metadata
            )
            
            # Get collection and insert
            collection = client.collections.get(self.collection_name)
            record_uuid = await collection.data.insert(
                properties=record.to_dict()
            )
            
            # Update record with assigned UUID
            record.id = str(record_uuid)
            
            msg.good(f"Saved resume record: {record.id}")
            return record
            
        except Exception as e:
            msg.fail(f"Failed to save resume record: {str(e)}")
            raise Exception(f"Failed to save resume record: {str(e)}")
    
    async def get_resume_history(
        self,
        client: WeaviateAsyncClient,
        target_role: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ResumeRecord]:
        """
        Retrieve resume records with optional filtering and pagination.
        
        Args:
            client: Weaviate async client instance
            target_role: Optional filter by target role
            start_date: Optional filter by start date (inclusive)
            end_date: Optional filter by end date (inclusive)
            format: Optional filter by resume format
            limit: Maximum number of records to return
            offset: Number of records to skip for pagination
            
        Returns:
            List[ResumeRecord]: List of matching resume records
            
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
            
            if target_role:
                filters.append(Filter.by_property("target_role").equal(target_role))
            
            if format:
                filters.append(Filter.by_property("format").equal(format))
            
            if start_date:
                filters.append(
                    Filter.by_property("generated_at").greater_or_equal(start_date.isoformat())
                )
            
            if end_date:
                filters.append(
                    Filter.by_property("generated_at").less_or_equal(end_date.isoformat())
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
                    sort=Sort.by_property("generated_at", ascending=False)
                )
            else:
                response = await collection.query.fetch_objects(
                    limit=limit,
                    offset=offset,
                    sort=Sort.by_property("generated_at", ascending=False)
                )
            
            # Convert to ResumeRecord objects
            records = [
                ResumeRecord.from_weaviate_object(obj)
                for obj in response.objects
            ]
            
            msg.info(f"Retrieved {len(records)} resume records")
            return records
            
        except Exception as e:
            msg.fail(f"Failed to retrieve resume history: {str(e)}")
            raise Exception(f"Failed to retrieve resume history: {str(e)}")
    
    async def get_resume_by_id(
        self,
        client: WeaviateAsyncClient,
        resume_id: str
    ) -> Optional[ResumeRecord]:
        """
        Retrieve a single resume record by ID.
        
        Args:
            client: Weaviate async client instance
            resume_id: UUID of the resume record
            
        Returns:
            Optional[ResumeRecord]: The resume record if found, None otherwise
            
        Raises:
            Exception: If Weaviate connection fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Check if record exists
            if not await collection.data.exists(UUID(resume_id)):
                msg.warn(f"Resume record not found: {resume_id}")
                return None
            
            # Fetch record
            obj = await collection.query.fetch_object_by_id(UUID(resume_id))
            record = ResumeRecord.from_weaviate_object(obj)
            
            return record
            
        except Exception as e:
            msg.fail(f"Failed to retrieve resume record: {str(e)}")
            raise Exception(f"Failed to retrieve resume record: {str(e)}")
    
    async def delete_resume_record(
        self,
        client: WeaviateAsyncClient,
        resume_id: str
    ) -> bool:
        """
        Remove a resume record from history.
        
        Args:
            client: Weaviate async client instance
            resume_id: UUID of the resume record to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            Exception: If record not found or deletion fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Check if record exists
            if not await collection.data.exists(UUID(resume_id)):
                raise Exception(f"Resume record not found: {resume_id}")
            
            # Delete record
            await collection.data.delete_by_id(UUID(resume_id))
            
            msg.good(f"Deleted resume record: {resume_id}")
            return True
            
        except Exception as e:
            msg.fail(f"Failed to delete resume record: {str(e)}")
            raise Exception(f"Failed to delete resume record: {str(e)}")
    
    async def update_resume_record(
        self,
        client: WeaviateAsyncClient,
        resume_id: str,
        resume_content: Optional[str] = None,
        job_description: Optional[str] = None,
        target_role: Optional[str] = None,
        format: Optional[str] = None,
        source_log_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ResumeRecord:
        """
        Update an existing resume record.
        
        Args:
            client: Weaviate async client instance
            resume_id: UUID of the resume record to update
            resume_content: Optional new resume content
            job_description: Optional new job description
            target_role: Optional new target role
            format: Optional new format
            source_log_ids: Optional new source log IDs
            metadata: Optional new metadata
            
        Returns:
            ResumeRecord: The updated resume record
            
        Raises:
            Exception: If record not found or update fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Check if record exists
            if not await collection.data.exists(UUID(resume_id)):
                raise Exception(f"Resume record not found: {resume_id}")
            
            # Fetch existing record
            existing_obj = await collection.query.fetch_object_by_id(UUID(resume_id))
            existing_props = existing_obj.properties
            
            # Build updated properties
            updated_props = {
                "resume_content": resume_content if resume_content is not None else existing_props.get("resume_content"),
                "job_description": job_description if job_description is not None else existing_props.get("job_description"),
                "target_role": target_role if target_role is not None else existing_props.get("target_role"),
                "generated_at": existing_props.get("generated_at"),
                "format": format if format is not None else existing_props.get("format"),
                "source_log_ids": source_log_ids if source_log_ids is not None else existing_props.get("source_log_ids", []),
                "metadata": metadata if metadata is not None else existing_props.get("metadata", {})
            }
            
            # Update in Weaviate
            await collection.data.update(
                uuid=UUID(resume_id),
                properties=updated_props
            )
            
            # Fetch and return updated record
            updated_obj = await collection.query.fetch_object_by_id(UUID(resume_id))
            updated_record = ResumeRecord.from_weaviate_object(updated_obj)
            
            msg.good(f"Updated resume record: {resume_id}")
            return updated_record
            
        except Exception as e:
            msg.fail(f"Failed to update resume record: {str(e)}")
            raise Exception(f"Failed to update resume record: {str(e)}")
    
    async def count_resume_records(
        self,
        client: WeaviateAsyncClient,
        target_role: Optional[str] = None
    ) -> int:
        """
        Count total resume records, optionally filtered by target role.
        
        Args:
            client: Weaviate async client instance
            target_role: Optional filter by target role
            
        Returns:
            int: Total count of matching records
            
        Raises:
            Exception: If Weaviate connection fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Build filter if target_role provided
            filter_obj = None
            if target_role:
                filter_obj = Filter.by_property("target_role").equal(target_role)
            
            # Get count
            response = await collection.aggregate.over_all(
                total_count=True,
                filters=filter_obj
            )
            
            return response.total_count
            
        except Exception as e:
            msg.fail(f"Failed to count resume records: {str(e)}")
            raise Exception(f"Failed to count resume records: {str(e)}")
    
    async def search_resumes_by_keyword(
        self,
        client: WeaviateAsyncClient,
        keyword: str,
        limit: int = 20
    ) -> List[ResumeRecord]:
        """
        Search resume records by keyword in content or job description.
        
        Args:
            client: Weaviate async client instance
            keyword: Keyword to search for
            limit: Maximum number of records to return
            
        Returns:
            List[ResumeRecord]: List of matching resume records
            
        Raises:
            Exception: If Weaviate connection fails or search fails
        """
        try:
            # Verify collection exists
            if not await client.collections.exists(self.collection_name):
                raise Exception(f"Collection {self.collection_name} does not exist")
            
            collection = client.collections.get(self.collection_name)
            
            # Search using BM25 keyword search
            response = await collection.query.bm25(
                query=keyword,
                limit=limit
            )
            
            # Convert to ResumeRecord objects
            records = [
                ResumeRecord.from_weaviate_object(obj)
                for obj in response.objects
            ]
            
            msg.info(f"Found {len(records)} resume records matching keyword: {keyword}")
            return records
            
        except Exception as e:
            msg.fail(f"Failed to search resume records: {str(e)}")
            raise Exception(f"Failed to search resume records: {str(e)}")
