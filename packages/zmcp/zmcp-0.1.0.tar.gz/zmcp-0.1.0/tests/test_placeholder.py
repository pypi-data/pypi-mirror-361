"""Tests for placeholder functionality"""

import pytest
import warnings
from zmcp import workflow, agent, tool, Context, NotImplementedWarning


def test_context_placeholder():
    """Test placeholder Context functionality"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        ctx = Context(test="value")
        assert len(w) == 1
        assert issubclass(w[0].category, NotImplementedWarning)

        assert ctx.get("test") == "value"
        assert ctx.get("missing", "default") == "default"

        new_ctx = ctx.set("new", "data")
        assert new_ctx.get("new") == "data"


def test_workflow_placeholder():
    """Test placeholder workflow functionality"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Should generate warnings for placeholder usage
        pipeline = (workflow("test")
                   .start_with("step1")
                   .task("step1", lambda x: x)
                   .build())

        # Should have generated warnings
        assert len(w) >= 1
        assert any(issubclass(warning.category, NotImplementedWarning) for warning in w)

        # Should be able to run (with warning)
        result = pipeline.run(Context())
        assert result.get("status") == "placeholder_executed"


def test_decorators_placeholder():
    """Test placeholder decorators"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @agent("test_agent")
        def my_agent(ctx):
            return ctx

        @tool("test_tool")
        def my_tool(data):
            return data

        # Should generate warnings
        assert len(w) >= 2
        assert all(issubclass(warning.category, NotImplementedWarning) for warning in w)


def test_import_warning():
    """Test that importing zmcp shows a warning"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Re-import to trigger warning
        import importlib
        importlib.reload(__import__('zmcp'))

        # Should show import warning
        assert len(w) >= 1
        assert any("placeholder release" in str(warning.message) for warning in w)
