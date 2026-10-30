import pytest

from app.ingestion.parser import parse_source
from app.ingestion.chunker import generate_chunks


def test_python_functions_classes_methods_async_nested_decorators_and_unicode():
    source = "@decorator\ndef café(x: int = 1):\n    return x\n\nclass Greeter:\n    def hello(self, name):\n        def nested():\n            return name\n        return nested()\n\nasync def fetch():\n    return 'ok'\n"
    results = parse_source(source, "python", "src/example.py")
    assert {item.symbol for item in results} >= {"café", "Greeter", "hello", "nested", "fetch"}
    greeter = next(item for item in results if item.symbol == "Greeter")
    assert greeter.start_line == 5
    assert greeter.end_line == 5
    assert greeter.content == "class Greeter:\n"
    café = next(item for item in results if item.symbol == "café")
    assert café.start_line == 1
    assert café.content.startswith("@decorator\ndef café")


def test_python_syntax_error_returns_fallback_candidates():
    source = "def broken(:\n    pass\n"
    results = parse_source(source, "python", "broken.py")
    assert results == []


@pytest.mark.parametrize("language, source", [
    ("javascript", "function add(a,b) { return a+b; }\nconst double = (x) => x*2;\nclass Box { method() { return 1; } }"),
    ("typescript", "interface User { name: string }\ntype ID = string;\nenum State { Ready }\nclass Service { run(): void {} }\nfunction load(): User { return {name: 'A'}; }"),
    ("tsx", "export interface Props { value: string }\nexport function View(): JSX.Element { return <div /> }"),
    ("java", "interface Worker { void run(); }\npublic class Example { Example() {} void run() {} public class Nested {} }\nenum State { READY }"),
])
def test_tree_sitter_supported_languages(language, source):
    results = parse_source(source, language, f"src/example.{language}")
    assert isinstance(results, list)
    assert all(item.start_line >= 1 and item.end_line >= item.start_line for item in results)


def test_chunker_fallback_and_deterministic_ordering():
    source = "first line\nsecond line\nthird line"
    chunks = generate_chunks(source, "markdown", [], max_chunk_chars=20)
    assert chunks
    assert [item.start_line for item in chunks] == sorted(item.start_line for item in chunks)
    assert "\n".join(item.content for item in chunks) != ""
    assert all(item.content.strip() for item in chunks)
    assert "".join(item.content for item in chunks) == source
    assert all(len(item.content) <= 20 for item in chunks)


def test_chunker_symbol_context_and_oversized_symbol():
    source = "class Large:\n    def first(self):\n        return 1\n\n    def second(self):\n        return 2\n"
    from app.ingestion.parser import ParseResult
    parsed = [
        ParseResult("Large", "class", None, 1, 6, source, "python"),
        ParseResult("first", "method", "Large", 2, 3, "    def first(self):\n        return 1", "python"),
        ParseResult("second", "method", "Large", 5, 6, "    def second(self):\n        return 2", "python"),
    ]
    chunks = generate_chunks(source, "python", parsed, max_chunk_chars=45)
    assert len(chunks) >= 2
    assert all(item.language == "python" for item in chunks)
    assert len({(item.start_line, item.end_line, item.content) for item in chunks}) == len(chunks)


@pytest.mark.parametrize("source", [
    "first\r\nsecond\r\nthird\r\n",
    "first\nsecond\nthird\n",
    "line one\nline two\n",
])
def test_chunker_preserves_exact_line_endings_and_trailing_newlines(source):
    chunks = generate_chunks(source, "python", [], max_chunk_chars=7)
    assert "".join(item.content for item in chunks) == source
    assert all(len(item.content) <= 7 for item in chunks)


def test_chunker_single_oversized_line_is_split_without_character_loss():
    source = "x" * 25 + "\nend"
    chunks = generate_chunks(source, "text", [], max_chunk_chars=8)
    assert "".join(item.content for item in chunks) == source
    assert all(len(item.content) <= 8 for item in chunks)
    assert chunks[0].start_line == 1
    assert chunks[-1].end_line == 2


def test_chunker_nested_symbols_do_not_overlap_and_reconstruct_source():
    source = "def outer():\n    def inner():\n        return 1\n    return inner()\n"
    parsed = parse_source(source, "python", "nested.py")
    chunks = generate_chunks(source, "python", parsed, max_chunk_chars=12)
    assert "".join(item.content for item in chunks) == source
    symbols = {item.symbol for item in chunks}
    assert "outer" in symbols
    assert "inner" not in symbols


def test_chunker_large_function_and_class_metadata_are_accurate():
    source = "class Large:\n    def run(self):\n        " + ("value = 1\n        " * 20) + "return value\n"
    parsed = parse_source(source, "python", "large.py")
    chunks = generate_chunks(source, "python", parsed, max_chunk_chars=30)
    assert "".join(item.content for item in chunks) == source
    assert all(len(item.content) <= 30 for item in chunks)
    assert all(item.start_line >= 1 and item.end_line >= item.start_line for item in chunks)
