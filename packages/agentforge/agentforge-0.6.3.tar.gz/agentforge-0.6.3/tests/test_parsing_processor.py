import pytest
from agentforge.utils.parsing_processor import ParsingProcessor


@pytest.fixture(scope="module")
def processor() -> ParsingProcessor:
    return ParsingProcessor()


def test_json_array_parsing(processor):
    raw = """```json
[
  {"index": 0, "text": "foo"},
  {"index": 1, "text": "bar"}
]
```"""
    parsed = processor.parse_by_format(raw, "json")
    assert isinstance(parsed, list)
    assert parsed[0]["index"] == 0
    assert parsed[1]["text"] == "bar"


def test_json_nested_objects_parsing(processor):
    raw = """```json
{"items": [{"id": 1}, {"id": 2}]}
```"""
    parsed = processor.parse_by_format(raw, "json")
    assert isinstance(parsed, dict)
    assert parsed["items"][1]["id"] == 2 