from collections.abc import Iterable, Mapping
import json
from uuid import UUID


class RAGContextBuilder:
    def __init__(self, max_context_chars: int = 12000):
        if max_context_chars < 1000:
            raise ValueError("Maximum RAG context size must be at least 1000 characters")
        self.max_context_chars = max_context_chars

    def build(self, results: Iterable[Mapping]) -> tuple[str, list[dict]]:
        seen = set()
        sources = []
        blocks = []
        remaining = self.max_context_chars

        for result in results:
            chunk_key = str(result.get("chunk_id") or "")
            if not chunk_key or chunk_key in seen:
                continue
            seen.add(chunk_key)

            source_id = len(sources) + 1
            file_path = str(result.get("file_path") or "")
            symbol = result.get("symbol") or None
            start_line = int(result["start_line"])
            end_line = int(result["end_line"])
            content = str(result.get("snippet") or result.get("content") or "")
            similarity = result.get("similarity")

            metadata = (
                f"[{source_id}] source_id={source_id} file_path={file_path!r} "
                f"symbol={symbol!r} start_line={start_line} end_line={end_line} "
                f"chunk_id={chunk_key}"
            )
            content_budget = remaining - len(metadata) - 160
            if content_budget <= 0:
                break

            code = content[:content_budget]
            if len(content) > content_budget:
                code += "\n[CODE CONTENT TRUNCATED TO CONTEXT LIMIT]"
            entry = {
                "source_id": source_id,
                "file_path": file_path,
                "symbol": symbol,
                "start_line": start_line,
                "end_line": end_line,
                "chunk_id": chunk_key,
                "code": code,
                "code_truncated": len(content) > content_budget,
            }
            block = json.dumps(entry, ensure_ascii=True, separators=(",", ":"))
            block = block.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            if len(block) > remaining:
                break
            blocks.append(block)
            remaining -= len(block)

            try:
                chunk_id = UUID(chunk_key)
            except ValueError:
                chunk_id = chunk_key
            sources.append({
                "id": source_id,
                "file_path": file_path,
                "symbol": symbol,
                "start_line": start_line,
                "end_line": end_line,
                "chunk_id": chunk_id,
                "similarity": float(similarity) if similarity is not None else None,
            })

        return ",\n".join(blocks), sources
