"""
Tests for schema extensions module.

This module tests the creation and initialization of resume-specific
Weaviate collections.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from goldenverba.components.schema_extensions import SchemaExtensions


class TestSchemaExtensions:
    """Test suite for SchemaExtensions class."""

    @pytest.fixture
    def schema_extensions(self):
        """Create a SchemaExtensions instance for testing."""
        return SchemaExtensions()

    @pytest.fixture
    def mock_client(self):
        """Create a mock Weaviate client."""
        client = AsyncMock()
        client.collections = MagicMock()
        client.collections.exists = AsyncMock()
        client.collections.create = AsyncMock()
        client.collections.delete = AsyncMock()
        return client

    def test_initialization(self, schema_extensions):
        """Test that SchemaExtensions initializes with correct collection names."""
        assert schema_extensions.worklog_collection_name == "VERBA_WorkLog"
        assert schema_extensions.skill_collection_name == "VERBA_Skill"
        assert schema_extensions.resume_record_collection_name == "VERBA_ResumeRecord"

    @pytest.mark.asyncio
    async def test_verify_worklog_collection_creates_new(
        self, schema_extensions, mock_client
    ):
        """Test that WorkLog collection is created when it doesn't exist."""
        mock_client.collections.exists.return_value = False
        mock_collection = MagicMock()
        mock_client.collections.create.return_value = mock_collection

        result = await schema_extensions.verify_worklog_collection(mock_client)

        assert result is True
        mock_client.collections.exists.assert_called_once_with("VERBA_WorkLog")
        mock_client.collections.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_worklog_collection_exists(
        self, schema_extensions, mock_client
    ):
        """Test that WorkLog collection verification succeeds when it exists."""
        mock_client.collections.exists.return_value = True

        result = await schema_extensions.verify_worklog_collection(mock_client)

        assert result is True
        mock_client.collections.exists.assert_called_once_with("VERBA_WorkLog")
        mock_client.collections.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_verify_skill_collection_creates_new(
        self, schema_extensions, mock_client
    ):
        """Test that Skill collection is created when it doesn't exist."""
        mock_client.collections.exists.return_value = False
        mock_collection = MagicMock()
        mock_client.collections.create.return_value = mock_collection

        result = await schema_extensions.verify_skill_collection(mock_client)

        assert result is True
        mock_client.collections.exists.assert_called_once_with("VERBA_Skill")
        mock_client.collections.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_resume_record_collection_creates_new(
        self, schema_extensions, mock_client
    ):
        """Test that ResumeRecord collection is created when it doesn't exist."""
        mock_client.collections.exists.return_value = False
        mock_collection = MagicMock()
        mock_client.collections.create.return_value = mock_collection

        result = await schema_extensions.verify_resume_record_collection(mock_client)

        assert result is True
        mock_client.collections.exists.assert_called_once_with("VERBA_ResumeRecord")
        mock_client.collections.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_all_collections_success(
        self, schema_extensions, mock_client
    ):
        """Test that all collections are initialized successfully."""
        mock_client.collections.exists.return_value = False
        mock_collection = MagicMock()
        mock_client.collections.create.return_value = mock_collection

        result = await schema_extensions.initialize_all_collections(mock_client)

        assert result is True
        # Should check existence of all three collections
        assert mock_client.collections.exists.call_count == 3

    @pytest.mark.asyncio
    async def test_initialize_all_collections_handles_error(
        self, schema_extensions, mock_client
    ):
        """Test that initialization handles errors gracefully."""
        mock_client.collections.exists.side_effect = Exception("Connection error")

        result = await schema_extensions.initialize_all_collections(mock_client)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_all_collections(self, schema_extensions, mock_client):
        """Test that all collections can be deleted."""
        mock_client.collections.exists.return_value = True

        result = await schema_extensions.delete_all_collections(mock_client)

        assert result is True
        # Should check existence and delete all three collections
        assert mock_client.collections.exists.call_count == 3
        assert mock_client.collections.delete.call_count == 3
