import logging
from typing import Dict, Any, List
from tree_sitter import Language, Parser

logger = logging.getLogger(__name__)

class ASTPreprocessor:
    def __init__(self):
        self.parsers: Dict[str, Parser] = {}
        self._init_languages()

    def _init_languages(self):
        # Python
        try:
            import tree_sitter_python as tspython
            py_lang = Language(tspython.language())
            self.parsers["python"] = Parser(py_lang)
            self.parsers["py"] = self.parsers["python"]
        except Exception as e:
            logger.warning(f"Could not load python parser: {e}")

        # JavaScript
        try:
            import tree_sitter_javascript as tsjs
            js_lang = Language(tsjs.language())
            self.parsers["javascript"] = Parser(js_lang)
            self.parsers["js"] = self.parsers["javascript"]
            self.parsers["node"] = self.parsers["javascript"]
        except Exception as e:
            logger.warning(f"Could not load javascript parser: {e}")

        # C
        try:
            import tree_sitter_c as tsc
            c_lang = Language(tsc.language())
            self.parsers["c"] = Parser(c_lang)
        except Exception as e:
            logger.warning(f"Could not load c parser: {e}")

        # C++
        try:
            import tree_sitter_cpp as tscpp
            cpp_lang = Language(tscpp.language())
            self.parsers["cpp"] = Parser(cpp_lang)
            self.parsers["c++"] = self.parsers["cpp"]
        except Exception as e:
            logger.warning(f"Could not load cpp parser: {e}")

        # Java
        try:
            import tree_sitter_java as tsjava
            java_lang = Language(tsjava.language())
            self.parsers["java"] = Parser(java_lang)
        except Exception as e:
            logger.warning(f"Could not load java parser: {e}")

    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        lang_key = (language or "python").lower().strip()
        parser = self.parsers.get(lang_key)

        if not parser:
            return {
                "supported": False,
                "language": language,
                "message": f"Tree-Sitter parser not initialized for '{language}'."
            }

        try:
            code_bytes = code.encode("utf8")
            tree = parser.parse(code_bytes)
            root = tree.root_node

            functions: List[str] = []
            syntax_errors: List[Dict[str, Any]] = []
            loop_count = 0
            call_count = 0

            def traverse(node):
                nonlocal loop_count, call_count
                
                # Check for syntax error or missing token
                if node.is_missing or node.type in ("ERROR", "syntax_error"):
                    start_row = node.start_point.row if hasattr(node.start_point, "row") else node.start_point[0]
                    start_col = node.start_point.column if hasattr(node.start_point, "column") else node.start_point[1]
                    syntax_errors.append({
                        "line": start_row + 1,
                        "column": start_col + 1,
                        "type": node.type,
                        "message": f"Syntax error near line {start_row + 1}"
                    })

                # Function and method definitions
                FUNCTION_NODE_TYPES = (
                    "function_definition",
                    "function_declaration",
                    "function_expression",
                    "arrow_function",
                    "method_declaration",
                    "method_definition"
                )
                if node.type in FUNCTION_NODE_TYPES:
                    # Try to get function name
                    name_node = node.child_by_field_name("name")
                    if name_node and name_node.text:
                        functions.append(name_node.text.decode("utf8", errors="replace"))
                    elif node.type in ("function_declaration", "function_definition"):
                        functions.append(f"func_{len(functions) + 1}")
                    else:
                        functions.append(f"anonymous_{len(functions) + 1}")

                # Loops
                if node.type in (
                    "for_statement", "while_statement", "for_in_statement",
                    "do_statement", "enhanced_for_statement"
                ):
                    loop_count += 1

                # Function calls
                if "call" in node.type or "invocation" in node.type:
                    call_count += 1

                for child in node.children:
                    traverse(child)

            traverse(root)

            named_descendant = root.named_descendant_for_byte_range(0, len(code_bytes))
            node_count = named_descendant.named_child_count if named_descendant else 0

            return {
                "supported": True,
                "language": language,
                "has_syntax_error": root.has_error or len(syntax_errors) > 0,
                "error_count": len(syntax_errors),
                "syntax_errors": syntax_errors[:8],
                "function_count": len(functions),
                "function_names": functions[:10],
                "loop_count": loop_count,
                "call_count": call_count,
                "node_count": node_count,
                "root_type": root.type
            }

        except Exception as e:
            logger.error(f"Error during AST analysis: {e}")
            return {
                "supported": False,
                "language": language,
                "error": str(e)
            }

ast_preprocessor = ASTPreprocessor()
