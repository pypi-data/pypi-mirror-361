# Extending flujo

## Adding a Custom Agent

```python
from pydantic_ai import Agent
class MyAgent(Agent):
    ...
```

## Adding a Reflection Step

The simplified orchestrator no longer performs reflection automatically. To
incorporate strategic feedback, build a custom pipeline using `Step`:

```python
from flujo import Step, Flujo, get_reflection_agent
from flujo.infra.agents import make_review_agent, make_solution_agent, make_validator_agent

reflection_agent = get_reflection_agent(model="anthropic:claude-3-haiku")

pipeline = (
    Step.review(make_review_agent())
    >> Step.solution(make_solution_agent())
    >> Step.validate(make_validator_agent())
    >> Step.validate(reflection_agent)
)

result = Flujo(pipeline).run("Write a poem")
```

### Creating Custom Step Factories with Pre-configured Plugins

If you frequently use a step with the same set of plugins, you can create your own factory function:

```python
from flujo import Step
from my_app.plugins import MyCustomValidator

def ReusableSQLStep(agent, **config) -> Step:
    '''A solution step that always includes MyCustomValidator.'''
    step = Step.solution(agent, **config)
    step.add_plugin(MyCustomValidator(), priority=10)
    return step

# Usage:
pipeline = ReusableSQLStep(my_sql_agent) >> Step.validate(...)
```

### Creating a Custom Execution Backend

Execution back-ends allow you to control how and where pipeline steps run.
Implement the `ExecutionBackend` protocol and pass your implementation to
`Flujo`.

```python
from flujo.domain.backends import ExecutionBackend, StepExecutionRequest
from flujo.domain.models import StepResult

class LoggingBackend(ExecutionBackend):
    def __init__(self, registry: dict[str, Any]):
        self.agent_registry = registry

    async def execute_step(self, request: StepExecutionRequest) -> StepResult:
        print(f"Executing {request.step.name}")
        agent = request.step.agent
        if request.stream and hasattr(agent, "stream"):
            chunks: list[Any] = []
            async for c in agent.stream(request.input_data):
                if request.on_chunk is not None:
                    await request.on_chunk(c)
                chunks.append(c)
        else:
            chunks = [await agent.run(request.input_data)]
        output = (
            "".join(chunks)
            if chunks and all(isinstance(c, str) for c in chunks)
            else chunks
        )
        return StepResult(name=request.step.name, output=output)

custom_backend = LoggingBackend({})
runner = Flujo(pipeline, backend=custom_backend)
```

For remote back-ends, use the `agent_registry` to safely map agent names to
trusted objects.

## Automatic Context and Resource Injection

`flujo` can automatically inject `PipelineContext` and `AppResources` into your custom functions and methods if they are type-hinted as keyword-only arguments. This allows you to write cleaner, more reusable code without having to manually pass these objects around.

### How it Works

When you use a custom function as a `mapper` in a `Step`, `flujo` analyzes its signature to determine if it needs `context` or `resources`. If it finds a keyword-only argument named `context` that is a subclass of `BaseModel`, or a keyword-only argument named `resources` that is a subclass of `AppResources`, it will automatically inject the corresponding object at runtime.

### Example

```python
from flujo import Step, Flujo
from flujo.domain.models import PipelineContext
from flujo.domain.resources import AppResources

class MyContext(PipelineContext):
    counter: int = 0

class MyResources(AppResources):
    db_pool: Any

async def my_mapper(text: str, *, context: MyContext, resources: MyResources) -> str:
    context.counter += 1
    # Access the database pool from resources
    db_conn = await resources.db_pool.acquire()
    # ... do something with the database connection ...
    await resources.db_pool.release(db_conn)
    return text.upper()

# Create a pipeline with the custom mapper
custom_pipeline = Step.from_mapper(my_mapper)

# Initialize Flujo with the context and resources
runner = Flujo(
    custom_pipeline,
    context_model=MyContext,
    initial_context_data={"counter": 0},
    resources=MyResources(db_pool=make_pool()),
)

# Run the pipeline
result = runner.run("some input")

# The counter in the context will be incremented
assert result.final_pipeline_context.counter == 1
```

In this example, `flujo` automatically injects the `MyContext` and `MyResources` objects into the `my_mapper` function because they are type-hinted as keyword-only arguments named `context` and `resources`.
