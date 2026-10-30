from dataclasses import dataclass

from .parser import ParseResult


@dataclass(frozen=True)
class ChunkCandidate:
    symbol: str
    symbol_type: str
    parent_symbol: str | None
    start_line: int
    end_line: int
    content: str
    language: str
    chunk_index: int


def _line_number(source: str, offset: int, end: bool = False) -> int:
    if end and offset > 0:
        offset -= 1
    return source.count("\n", 0, max(0, offset)) + 1


def _offset_for_line(source: str, line_number: int) -> int:
    if line_number <= 1:
        return 0
    offsets = source.splitlines(keepends=True)
    current = 0
    for line in offsets[:line_number - 1]:
        current += len(line)
    return current


def _locate_parse_result(source: str, item: ParseResult) -> tuple[int, int] | None:
    if not item.content:
        return None
    line_start = _offset_for_line(source, item.start_line)
    index = source.find(item.content, line_start)
    if index >= 0 and index < len(source):
        return index, index + len(item.content)
    return None


def _candidate_piece(source: str, language: str, start: int, end: int,
                     max_chars: int, symbol: str, symbol_type: str,
                     parent_symbol: str | None) -> list[ChunkCandidate]:
    if max_chars <= 0:
        raise ValueError("max_chunk_chars must be positive")
    pieces: list[ChunkCandidate] = []
    cursor = start
    while cursor < end:
        piece_end = min(cursor + max_chars, end)
        pieces.append(ChunkCandidate(
            symbol,
            symbol_type,
            parent_symbol,
            _line_number(source, cursor),
            _line_number(source, piece_end, end=True),
            source[cursor:piece_end],
            language,
            0,
        ))
        cursor = piece_end
    return pieces


def _line_fallback(content: str, language: str, max_chars: int = 8000,
                   symbol_prefix: str = "module_block") -> list[ChunkCandidate]:
    pieces = _candidate_piece(content, language, 0, len(content), max_chars,
                              symbol_prefix, "block", None)
    return pieces


def generate_chunks(source: str, language: str, parsed: list[ParseResult],
                    max_chunk_chars: int = 8000) -> list[ChunkCandidate]:
    if max_chunk_chars <= 0:
        raise ValueError("max_chunk_chars must be positive")

    ranges: list[tuple[int, int, ParseResult]] = []
    for item in parsed:
        located = _locate_parse_result(source, item)
        if located is not None:
            ranges.append((located[0], located[1], item))
    ranges.sort(key=lambda entry: (entry[0], entry[1], entry[2].symbol))

    non_overlapping: list[tuple[int, int, ParseResult | None]] = []
    covered_until = 0
    for start, end, item in ranges:
        if end <= covered_until or start >= len(source) or end <= start:
            continue
        if start < covered_until:
            continue
        non_overlapping.append((start, end, item))
        covered_until = end

    candidates: list[ChunkCandidate] = []
    cursor = 0
    for start, end, item in non_overlapping:
        if cursor < start:
            candidates.extend(_candidate_piece(source, language, cursor, start,
                                               max_chunk_chars, "module_block", "block", None))
        if item is None:
            continue
        candidates.extend(_candidate_piece(source, item.language, start, end,
                                           max_chunk_chars, item.symbol, item.symbol_type,
                                           item.parent_symbol))
        cursor = end
    if cursor < len(source):
        candidates.extend(_candidate_piece(source, language, cursor, len(source),
                                           max_chunk_chars, "module_block", "block", None))
    if not non_overlapping and not source:
        return []

    if not parsed:
        candidates = _line_fallback(source, language, max_chunk_chars)

    return [ChunkCandidate(
        candidate.symbol,
        candidate.symbol_type,
        candidate.parent_symbol,
        candidate.start_line,
        candidate.end_line,
        candidate.content,
        candidate.language,
        chunk_index,
    ) for chunk_index, candidate in enumerate(candidates)]
