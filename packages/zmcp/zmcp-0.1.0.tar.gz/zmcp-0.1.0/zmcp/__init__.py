"""
ZMCP - Full-Stack AI Framework For Building Enterprise AI Applications

This is a placeholder release to secure the package namespace.
The full implementation is coming soon!

Visit https://zpkg.ai for updates and documentation.
"""

__version__ = "0.1.0"
__author__ = "Octallium Inc"

# Placeholder imports - will be replaced with real implementation
from ._placeholder import (
    workflow,
    agent,
    tool,
    Context,
    NotImplementedWarning,
)

# Public API (placeholder)
__all__ = [
    "workflow",
    "agent",
    "tool",
    "Context",
    "NotImplementedWarning",
]

# Show friendly message on import
import warnings
warnings.warn(
    "ZMCP is in early development. This is a placeholder release to secure the namespace. "
    "Full implementation coming soon! Visit https://zpkg.ai for updates.",
    NotImplementedWarning,
    stacklevel=2
)
