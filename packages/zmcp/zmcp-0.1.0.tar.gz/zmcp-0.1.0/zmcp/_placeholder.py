"""
Placeholder implementations for ZMCP core functionality.
These will be replaced with the real implementation.
"""

import warnings
from typing import Any, Callable, Dict, Optional


class NotImplementedWarning(UserWarning):
    """Warning for placeholder functionality"""
    pass


class Context:
    """Placeholder Context class"""

    def __init__(self, **kwargs):
        self._data = kwargs
        warnings.warn(
            "Context is a placeholder implementation. Full version coming soon!",
            NotImplementedWarning,
            stacklevel=2
        )

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> 'Context':
        new_context = Context(**self._data)
        new_context._data[key] = value
        return new_context


def workflow(name: str):
    """Placeholder workflow function"""
    warnings.warn(
        f"workflow('{name}') is a placeholder. Full implementation coming soon!",
        NotImplementedWarning,
        stacklevel=2
    )

    class WorkflowBuilder:
        def __init__(self, name: str):
            self.name = name

        def start_with(self, node_id: str):
            return self

        def task(self, node_id: str, func: Callable):
            return self

        def agent(self, node_id: str, func: Callable):
            return self

        def build(self):
            return PlaceholderWorkflow(self.name)

    return WorkflowBuilder(name)


class PlaceholderWorkflow:
    """Placeholder workflow implementation"""

    def __init__(self, name: str):
        self.name = name

    def run(self, context: Context) -> Context:
        warnings.warn(
            "Workflow execution is not implemented yet. Coming soon!",
            NotImplementedWarning,
            stacklevel=2
        )
        return context.set("status", "placeholder_executed")


def agent(name: str, model: str = "gpt-4"):
    """Placeholder agent decorator"""
    def decorator(func: Callable):
        warnings.warn(
            f"agent('{name}') is a placeholder. Full implementation coming soon!",
            NotImplementedWarning,
            stacklevel=2
        )
        return func
    return decorator


def tool(name: str, description: str = ""):
    """Placeholder tool decorator"""
    def decorator(func: Callable):
        warnings.warn(
            f"tool('{name}') is a placeholder. Full implementation coming soon!",
            NotImplementedWarning,
            stacklevel=2
        )
        return func
    return decorator
