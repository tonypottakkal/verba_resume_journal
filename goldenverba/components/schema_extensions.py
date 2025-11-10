"""
Schema extensions for resume-specific Weaviate collections.

This module defines the schema for WorkLog, Skill, and ResumeRecord collections
that extend the base Verba functionality with resume generation capabilities.
"""

from wasabi import msg
from weaviate.client import WeaviateAsyncClient
from weaviate.classes.config import Configure, Property, DataType
from typing import Optional


class SchemaExtensions:
    """Manages schema extensions for resume-specific collections."""

    def __init__(self):
        self.worklog_collection_name = "VERBA_WorkLog"
        self.skill_collection_name = "VERBA_Skill"
        self.resume_record_collection_name = "VERBA_ResumeRecord"

    async def verify_worklog_collection(
        self, client: WeaviateAsyncClient, vectorizer_config: Optional[dict] = None
    ) -> bool:
        """
        Verify and create WorkLog collection if it doesn't exist.

        Args:
            client: Weaviate async client instance
            vectorizer_config: Optional vectorizer configuration

        Returns:
            bool: True if collection exists or was created successfully
        """
        if not await client.collections.exists(self.worklog_collection_name):
            msg.info(
                f"Collection: {self.worklog_collection_name} does not exist, creating new collection."
            )
            try:
                # Create collection with properties
                collection = await client.collections.create(
                    name=self.worklog_collection_name,
                    properties=[
                        Property(
                            name="content",
                            data_type=DataType.TEXT,
                            description="The work log entry content",
                        ),
                        Property(
                            name="timestamp",
                            data_type=DataType.DATE,
                            description="When the work log entry was created",
                        ),
                        Property(
                            name="user_id",
                            data_type=DataType.TEXT,
                            description="User who created the work log entry",
                        ),
                        Property(
                            name="extracted_skills",
                            data_type=DataType.TEXT_ARRAY,
                            description="Skills extracted from the work log content",
                        ),
                        Property(
                            name="metadata",
                            data_type=DataType.OBJECT,
                            description="Additional metadata for the work log entry",
                        ),
                    ],
                    vectorizer_config=vectorizer_config or Configure.Vectorizer.none(),
                )
                if collection:
                    msg.good(f"Created collection: {self.worklog_collection_name}")
                    return True
                else:
                    msg.fail(f"Failed to create collection: {self.worklog_collection_name}")
                    return False
            except Exception as e:
                msg.fail(f"Error creating WorkLog collection: {str(e)}")
                return False
        else:
            return True

    async def verify_skill_collection(
        self, client: WeaviateAsyncClient
    ) -> bool:
        """
        Verify and create Skill collection if it doesn't exist.

        Args:
            client: Weaviate async client instance

        Returns:
            bool: True if collection exists or was created successfully
        """
        if not await client.collections.exists(self.skill_collection_name):
            msg.info(
                f"Collection: {self.skill_collection_name} does not exist, creating new collection."
            )
            try:
                # Create collection with properties
                # Skills don't need vectorization as they're primarily for aggregation
                collection = await client.collections.create(
                    name=self.skill_collection_name,
                    properties=[
                        Property(
                            name="name",
                            data_type=DataType.TEXT,
                            description="The skill name",
                        ),
                        Property(
                            name="category",
                            data_type=DataType.TEXT,
                            description="The skill category (e.g., programming, framework, tool)",
                        ),
                        Property(
                            name="proficiency_score",
                            data_type=DataType.NUMBER,
                            description="Calculated proficiency score for the skill",
                        ),
                        Property(
                            name="occurrence_count",
                            data_type=DataType.INT,
                            description="Number of times the skill appears in documents",
                        ),
                        Property(
                            name="source_documents",
                            data_type=DataType.TEXT_ARRAY,
                            description="UUIDs of documents where this skill was found",
                        ),
                        Property(
                            name="last_used",
                            data_type=DataType.DATE,
                            description="Most recent date the skill was mentioned",
                        ),
                    ],
                    vectorizer_config=Configure.Vectorizer.none(),
                )
                if collection:
                    msg.good(f"Created collection: {self.skill_collection_name}")
                    return True
                else:
                    msg.fail(f"Failed to create collection: {self.skill_collection_name}")
                    return False
            except Exception as e:
                msg.fail(f"Error creating Skill collection: {str(e)}")
                return False
        else:
            return True

    async def verify_resume_record_collection(
        self, client: WeaviateAsyncClient, vectorizer_config: Optional[dict] = None
    ) -> bool:
        """
        Verify and create ResumeRecord collection if it doesn't exist.

        Args:
            client: Weaviate async client instance
            vectorizer_config: Optional vectorizer configuration

        Returns:
            bool: True if collection exists or was created successfully
        """
        if not await client.collections.exists(self.resume_record_collection_name):
            msg.info(
                f"Collection: {self.resume_record_collection_name} does not exist, creating new collection."
            )
            try:
                # Create collection with properties
                collection = await client.collections.create(
                    name=self.resume_record_collection_name,
                    properties=[
                        Property(
                            name="resume_content",
                            data_type=DataType.TEXT,
                            description="The generated resume content",
                        ),
                        Property(
                            name="job_description",
                            data_type=DataType.TEXT,
                            description="The job description used to generate the resume",
                        ),
                        Property(
                            name="target_role",
                            data_type=DataType.TEXT,
                            description="The target job role for this resume",
                        ),
                        Property(
                            name="generated_at",
                            data_type=DataType.DATE,
                            description="When the resume was generated",
                        ),
                        Property(
                            name="format",
                            data_type=DataType.TEXT,
                            description="The resume format (markdown, pdf, docx)",
                        ),
                        Property(
                            name="source_log_ids",
                            data_type=DataType.TEXT_ARRAY,
                            description="UUIDs of work log entries used to generate this resume",
                        ),
                        Property(
                            name="metadata",
                            data_type=DataType.OBJECT,
                            description="Additional metadata for the resume record",
                        ),
                    ],
                    vectorizer_config=vectorizer_config or Configure.Vectorizer.none(),
                )
                if collection:
                    msg.good(f"Created collection: {self.resume_record_collection_name}")
                    return True
                else:
                    msg.fail(f"Failed to create collection: {self.resume_record_collection_name}")
                    return False
            except Exception as e:
                msg.fail(f"Error creating ResumeRecord collection: {str(e)}")
                return False
        else:
            return True

    async def initialize_all_collections(
        self, 
        client: WeaviateAsyncClient,
        vectorizer_config: Optional[dict] = None
    ) -> bool:
        """
        Initialize all resume-specific collections.

        Args:
            client: Weaviate async client instance
            vectorizer_config: Optional vectorizer configuration for collections that need it

        Returns:
            bool: True if all collections were initialized successfully
        """
        try:
            worklog_ok = await self.verify_worklog_collection(client, vectorizer_config)
            skill_ok = await self.verify_skill_collection(client)
            resume_ok = await self.verify_resume_record_collection(client, vectorizer_config)

            if worklog_ok and skill_ok and resume_ok:
                msg.good("All resume-specific collections initialized successfully")
                return True
            else:
                msg.fail("Failed to initialize some resume-specific collections")
                return False
        except Exception as e:
            msg.fail(f"Error initializing resume collections: {str(e)}")
            return False

    async def delete_all_collections(self, client: WeaviateAsyncClient) -> bool:
        """
        Delete all resume-specific collections. Use with caution!

        Args:
            client: Weaviate async client instance

        Returns:
            bool: True if all collections were deleted successfully
        """
        try:
            collections_to_delete = [
                self.worklog_collection_name,
                self.skill_collection_name,
                self.resume_record_collection_name,
            ]

            for collection_name in collections_to_delete:
                if await client.collections.exists(collection_name):
                    await client.collections.delete(collection_name)
                    msg.info(f"Deleted collection: {collection_name}")

            msg.good("All resume-specific collections deleted successfully")
            return True
        except Exception as e:
            msg.fail(f"Error deleting resume collections: {str(e)}")
            return False
