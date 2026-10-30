import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class ParseResult:
    symbol: str
    symbol_type: str
    parent_symbol: str | None
    start_line: int
    end_line: int
    content: str
    language: str


class SourceParser:
    def parse(self, source: str, language: str, relative_path: str) -> list[ParseResult]:
        if language == "python": return PythonParser().parse(source)
        if language in {"javascript", "jsx"}: return TreeSitterParser("javascript").parse(source, language)
        if language in {"typescript", "tsx"}: return TreeSitterParser("tsx" if language == "tsx" else "typescript").parse(source, language)
        if language == "java": return TreeSitterParser("java").parse(source, language)
        return []


class PythonParser:
    def parse(self, source: str) -> list[ParseResult]:
        try:
            tree = ast.parse(source)
        except (SyntaxError, ValueError):
            return []
        lines = source.splitlines(keepends=True)
        results: list[ParseResult] = []

        def exact_slice(start_line: int, end_line: int) -> str:
            return "".join(lines[start_line - 1:end_line])

        def visit(node, parent: str | None = None):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if isinstance(node, ast.ClassDef):
                    symbol_type = "class"
                else:
                    symbol_type = "method" if parent is not None else "function"
                    if isinstance(node, ast.AsyncFunctionDef): symbol_type = "async_method" if parent is not None else "async_function"
                decorator_lines = [item.lineno for item in getattr(node, "decorator_list", [])]
                start = min([node.lineno, *decorator_lines])
                end = getattr(node, "end_lineno", node.lineno) or node.lineno
                if isinstance(node, ast.ClassDef):
                    first_body_line = min((item.lineno for item in node.body), default=end)
                    header_end = end if first_body_line <= node.lineno else max(node.lineno, first_body_line - 1)
                    if first_body_line == node.lineno:
                        header_end = node.lineno
                    text = exact_slice(start, header_end)
                    if text and not text.endswith(("\n", "\r")) and header_end < len(lines):
                        pass
                else:
                    text = exact_slice(start, end)
                results.append(ParseResult(node.name, symbol_type, parent, start, header_end if isinstance(node, ast.ClassDef) else end, text, "python"))
                parent_for_children = node.name
            else:
                parent_for_children = parent
            for child in ast.iter_child_nodes(node):
                visit(child, parent_for_children)

        visit(tree)
        return results


class TreeSitterParser:
    def __init__(self, grammar: str):
        from tree_sitter import Language, Parser
        if grammar == "javascript":
            import tree_sitter_javascript as grammar_module
        elif grammar in {"typescript", "tsx"}:
            import tree_sitter_typescript as grammar_module
        elif grammar == "java":
            import tree_sitter_java as grammar_module
        else:
            raise ValueError("Unsupported Tree-sitter grammar")
        if grammar == "tsx":
            language_value = grammar_module.language_tsx()
        elif grammar == "typescript":
            language_value = grammar_module.language_typescript()
        else:
            language_value = grammar_module.language()
        self.parser = Parser(Language(language_value))
        self.grammar = grammar

    def parse(self, source: str, language: str) -> list[ParseResult]:
        source_bytes = source.encode("utf-8")
        tree = self.parser.parse(source_bytes)
        if tree.root_node.has_error:
            return []
        results: list[ParseResult] = []
        stack_types = {"javascript": {"function_declaration", "arrow_function", "class_declaration", "method_definition"},
                       "typescript": {"function_declaration", "class_declaration", "method_definition", "method_signature", "interface_declaration", "type_alias_declaration", "enum_declaration"},
                       "tsx": {"function_declaration", "class_declaration", "method_definition", "method_signature", "interface_declaration", "type_alias_declaration", "enum_declaration"},
                       "java": {"class_declaration", "interface_declaration", "enum_declaration", "method_declaration", "constructor_declaration", "record_declaration"}}
        types = stack_types.get(self.grammar, set())

        def walk(node, parent: str | None = None, parent_node=None):
            name = None
            if node.type == "arrow_function" and parent_node is not None and parent_node.type in {"variable_declarator", "variable_definition"}:
                for child in parent_node.children:
                    if child.type in {"identifier", "property_identifier"} and child.text:
                        name = child.text.decode("utf-8", errors="replace")
                        break
            elif node.type in types:
                name = self._name(node)

            if name and (node.type in types or node.type == "arrow_function"):
                start = node.start_point[0] + 1
                end = node.end_point[0] + 1
                source_bytes = source.encode("utf-8")
                if node.type in {"class_declaration", "interface_declaration", "enum_declaration"}:
                    body = next((child for child in node.named_children if child.type in {"class_body", "interface_body", "enum_body", "object_type"}), None)
                    if body is not None:
                        header_bytes = source_bytes[node.start_byte:body.start_byte]
                        brace = header_bytes.find(b"{")
                        if brace >= 0:
                            header_bytes = header_bytes[:brace]
                        text = header_bytes.decode("utf-8", errors="replace")
                        end = body.start_point[0] + (1 if node.start_point[0] == body.start_point[0] else 0)
                    else:
                        text = source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
                        end = node.end_point[0] + 1
                else:
                    text = source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace")
                results.append(ParseResult(name, self._stable_type(node.type), parent, start, end, text, language))
                new_parent = name
            else:
                new_parent = parent
            for child in node.children:
                walk(child, new_parent, node)

        walk(tree.root_node)
        return results

    @staticmethod
    def _stable_type(node_type: str) -> str:
        return node_type.replace("_declaration", "").replace("_definition", "").replace("_declaration", "")

    @staticmethod
    def _name(node) -> str | None:
        direct_fields = ("name", "property_identifier", "identifier", "type_identifier")
        for child in node.children:
            if child.type in direct_fields and child.text:
                return child.text.decode("utf-8", errors="replace")
        for child in node.named_children:
            if child.type in {"property_identifier", "identifier", "type_identifier"} and child.text:
                return child.text.decode("utf-8", errors="replace")
        return None


def parse_source(source: str, language: str, relative_path: str) -> list[ParseResult]:
    return SourceParser().parse(source, language, relative_path)
