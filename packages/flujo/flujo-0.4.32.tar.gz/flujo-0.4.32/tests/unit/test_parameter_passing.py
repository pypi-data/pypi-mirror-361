"""Test parameter passing to ensure context injection works correctly."""

import pytest
from unittest.mock import AsyncMock
from flujo.application.runner import Flujo
from flujo.domain.dsl import Pipeline, Step, StepConfig
from flujo.domain.models import PipelineContext
from flujo.domain.plugins import PluginOutcome


class MockAgentWithContext:
    """Mock agent that expects 'context' parameter."""

    def __init__(self):
        self.run_mock = AsyncMock(return_value={"output": "ok"})

    async def run(self, data, *, context: PipelineContext | None = None, **kwargs):
        """Run method that expects 'context' parameter."""
        await self.run_mock(data, context=context, **kwargs)
        return {"output": f"Processed: {data}"}


class MockPluginWithContext:
    """Mock plugin that expects 'context' parameter."""

    def __init__(self):
        self.mock = AsyncMock(return_value=PluginOutcome(success=True, feedback=None))

    async def validate(self, data, *, context: PipelineContext | None = None, **kwargs):
        """Validate method that expects 'context' parameter."""
        await self.mock(data, context=context, **kwargs)
        return PluginOutcome(success=True, feedback=None)


@pytest.mark.asyncio
async def test_agent_receives_context_parameter():
    """Test that agents receive 'context' parameter when they expect it."""
    agent = MockAgentWithContext()
    step = Step.model_validate(
        {"name": "test_step", "agent": agent, "config": StepConfig(max_retries=1, timeout_s=30)}
    )

    pipeline = Pipeline(steps=[step])

    flujo = Flujo(pipeline, context_model=PipelineContext)

    # Run the pipeline
    async for result in flujo.run_async(
        "test_data", initial_context_data={"initial_prompt": "test prompt"}
    ):
        pass  # We only need the first result

    # Verify the agent was called with 'context' parameter
    agent.run_mock.assert_called_once()
    call_args = agent.run_mock.call_args
    assert "context" in call_args[1]
    assert call_args[1]["context"].initial_prompt == "test prompt"


@pytest.mark.asyncio
async def test_plugin_receives_context_parameter():
    """Test that plugins receive 'context' parameter when they expect it."""
    agent = MockAgentWithContext()
    plugin = MockPluginWithContext()

    step = Step.model_validate(
        {
            "name": "test_step",
            "agent": agent,
            "plugins": [(plugin, 1)],
            "config": StepConfig(max_retries=1, timeout_s=30),
        }
    )

    pipeline = Pipeline(steps=[step])

    flujo = Flujo(pipeline, context_model=PipelineContext)

    # Run the pipeline
    async for result in flujo.run_async(
        "test_data", initial_context_data={"initial_prompt": "test prompt"}
    ):
        pass  # We only need the first result

    # Verify the plugin was called with 'context' parameter
    plugin.mock.assert_called_once()
    call_args = plugin.mock.call_args
    assert "context" in call_args[1]
    assert call_args[1]["context"].initial_prompt == "test prompt"
