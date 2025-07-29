"""
Azure Cosmos DB Prompt Management Tool.

This module provides a comprehensive prompt management system using Azure Cosmos DB
for storing and retrieving prompts with real-time updates and caching.

Features:
- Simple prompt storage in Cosmos DB
- Real-time updates across all instances
- Caching for performance optimization
- Backward compatibility with existing system
- Standardized azpaddypy logging and error handling
"""

import json
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from azure.core.exceptions import ResourceNotFoundError
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

from ..resources.cosmosdb import AzureCosmosDB
from ..mgmt.logging import AzureLogger
from ..mgmt.identity import AzureIdentity


class CosmosPromptManager:
    """
    Azure Cosmos DB-based prompt management tool with standardized client initialization,
    caching, and both synchronous and asynchronous operations.
    
    This tool follows the azpaddypy pattern for Azure resource management with
    proper logging, error handling, and configuration management.
    """

    def __init__(
        self,
        cosmos_client: AzureCosmosDB,
        database_name: str = "prompts",
        container_name: str = "prompts",
        service_name: str = "azure_cosmos_prompt_manager",
        service_version: str = "1.0.0",
        logger: Optional[AzureLogger] = None,
        cache_ttl: int = 300,  # 5 minutes default
    ):
        self.cosmos_client = cosmos_client
        self.database_name = database_name
        self.container_name = container_name
        self.service_name = service_name
        self.service_version = service_version
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}

        if logger:
            self.logger = logger
        else:
            self.logger = AzureLogger(
                service_name=service_name,
                service_version=service_version,
                enable_console_logging=True,
            )

        self.logger.info(
            f"Cosmos Prompt Manager initialized for service '{service_name}' v{service_version}",
            extra={
                "database_name": database_name,
                "container_name": container_name,
                "cache_ttl": cache_ttl
            }
        )

    def _get_cache_key(self, prompt_name: str) -> str:
        """Generate cache key for prompt."""
        return f"prompt:{prompt_name}"

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cached data is still valid."""
        return time.time() - cache_entry['timestamp'] < self.cache_ttl

    def _create_prompt_document(self, prompt_name: str, prompt_template: str) -> Dict[str, Any]:
        """Create Cosmos DB document from prompt data."""
        return {
            "id": prompt_name,
            "name": prompt_name,
            "prompt_template": prompt_template,
            "created_at": time.time(),
            "updated_at": time.time()
        }

    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Get prompt template from Cosmos DB with caching.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Prompt template if found, None otherwise
        """
        cache_key = self._get_cache_key(prompt_name)
        
        with self.logger.create_span("CosmosPromptManager.get_prompt", attributes={"prompt_name": prompt_name}):
            # Check cache first
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if self._is_cache_valid(cached_data):
                    self.logger.debug(f"Returning cached prompt: {prompt_name}")
                    return cached_data['data']
            
            # Load from Cosmos DB
            try:
                doc = self.cosmos_client.read_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name,
                    max_integrated_cache_staleness_in_ms=5000  # 5 seconds, adjust as needed
                )
                
                # Check if document was found
                if doc is None:
                    self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                    return None
                
                prompt_template = doc.get("prompt_template", "")
                
                # Cache the result
                self.cache[cache_key] = {
                    'data': prompt_template,
                    'timestamp': time.time()
                }
                
                self.logger.info(f"Loaded prompt from Cosmos DB: {prompt_name}")
                return prompt_template
                
            except ResourceNotFoundError:
                self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                return None
            except Exception as e:
                self.logger.error(f"Error loading prompt {prompt_name}: {e}", exc_info=True)
                return None

    def save_prompt(self, prompt_name: str, prompt_template: str) -> bool:
        """
        Save prompt to Cosmos DB.
        
        Args:
            prompt_name: Name of the prompt
            prompt_template: Template content
            
        Returns:
            True if successful, False otherwise
        """
        with self.logger.create_span("CosmosPromptManager.save_prompt", attributes={"prompt_name": prompt_name}):
            try:
                # Create document
                doc = self._create_prompt_document(prompt_name, prompt_template)
                
                # Save to Cosmos DB
                self.cosmos_client.upsert_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item=doc
                )
                
                # Invalidate cache
                cache_key = self._get_cache_key(prompt_name)
                self.cache.pop(cache_key, None)
                
                self.logger.info(f"Saved prompt to Cosmos DB: {prompt_name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error saving prompt {prompt_name}: {e}", exc_info=True)
                return False

    def list_prompts(self) -> List[str]:
        """
        List all prompt names.
        
        Returns:
            List of prompt names
        """
        with self.logger.create_span("CosmosPromptManager.list_prompts"):
            try:
                query = "SELECT c.name FROM c"
                
                docs = self.cosmos_client.query_items(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    query=query
                )
                
                prompt_names = [doc["name"] for doc in docs]
                self.logger.debug(f"Found {len(prompt_names)} prompts in Cosmos DB")
                return prompt_names
                
            except Exception as e:
                self.logger.error(f"Error listing prompts: {e}", exc_info=True)
                return []

    def delete_prompt(self, prompt_name: str) -> bool:
        """
        Delete a prompt from Cosmos DB.
        
        Args:
            prompt_name: Name of prompt to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self.logger.create_span("CosmosPromptManager.delete_prompt", attributes={"prompt_name": prompt_name}):
            try:
                success = self.cosmos_client.delete_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name
                )
                
                if success:
                    # Invalidate cache
                    cache_key = self._get_cache_key(prompt_name)
                    self.cache.pop(cache_key, None)
                    
                    self.logger.info(f"Deleted prompt from Cosmos DB: {prompt_name}")
                    return True
                else:
                    self.logger.warning(f"Prompt not found for deletion: {prompt_name}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error deleting prompt {prompt_name}: {e}", exc_info=True)
                return False

    def clear_cache(self):
        """Clear all cached prompts."""
        with self.logger.create_span("CosmosPromptManager.clear_cache"):
            cache_size = len(self.cache)
            self.cache.clear()
            self.logger.info(f"Prompt cache cleared ({cache_size} entries removed)")

    def migrate_from_json(self, json_file_path: str, prompt_name: str) -> bool:
        """
        Migrate a prompt from JSON file to Cosmos DB.
        
        Args:
            json_file_path: Path to JSON file containing prompt
            prompt_name: Name to save prompt as in Cosmos DB
            
        Returns:
            True if successful, False otherwise
        """
        with self.logger.create_span("CosmosPromptManager.migrate_from_json", attributes={"prompt_name": prompt_name}):
            try:
                with open(json_file_path, 'r') as f:
                    data = json.load(f)
                
                prompt_template = data.get("prompt_template", "")
                
                if self.save_prompt(prompt_name, prompt_template):
                    self.logger.info(f"Successfully migrated prompt '{prompt_name}' from JSON.")
                    return True
                else:
                    self.logger.error(f"Failed to save migrated prompt '{prompt_name}' to Cosmos DB.")
                    return False

            except FileNotFoundError:
                self.logger.error(f"Error migrating prompt '{prompt_name}' from JSON: File not found", exc_info=True)
                return False
            except Exception as e:
                self.logger.error(f"Error migrating prompt '{prompt_name}' from JSON: {e}", exc_info=True)
                return False

    def get_prompt_details(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific prompt.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Dictionary with prompt details if found, None otherwise
        """
        with self.logger.create_span("CosmosPromptManager.get_prompt_details", attributes={"prompt_name": prompt_name}):
            try:
                doc = self.cosmos_client.read_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name
                )
                
                if doc is None:
                    self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                    return None
                
                self.logger.info(f"Retrieved details for prompt: {prompt_name}")
                return {
                    "id": doc.get("id"),
                    "name": doc.get("name"),
                    "prompt_template": doc.get("prompt_template"),
                    "created_at": doc.get("created_at"),
                    "updated_at": doc.get("updated_at")
                }
            except ResourceNotFoundError:
                self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                return None
            except Exception as e:
                self.logger.error(f"Error getting details for prompt {prompt_name}: {e}", exc_info=True)
                return None

    def get_all_prompt_details(self) -> List[Dict[str, Any]]:
        """
        Get details for all prompts.
        
        Returns:
            List of dictionaries with prompt details
        """
        with self.logger.create_span("CosmosPromptManager.get_all_prompt_details"):
            try:
                query = "SELECT * FROM c"
                
                docs = self.cosmos_client.query_items(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    query=query
                )
                
                detailed_prompts = [
                    {
                        "id": doc.get("id"),
                        "name": doc.get("name"),
                        "prompt_template": doc.get("prompt_template"),
                        "created_at": doc.get("created_at"),
                        "updated_at": doc.get("updated_at")
                    }
                    for doc in docs
                ]
                
                self.logger.debug(f"Found {len(detailed_prompts)} prompts in Cosmos DB")
                return detailed_prompts
                
            except Exception as e:
                self.logger.error(f"Error getting all prompt details: {e}", exc_info=True)
                return []

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the prompt cache.
        
        Returns:
            Dictionary with cache information
        """
        with self.logger.create_span("CosmosPromptManager.get_cache_info"):
            current_time = time.time()
            valid_entries = 0
            expired_entries = 0
            cache_details = []
            
            for key, entry in self.cache.items():
                age_seconds = current_time - entry['timestamp']
                is_valid = self._is_cache_valid(entry)
                
                if is_valid:
                    valid_entries += 1
                else:
                    expired_entries += 1
                    
                cache_details.append({
                    "key": key,
                    "age_seconds": age_seconds,
                    "is_valid": is_valid,
                    "data_preview": entry['data'][:100] + "..." if len(entry['data']) > 100 else entry['data']
                })
            
            return {
                "total_entries": len(self.cache),
                "valid_entries": valid_entries,
                "expired_entries": expired_entries,
                "cache_details": cache_details
            }

    @asynccontextmanager
    async def async_context(self):
        """
        Provide an asynchronous context manager for async operations.
        """
        try:
            self.logger.debug("Entering async prompt manager context.")
            yield self
        finally:
            self.logger.debug("Exited async prompt manager context.")


def create_cosmos_prompt_manager(
    cosmos_client: AzureCosmosDB,
    database_name: str = "prompts",
    container_name: str = "prompts",
    service_name: str = "azure_cosmos_prompt_manager",
    service_version: str = "1.0.0",
    logger: Optional[AzureLogger] = None,
    cache_ttl: int = 300,
) -> CosmosPromptManager:
    """
    Factory function to create an instance of CosmosPromptManager.
    
    Args:
        cosmos_client: AzureCosmosDB client instance
        database_name: Name of the Cosmos DB database
        container_name: Name of the Cosmos DB container
        service_name: Service name for logging
        service_version: Service version for logging
        logger: Optional AzureLogger instance
        cache_ttl: Cache time-to-live in seconds
        
    Returns:
        Configured CosmosPromptManager instance
    """
    return CosmosPromptManager(
        cosmos_client=cosmos_client,
        database_name=database_name,
        container_name=container_name,
        service_name=service_name,
        service_version=service_version,
        logger=logger,
        cache_ttl=cache_ttl,
    ) 