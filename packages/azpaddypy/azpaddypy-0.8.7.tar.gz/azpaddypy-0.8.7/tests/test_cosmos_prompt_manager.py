"""
Tests for the CosmosPromptManager tool.

This module tests the CosmosPromptManager functionality including
initialization, caching, CRUD operations, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, Any
import os
import sys
import importlib
from datetime import datetime

from azpaddypy.tools.cosmos_prompt_manager import CosmosPromptManager, create_cosmos_prompt_manager
from azpaddypy.resources.cosmosdb import AzureCosmosDB
from azpaddypy.mgmt.logging import AzureLogger


class TestCosmosPromptManager:
    """Test the CosmosPromptManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_cosmos_client = Mock(spec=AzureCosmosDB)
        self.mock_logger = Mock(spec=AzureLogger)
        
        # Configure mock logger
        self.mock_logger.create_span.return_value.__enter__ = Mock()
        self.mock_logger.create_span.return_value.__exit__ = Mock()
        
        self.prompt_manager = CosmosPromptManager(
            cosmos_client=self.mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test_prompt_manager",
            service_version="1.0.0",
            logger=self.mock_logger
        )

    def test_initialization(self):
        """Test CosmosPromptManager initialization."""
        assert self.prompt_manager.cosmos_client == self.mock_cosmos_client
        assert self.prompt_manager.database_name == "test_db"
        assert self.prompt_manager.container_name == "test_container"
        assert self.prompt_manager.service_name == "test_prompt_manager"
        assert self.prompt_manager.service_version == "1.0.0"

    def test_get_prompt_from_cosmos_db(self):
        """Test getting prompt from Cosmos DB."""
        # Mock Cosmos DB response
        mock_doc = {
            "id": "test_prompt",
            "name": "test_prompt",
            "prompt_template": "cosmos template"
        }
        
        self.mock_cosmos_client.read_item.return_value = mock_doc
        
        result = self.prompt_manager.get_prompt("test_prompt")
        
        assert result == "cosmos template"
        self.mock_cosmos_client.read_item.assert_called_once()
        self.mock_logger.info.assert_called_with("Loaded prompt from Cosmos DB: test_prompt")

    def test_get_prompt_not_found(self):
        """Test getting prompt that doesn't exist."""
        self.mock_cosmos_client.read_item.return_value = None
        
        result = self.prompt_manager.get_prompt("nonexistent_prompt")
        
        assert result is None
        self.mock_logger.warning.assert_called_with("Prompt not found in Cosmos DB: nonexistent_prompt")

    def test_save_prompt(self):
        """Test saving prompt to Cosmos DB."""
        # Mock successful upsert
        self.mock_cosmos_client.upsert_item.return_value = {"id": "test_prompt"}
        
        with patch.object(self.prompt_manager, '_create_prompt_document', return_value={}) as mock_create_doc:
            result = self.prompt_manager.save_prompt("test_prompt", {"prompt_template": "new template"})
            
            assert result is True
            mock_create_doc.assert_called_once_with(prompt_name="test_prompt", promt_data={"prompt_template": "new template"})
            self.mock_cosmos_client.upsert_item.assert_called_once()
            self.mock_logger.info.assert_called_with("Saved prompt to Cosmos DB: test_prompt")

    def test_save_prompt_error(self):
        """Test saving prompt with error."""
        self.mock_cosmos_client.upsert_item.side_effect = Exception("Test error")
        
        with patch.object(self.prompt_manager, '_create_prompt_document', return_value={}) as mock_create_doc:
            result = self.prompt_manager.save_prompt("test_prompt", {"prompt_template": "new template"})
        
            assert result is False
            self.mock_logger.error.assert_called()

    def test_list_prompts(self):
        """Test listing prompts."""
        # Mock query response
        mock_docs = [
            {"name": "prompt1"},
            {"name": "prompt2"}
        ]
        self.mock_cosmos_client.query_items.return_value = mock_docs
        
        result = self.prompt_manager.list_prompts()
        
        assert result == ["prompt1", "prompt2"]
        self.mock_cosmos_client.query_items.assert_called_once()

    def test_delete_prompt_success(self):
        """Test successful prompt deletion."""
        self.mock_cosmos_client.delete_item.return_value = True
        
        result = self.prompt_manager.delete_prompt("test_prompt")
        
        assert result is True
        self.mock_cosmos_client.delete_item.assert_called_once()
        self.mock_logger.info.assert_called_with("Deleted prompt from Cosmos DB: test_prompt")

    def test_delete_prompt_not_found(self):
        """Test deleting prompt that doesn't exist."""
        self.mock_cosmos_client.delete_item.return_value = False
        
        result = self.prompt_manager.delete_prompt("nonexistent_prompt")
        
        assert result is False
        self.mock_logger.warning.assert_called_with("Prompt not found for deletion: nonexistent_prompt")

    def test_get_prompt_details(self):
        """Test getting prompt details."""
        mock_doc = {
            "id": "test_prompt",
            "name": "test_prompt",
            "prompt_template": "cosmos template",
            "timestamp": "2023-01-01T00:00:00.000000Z"
        }
        self.mock_cosmos_client.read_item.return_value = mock_doc
        
        result = self.prompt_manager.get_prompt_details("test_prompt")
        
        assert result['id'] == mock_doc['id']
        assert result['name'] == mock_doc['name']
        assert result['prompt_template'] == mock_doc['prompt_template']
        assert 'timestamp' in result

        self.mock_cosmos_client.read_item.assert_called_once_with(
            database_name='test_db',
            container_name='test_container',
            item_id='test_prompt',
            partition_key='test_prompt'
        )

    def test_get_prompt_details_not_found(self):
        """Test getting details for a non-existent prompt."""
        self.mock_cosmos_client.read_item.return_value = None
        
        result = self.prompt_manager.get_prompt_details("nonexistent_prompt")
        
        assert result is None
        self.mock_logger.warning.assert_called_with(
            "Prompt not found in Cosmos DB: nonexistent_prompt"
        )

    def test_get_prompt_details_not_found_exception(self):
        """Test getting details for a non-existent prompt that raises an exception."""
        from azure.core.exceptions import ResourceNotFoundError
        self.mock_cosmos_client.read_item.side_effect = ResourceNotFoundError("Not found")
        
        result = self.prompt_manager.get_prompt_details("nonexistent_prompt")
        
        assert result is None
        self.mock_logger.warning.assert_called_with(
            "Prompt not found in Cosmos DB: nonexistent_prompt"
        )

    def test_get_all_prompt_details(self):
        """Test getting all prompt details."""
        mock_docs = [
            {
                "id": "prompt1",
                "name": "prompt1",
                "prompt_template": "template1",
                "timestamp": "2023-01-01T00:00:00.000000Z"
            },
            {
                "id": "prompt2",
                "name": "prompt2",
                "prompt_template": "template2",
                "timestamp": "2023-01-01T00:00:00.000000Z"
            }
        ]
        self.mock_cosmos_client.query_items.return_value = mock_docs
        
        result = self.prompt_manager.get_all_prompt_details()
        
        assert len(result) == 2
        assert result[0]["name"] == "prompt1"
        self.mock_cosmos_client.query_items.assert_called_once()
        
        # Check for the specific log call
        expected_log = f"Found {len(mock_docs)} prompts in Cosmos DB"
        log_found = any(
            call.args[0] == expected_log for call in self.mock_logger.debug.call_args_list
        )
        assert log_found, f"Log message '{expected_log}' not found"


