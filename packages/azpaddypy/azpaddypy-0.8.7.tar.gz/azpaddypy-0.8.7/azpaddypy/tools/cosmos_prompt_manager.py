"""
Azure Cosmos DB Prompt Management Tool.

This module provides a comprehensive prompt management system using Azure Cosmos DB
for storing and retrieving prompts with real-time updates.

Features:
- Simple prompt storage in Cosmos DB
- Real-time updates across all instances
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
    Azure Cosmos DB-based prompt management tool with standardized client initialization
    and both synchronous and asynchronous operations.
    
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
    ):
        self.cosmos_client = cosmos_client
        self.database_name = database_name
        self.container_name = container_name
        self.service_name = service_name
        self.service_version = service_version

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
            }
        )

    def _create_prompt_document(self, prompt_name: str, promt_data: object) -> Dict[str, Any]:
        """Create Cosmos DB document from prompt data."""
        context = {
            "id": prompt_name,
            "name": prompt_name,
            "prompt_template": promt_data,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        merged_data = {**promt_data, **context}
        return merged_data

    def get_prompt(self, prompt_name: str, max_integrated_cache_staleness_in_ms: int = 5000) -> Optional[str]:
        """
        Get prompt template from Cosmos DB.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Prompt template if found, None otherwise
        """
        with self.logger.create_span("CosmosPromptManager.get_prompt", attributes={"prompt_name": prompt_name}):
            # Load from Cosmos DB
            try:
                doc = self.cosmos_client.read_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name,
                    max_integrated_cache_staleness_in_ms=max_integrated_cache_staleness_in_ms
                )
                
                # Check if document was found
                if doc is None:
                    self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                    return None
                
                prompt_template = doc.get("prompt_template", "")
                
                self.logger.info(f"Loaded prompt from Cosmos DB: {prompt_name}")
                return prompt_template
                
            except ResourceNotFoundError:
                self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                return None
            except Exception as e:
                self.logger.error(f"Error loading prompt {prompt_name}: {e}", exc_info=True)
                return None

    def save_prompt(self, prompt_name: str, promt_data: object) -> bool:
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
                doc = self._create_prompt_document(prompt_name=prompt_name, promt_data=promt_data)
                
                # Save to Cosmos DB
                self.cosmos_client.upsert_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item=doc
                )
                
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
                    self.logger.info(f"Deleted prompt from Cosmos DB: {prompt_name}")
                    return True
                else:
                    self.logger.warning(f"Prompt not found for deletion: {prompt_name}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error deleting prompt {prompt_name}: {e}", exc_info=True)
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
                    "timestamp": doc.get("timestamp")
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
                        "timestamp": doc.get("timestamp")
                    }
                    for doc in docs
                ]
                
                self.logger.debug(f"Found {len(detailed_prompts)} prompts in Cosmos DB")
                return detailed_prompts
                
            except Exception as e:
                self.logger.error(f"Error getting all prompt details: {e}", exc_info=True)
                return []

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
    ) 