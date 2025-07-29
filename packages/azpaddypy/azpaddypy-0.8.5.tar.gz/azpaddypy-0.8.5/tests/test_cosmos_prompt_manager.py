"""
Tests for the CosmosPromptManager tool.

This module tests the CosmosPromptManager functionality including
initialization, caching, CRUD operations, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import os
import sys
import importlib

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
            logger=self.mock_logger,
            cache_ttl=300
        )

    def test_initialization(self):
        """Test CosmosPromptManager initialization."""
        assert self.prompt_manager.cosmos_client == self.mock_cosmos_client
        assert self.prompt_manager.database_name == "test_db"
        assert self.prompt_manager.container_name == "test_container"
        assert self.prompt_manager.service_name == "test_prompt_manager"
        assert self.prompt_manager.service_version == "1.0.0"
        assert self.prompt_manager.cache_ttl == 300
        assert self.prompt_manager.cache == {}

    def test_get_cache_key(self):
        """Test cache key generation."""
        cache_key = self.prompt_manager._get_cache_key("test_prompt")
        assert cache_key == "prompt:test_prompt"

    def test_is_cache_valid(self):
        """Test cache validation logic."""
        import time
        
        # Valid cache entry
        valid_entry = {"data": "test", "timestamp": time.time()}
        assert self.prompt_manager._is_cache_valid(valid_entry) is True
        
        # Expired cache entry
        expired_entry = {"data": "test", "timestamp": time.time() - 400}
        assert self.prompt_manager._is_cache_valid(expired_entry) is False

    def test_create_prompt_document(self):
        """Test prompt document creation."""
        doc = self.prompt_manager._create_prompt_document("test_prompt", "test template")
        
        assert doc["id"] == "test_prompt"
        assert doc["name"] == "test_prompt"
        assert doc["prompt_template"] == "test template"
        assert "created_at" in doc
        assert "updated_at" in doc

    def test_get_prompt_from_cache(self):
        """Test getting prompt from cache."""
        import time
        
        # Setup cache
        cache_key = self.prompt_manager._get_cache_key("test_prompt")
        self.prompt_manager.cache[cache_key] = {
            "data": "cached template",
            "timestamp": time.time()
        }
        
        # Mock logger
        self.mock_logger.debug.return_value = None
        
        result = self.prompt_manager.get_prompt("test_prompt")
        
        assert result == "cached template"
        self.mock_logger.debug.assert_called_with("Returning cached prompt: test_prompt")

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
        
        result = self.prompt_manager.save_prompt("test_prompt", "new template")
        
        assert result is True
        self.mock_cosmos_client.upsert_item.assert_called_once()
        self.mock_logger.info.assert_called_with("Saved prompt to Cosmos DB: test_prompt")

    def test_save_prompt_error(self):
        """Test saving prompt with error."""
        self.mock_cosmos_client.upsert_item.side_effect = Exception("Test error")
        
        result = self.prompt_manager.save_prompt("test_prompt", "new template")
        
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

    def test_clear_cache(self):
        """Test cache clearing."""
        # Setup cache
        self.prompt_manager.cache["prompt:test1"] = {"data": "test1", "timestamp": 100}
        self.prompt_manager.cache["prompt:test2"] = {"data": "test2", "timestamp": 200}
        
        self.prompt_manager.clear_cache()
        
        assert len(self.prompt_manager.cache) == 0
        self.mock_logger.info.assert_called_with("Prompt cache cleared (2 entries removed)")

    def test_get_cache_info(self):
        """Test cache information retrieval."""
        import time
        
        # Setup cache with valid and expired entries
        current_time = time.time()
        self.prompt_manager.cache["prompt:valid"] = {"data": "valid", "timestamp": current_time}
        self.prompt_manager.cache["prompt:expired"] = {"data": "expired", "timestamp": current_time - 400}
        
        cache_info = self.prompt_manager.get_cache_info()
        
        assert cache_info["total_entries"] == 2
        assert cache_info["valid_entries"] == 1
        assert cache_info["expired_entries"] == 1
        assert len(cache_info["cache_details"]) == 2


    def test_get_prompt_details(self):
        """Test getting prompt details."""
        mock_doc = {
            "id": "test_prompt",
            "name": "test_prompt",
            "prompt_template": "cosmos template",
            "created_at": 1678886400,
            "updated_at": 1678886400
        }
        self.mock_cosmos_client.read_item.return_value = mock_doc
        
        result = self.prompt_manager.get_prompt_details("test_prompt")
        
        assert result == mock_doc
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
                "created_at": 1678886400,
                "updated_at": 1678886400
            },
            {
                "id": "prompt2",
                "name": "prompt2",
                "prompt_template": "template2",
                "created_at": 1678886401,
                "updated_at": 1678886401
            }
        ]
        self.mock_cosmos_client.query_items.return_value = mock_docs
        
        result = self.prompt_manager.get_all_prompt_details()
        
        assert result == mock_docs
        self.mock_cosmos_client.query_items.assert_called_once()

    def test_migrate_from_json_success(self):
        """Test successful migration from JSON file."""
        json_content = '{"prompt_template": "migrated template"}'
        prompt_name = "migrated_prompt"
        
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json_content
            self.mock_cosmos_client.upsert_item.return_value = {"id": prompt_name}
            
            result = self.prompt_manager.migrate_from_json("dummy.json", prompt_name)
            
            assert result is True
            self.mock_cosmos_client.upsert_item.assert_called_once()
            self.mock_logger.info.assert_called_with(f"Successfully migrated prompt '{prompt_name}' from JSON.")

    def test_migrate_from_json_file_not_found(self):
        """Test migration with file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            result = self.prompt_manager.migrate_from_json("nonexistent.json", "test_prompt")
            
            assert result is False
            self.mock_logger.error.assert_called_with(
                "Error migrating prompt 'test_prompt' from JSON: File not found",
                exc_info=True
            )

    def test_migrate_from_json_invalid_json(self):
        """Test migration with invalid JSON content."""
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "invalid json"
            
            result = self.prompt_manager.migrate_from_json("invalid.json", "test_prompt")
            
            assert result is False
            self.mock_logger.error.assert_called()


class TestCreateCosmosPromptManager:
    """Test the factory function."""

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
            logger=mock_logger,
            cache_ttl=600
        )
        
        assert isinstance(prompt_manager, CosmosPromptManager)
        assert prompt_manager.cosmos_client == mock_cosmos_client
        assert prompt_manager.database_name == "test_db"
        assert prompt_manager.container_name == "test_container"
        assert prompt_manager.service_name == "test_service"
        assert prompt_manager.service_version == "2.0.0"
        assert prompt_manager.cache_ttl == 600
        assert prompt_manager.logger == mock_logger