class TestCreateCosmosPromptManager:
    """Test the factory function for CosmosPromptManager."""

    def test_create_cosmos_prompt_manager(self):
        """Test factory function creation."""
        mock_cosmos_client = Mock(spec=AzureCosmosDB)
        mock_logger = Mock(spec=AzureLogger)

        prompt_manager = create_cosmos_prompt_manager(
            cosmos_client=mock_cosmos_client,
            database_name="test_db",
            container_name="test_container",
            service_name="test_service",
            service_version="2.0.0",
            logger=mock_logger
        )

        assert isinstance(prompt_manager, CosmosPromptManager)
        assert prompt_manager.cosmos_client == mock_cosmos_client
        assert prompt_manager.database_name == "test_db"
        assert prompt_manager.service_name == "test_service"
        assert prompt_manager.service_version == "2.0.0"

    def test_create_cosmos_prompt_manager_with_defaults(self):
        """Test factory function with default values."""
        mock_cosmos_client = Mock(spec=AzureCosmosDB)

        prompt_manager = create_cosmos_prompt_manager(
            cosmos_client=mock_cosmos_client
        )

        assert prompt_manager.database_name == "prompts"
        assert prompt_manager.container_name == "prompts"
        assert prompt_manager.service_name == "azure_cosmos_prompt_manager"
        assert prompt_manager.service_version == "1.0.0"

