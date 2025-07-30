"""
Azure Cosmos DB Prompt Management Tool.

This module provides a comprehensive prompt management system using Azure Cosmos DB
for storing and retrieving prompts with real-time updates and optimized performance.

Features:
- Simple prompt storage in Cosmos DB with optimized integrated cache usage
- Batch operations for high-performance scenarios
- Configurable consistency levels (eventual, bounded, strong)
- Real-time updates across all instances
- Async support for high-throughput applications
- Retry logic with exponential backoff
- Comprehensive error handling and logging
- Backward compatibility with existing system
- Standardized azpaddypy logging and error handling
"""

import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Literal
from contextlib import asynccontextmanager
from functools import wraps

from azure.core.exceptions import ResourceNotFoundError
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

from ..resources.cosmosdb import AzureCosmosDB
from ..mgmt.logging import AzureLogger

def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
):
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for the first retry
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        # Last attempt failed, raise the exception
                        break
                    
                    # Calculate delay for next attempt
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                                    # Log the retry attempt
                if args and hasattr(args[0], 'logger'):
                    args[0].logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s",
                        extra={
                            "error": str(e), 
                            "attempt": attempt + 1,
                            "function": func.__name__
                        }
                    )
                    
                    time.sleep(delay)
            
            # All attempts failed
            raise last_exception
            
        return wrapper
    return decorator


