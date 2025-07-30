import json
import pytest
from flujo.domain.models import Candidate, Checklist, ChecklistItem
from flujo.utils.serialization import safe_serialize

complex_candidate = Candidate(
    solution="This is a very long solution string...",
    score=0.85,
    checklist=Checklist(
        items=[
            ChecklistItem(description=f"Item {i}", passed=True, feedback="Looks good")
            for i in range(20)
        ]
    ),
)


@pytest.mark.benchmark(group="serialization")
def test_benchmark_pydantic_orjson_dumps(benchmark):
    # Use robust serialization instead of deprecated model_dump_json
    benchmark(lambda: json.dumps(safe_serialize(complex_candidate)))


@pytest.mark.benchmark(group="serialization")
def test_benchmark_stdlib_json_dumps(benchmark):
    data = safe_serialize(complex_candidate)
    benchmark(json.dumps, data)


@pytest.mark.benchmark(group="deserialization")
def test_benchmark_pydantic_orjson_loads(benchmark):
    # Use robust serialization instead of deprecated model_dump_json
    json_str = json.dumps(safe_serialize(complex_candidate))
    benchmark(Candidate.model_validate_json, json_str)


@pytest.mark.benchmark(group="deserialization")
def test_benchmark_stdlib_json_loads(benchmark):
    # Use robust serialization instead of deprecated model_dump_json
    json_str = json.dumps(safe_serialize(complex_candidate))
    benchmark(json.loads, json_str)
