"""Azure tools package for azpaddypy.

This package contains utility tools for common Azure operations
including prompt management, data processing, and other specialized tools.
"""

from .cosmos_prompt_manager import CosmosPromptManager, create_cosmos_prompt_manager

__all__ = [
    "CosmosPromptManager",
    "create_cosmos_prompt_manager",
] 