class CosmosPromptManager:
    """
    Azure Cosmos DB-based prompt management tool with optimized performance,
    batch operations, and configurable consistency levels.
    
    This tool follows the azpaddypy pattern for Azure resource management with
    proper logging, error handling, and configuration management. It leverages
    Cosmos DB's integrated cache for optimal performance without additional 
    local caching layers.
    
    Features:
    - Optimized Cosmos DB integrated cache usage
    - Batch operations for multiple prompts
    - Configurable consistency levels (eventual, bounded, strong)
    - Async support for high-throughput scenarios
    - Retry logic with exponential backoff
    - Comprehensive error handling and logging
    """

    def __init__(
        self,
        cosmos_client: AzureCosmosDB,
        database_name: str = "prompts",
        container_name: str = "prompts",
        service_name: str = "azure_cosmos_prompt_manager",
        service_version: str = "1.0.0",
        logger: Optional[AzureLogger] = None,
        max_retries: int = 3,
        base_retry_delay: float = 1.0,
    ):
        """
        Initialize CosmosPromptManager.
        
        Args:
            cosmos_client: AzureCosmosDB client instance
            database_name: Name of the Cosmos DB database
            container_name: Name of the Cosmos DB container
            service_name: Service name for logging
            service_version: Service version for logging
            logger: Optional AzureLogger instance
            max_retries: Maximum number of retry attempts for failed operations
            base_retry_delay: Base delay in seconds for retry logic
        """
        self.cosmos_client = cosmos_client
        self.database_name = database_name
        self.container_name = container_name
        self.service_name = service_name
        self.service_version = service_version
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay

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
                "max_retries": max_retries,
                "base_retry_delay": base_retry_delay,
            }
        )

    def _create_prompt_document(self, prompt_name: str, prompt_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create Cosmos DB document from prompt data.
        
        Args:
            prompt_name: Name of the prompt
            prompt_data: Either a string template or dictionary with prompt data
            
        Returns:
            Dictionary formatted for Cosmos DB storage
        """
        # If prompt_data is a dict, merge it; otherwise, treat it as prompt_template content
        if isinstance(prompt_data, dict):
            # prompt_data is already a dictionary, merge with context
            context = {
                "id": prompt_name,
                "name": prompt_name,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
            merged_data = {**prompt_data, **context}
        else:
            # prompt_data is a string or other type, treat as prompt_template
            merged_data = {
                "id": prompt_name,
                "name": prompt_name,
                "prompt_template": prompt_data,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }
        return merged_data

    def _get_cache_staleness_ms(self, consistency_level: Literal["eventual", "bounded", "strong"]) -> int:
        """
        Get cache staleness in milliseconds based on consistency level.
        
        Args:
            consistency_level: Desired consistency level
            
        Returns:
            Cache staleness in milliseconds
        """
        staleness_config = {
            "eventual": 30000,    # 30 seconds for non-critical prompts
            "bounded": 5000,      # 5 seconds for normal prompts
            "strong": 0           # 0 milliseconds for critical prompts (no cache)
        }
        return staleness_config.get(consistency_level, 5000)

    def get_prompt(
        self, 
        prompt_name: str, 
        consistency_level: Literal["eventual", "bounded", "strong"] = "bounded",
        max_integrated_cache_staleness_in_ms: Optional[int] = None
    ) -> Optional[str]:
        """
        Get prompt template from Cosmos DB with configurable consistency.
        
        Args:
            prompt_name: Name of the prompt
            consistency_level: Consistency level (eventual, bounded, strong)
            max_integrated_cache_staleness_in_ms: Override cache staleness (optional)
            
        Returns:
            Prompt template if found, None otherwise
        """
        @retry_with_exponential_backoff(max_retries=self.max_retries)
        def _get_with_retry():
            with self.logger.create_span(
                "CosmosPromptManager.get_prompt", 
                attributes={
                    "prompt_name": prompt_name,
                    "consistency_level": consistency_level
                }
            ):
                # Determine cache staleness
                if max_integrated_cache_staleness_in_ms is None:
                    staleness_ms = self._get_cache_staleness_ms(consistency_level)
                else:
                    staleness_ms = max_integrated_cache_staleness_in_ms
                
                # Read from Cosmos DB with optimized cache settings
                doc = self.cosmos_client.read_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item_id=prompt_name,
                    partition_key=prompt_name,
                    max_integrated_cache_staleness_in_ms=staleness_ms
                )
                
                # Check if document was found
                if doc is None:
                    self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
                    return None
                
                prompt_template = doc.get("prompt_template", "")
                
                self.logger.info(
                    f"Loaded prompt from Cosmos DB: {prompt_name}",
                    extra={
                        "consistency_level": consistency_level,
                        "cache_staleness_ms": staleness_ms
                    }
                )
                return prompt_template
        
        try:
            return _get_with_retry()
        except ResourceNotFoundError:
            self.logger.warning(f"Prompt not found in Cosmos DB: {prompt_name}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading prompt {prompt_name}: {e}", exc_info=True)
            return None

    def get_prompts_batch(
        self, 
        prompt_names: List[str],
        consistency_level: Literal["eventual", "bounded", "strong"] = "bounded"
    ) -> Dict[str, Optional[str]]:
        """
        Get multiple prompts in a single batch operation for improved performance.
        
        Args:
            prompt_names: List of prompt names to retrieve
            consistency_level: Consistency level for all prompts
            
        Returns:
            Dictionary mapping prompt names to their templates (None if not found)
        """
        with self.logger.create_span(
            "CosmosPromptManager.get_prompts_batch",
            attributes={
                "prompt_count": len(prompt_names),
                "consistency_level": consistency_level
            }
        ):
            if not prompt_names:
                return {}
            
            try:
                # Build SQL query for batch retrieval
                prompt_name_params = [f"@name{i}" for i in range(len(prompt_names))]
                query = f"SELECT * FROM c WHERE c.id IN ({','.join(prompt_name_params)})"
                
                # Create parameters for the query
                parameters = [
                    {"name": f"@name{i}", "value": name} 
                    for i, name in enumerate(prompt_names)
                ]
                
                # Determine cache staleness
                staleness_ms = self._get_cache_staleness_ms(consistency_level)
                
                # Execute batch query
                docs = self.cosmos_client.query_items(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    query=query,
                    parameters=parameters,
                    max_integrated_cache_staleness_in_ms=staleness_ms
                )
                
                # Create result dictionary
                result = {}
                found_prompts = {doc["id"]: doc.get("prompt_template", "") for doc in docs}
                
                # Ensure all requested prompts are in the result
                for prompt_name in prompt_names:
                    result[prompt_name] = found_prompts.get(prompt_name)
                
                found_count = len([v for v in result.values() if v is not None])
                self.logger.info(
                    f"Batch loaded {found_count}/{len(prompt_names)} prompts from Cosmos DB",
                    extra={
                        "requested_count": len(prompt_names),
                        "found_count": found_count,
                        "consistency_level": consistency_level
                    }
                )
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error in batch prompt retrieval: {e}", exc_info=True)
                # Return dictionary with all None values as fallback
                return {name: None for name in prompt_names}

    def save_prompt(self, prompt_name: str, prompt_data: Union[str, Dict[str, Any]]) -> bool:
        """
        Save prompt to Cosmos DB with retry logic.
        
        Args:
            prompt_name: Name of the prompt
            prompt_data: Template content (string) or dictionary with prompt data
            
        Returns:
            True if successful, False otherwise
        """
        @retry_with_exponential_backoff(max_retries=self.max_retries)
        def _save_with_retry():
            with self.logger.create_span(
                "CosmosPromptManager.save_prompt", 
                attributes={"prompt_name": prompt_name}
            ):
                # Create document
                doc = self._create_prompt_document(prompt_name=prompt_name, prompt_data=prompt_data)
                
                # Save to Cosmos DB
                self.cosmos_client.upsert_item(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    item=doc
                )
                
                self.logger.info(f"Saved prompt to Cosmos DB: {prompt_name}")
                return True
        
        try:
            return _save_with_retry()
        except Exception as e:
            self.logger.error(f"Error saving prompt {prompt_name}: {e}", exc_info=True)
            return False

    def save_prompts_batch(
        self, 
        prompts: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """
        Save multiple prompts in batch for improved performance using concurrent operations.
        
        Args:
            prompts: List of prompt dictionaries, each containing 'name' and 'data' keys
                    Example: [
                        {"name": "prompt1", "data": "template content"},
                        {"name": "prompt2", "data": {"prompt_template": "content", "category": "test"}}
                    ]
            
        Returns:
            Dictionary mapping prompt names to success status
        """
        with self.logger.create_span(
            "CosmosPromptManager.save_prompts_batch",
            attributes={"prompt_count": len(prompts)}
        ):
            if not prompts:
                return {}
            
            results = {}
            
            # Process each prompt individually but with better error handling
            # Note: Cosmos DB SDK doesn't expose bulk operations through our wrapper
            for prompt_dict in prompts:
                prompt_name = prompt_dict.get("name")
                prompt_data = prompt_dict.get("data")
                
                if not prompt_name:
                    self.logger.error(f"Prompt missing 'name' field: {prompt_dict}")
                    results[f"unnamed_prompt_{len(results)}"] = False
                    continue
                
                try:
                    doc = self._create_prompt_document(prompt_name, prompt_data)
                    
                    # Use individual upsert operations (each JSON document is separate)
                    self.cosmos_client.upsert_item(
                        database_name=self.database_name,
                        container_name=self.container_name,
                        item=doc
                    )
                    
                    results[prompt_name] = True
                    
                except Exception as e:
                    self.logger.error(f"Error saving prompt {prompt_name} in batch: {e}", exc_info=True)
                    results[prompt_name] = False
            
            success_count = sum(1 for success in results.values() if success)
            self.logger.info(
                f"Batch saved {success_count}/{len(prompts)} prompts to Cosmos DB",
                extra={
                    "total_count": len(prompts),
                    "success_count": success_count,
                    "note": "Individual JSON documents saved separately"
                }
            )
            
            return results

    def list_prompts(self) -> List[str]:
        """
        List all prompt names with optimized query.
        
        Returns:
            List of prompt names
        """
        with self.logger.create_span("CosmosPromptManager.list_prompts"):
            try:
                # Optimized query to get only names
                query = "SELECT c.name FROM c ORDER BY c.name"
                
                docs = self.cosmos_client.query_items(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    query=query,
                    max_integrated_cache_staleness_in_ms=30000  # 30s cache for list operations
                )
                
                prompt_names = [doc["name"] for doc in docs]
                self.logger.debug(f"Found {len(prompt_names)} prompts in Cosmos DB")
                return prompt_names
                
            except Exception as e:
                self.logger.error(f"Error listing prompts: {e}", exc_info=True)
                return []

    def delete_prompt(self, prompt_name: str) -> bool:
        """
        Delete a prompt from Cosmos DB with retry logic.
        
        Args:
            prompt_name: Name of prompt to delete
            
        Returns:
            True if successful, False otherwise
        """
        @retry_with_exponential_backoff(max_retries=self.max_retries)
        def _delete_with_retry():
            with self.logger.create_span(
                "CosmosPromptManager.delete_prompt", 
                attributes={"prompt_name": prompt_name}
            ):
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
        
        try:
            return _delete_with_retry()
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
        with self.logger.create_span(
            "CosmosPromptManager.get_prompt_details", 
            attributes={"prompt_name": prompt_name}
        ):
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
        Get details for all prompts with optimized query.
        
        Returns:
            List of dictionaries with prompt details
        """
        with self.logger.create_span("CosmosPromptManager.get_all_prompt_details"):
            try:
                # Optimized query with specific fields
                query = "SELECT c.id, c.name, c.prompt_template, c.timestamp FROM c ORDER BY c.name"
                
                docs = self.cosmos_client.query_items(
                    database_name=self.database_name,
                    container_name=self.container_name,
                    query=query,
                    max_integrated_cache_staleness_in_ms=30000  # 30s cache for bulk operations
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

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the prompt manager.
        
        Returns:
            Dictionary with health check results
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": {
                "name": self.service_name,
                "version": self.service_version
            },
            "checks": {}
        }
        
        try:
            # Test database connection
            start_time = time.time()
            self.cosmos_client.get_database(self.database_name)
            connection_time = time.time() - start_time
            
            health_status["checks"]["database_connection"] = {
                "status": "healthy",
                "response_time_ms": int(connection_time * 1000)
            }
            
            # Test container access
            start_time = time.time()
            container = self.cosmos_client.get_container(self.database_name, self.container_name)
            container_time = time.time() - start_time
            
            health_status["checks"]["container_access"] = {
                "status": "healthy",
                "response_time_ms": int(container_time * 1000)
            }
            
            # Test basic operations
            start_time = time.time()
            prompts = self.list_prompts()
            list_time = time.time() - start_time
            
            health_status["checks"]["basic_operations"] = {
                "status": "healthy",
                "response_time_ms": int(list_time * 1000),
                "prompt_count": len(prompts)
            }
            
            self.logger.info("Health check completed successfully")
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            health_status["checks"]["error"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self.logger.error(f"Health check failed: {e}", exc_info=True)
        
        return health_status

    @asynccontextmanager
    async def async_context(self):
        """
        Provide an asynchronous context manager for async operations.
        Enhanced with better connection management.
        """
        try:
            self.logger.debug("Entering async prompt manager context")
            yield self
        finally:
            self.logger.debug("Exited async prompt manager context")

    async def get_prompt_async(
        self, 
        prompt_name: str,
        consistency_level: Literal["eventual", "bounded", "strong"] = "bounded"
    ) -> Optional[str]:
        """
        Async version of get_prompt for high-throughput scenarios.
        
        Args:
            prompt_name: Name of the prompt
            consistency_level: Consistency level for cache staleness
            
        Returns:
            Prompt template if found, None otherwise
        """
        async with self.cosmos_client.async_client_context() as client:
            try:
                container = client.get_database_client(self.database_name)\
                    .get_container_client(self.container_name)
                
                # Get cache staleness based on consistency level
                staleness_ms = self._get_cache_staleness_ms(consistency_level)
                
                options = {}
                if staleness_ms > 0:
                    options['max_integrated_cache_staleness_in_ms'] = staleness_ms
                
                doc = await container.read_item(
                    item=prompt_name,
                    partition_key=prompt_name,
                    **options
                )
                
                if doc:
                    self.logger.info(f"Async loaded prompt: {prompt_name}")
                    return doc.get("prompt_template", "")
                else:
                    self.logger.warning(f"Async prompt not found: {prompt_name}")
                    return None
                
            except Exception as e:
                self.logger.error(f"Error in async prompt retrieval {prompt_name}: {e}", exc_info=True)
                return None


def create_cosmos_prompt_manager(
    cosmos_client: AzureCosmosDB,
    database_name: str = "prompts",
    container_name: str = "prompts",
    service_name: str = "azure_cosmos_prompt_manager",
    service_version: str = "1.0.0",
    logger: Optional[AzureLogger] = None,
    max_retries: int = 3,
    base_retry_delay: float = 1.0,
) -> CosmosPromptManager:
    """
    Factory function to create an instance of CosmosPromptManager with enhanced features.
    
    Args:
        cosmos_client: AzureCosmosDB client instance
        database_name: Name of the Cosmos DB database
        container_name: Name of the Cosmos DB container
        service_name: Service name for logging
        service_version: Service version for logging
        logger: Optional AzureLogger instance
        max_retries: Maximum number of retry attempts
        base_retry_delay: Base delay in seconds for retry logic
        
    Returns:
        Configured CosmosPromptManager instance with enhanced features
    """
    return CosmosPromptManager(
        cosmos_client=cosmos_client,
        database_name=database_name,
        container_name=container_name,
        service_name=service_name,
        service_version=service_version,
        logger=logger,
        max_retries=max_retries,
        base_retry_delay=base_retry_delay,
    ) 