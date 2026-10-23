import ast
from typing import Dict, Any, List

class StaticAnalyzer:
    def analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Performs static metrics and AST checks on Python code."""
        issues: List[Dict[str, Any]] = []
        cyclomatic_complexity = 1
        has_eval_or_exec = False
        nested_loop_depth = 0

        # Try radon cyclomatic complexity
        try:
            from radon.complexity import cc_visit
            blocks = cc_visit(code)
            if blocks:
                cyclomatic_complexity = max(b.complexity for b in blocks)
        except Exception:
            pass

        # Try Python standard ast parsing for deeper static rule checks
        try:
            parsed = ast.parse(code)
            
            # Check for eval, exec, os.system
            for node in ast.walk(parsed):
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr

                    if func_name in ("eval", "exec"):
                        has_eval_or_exec = True
                        issues.append({
                            "line": getattr(node, "lineno", None),
                            "severity": "Critical",
                            "message": f"Dangerous dynamic execution '{func_name}()' detected. High security risk.",
                            "suggestedFix": "Refactor to use safe data structures or json.loads()."
                        })

            # Check nested loop depth
            def check_loop_depth(node, current_depth):
                nonlocal nested_loop_depth
                is_loop = isinstance(node, (ast.For, ast.While))
                new_depth = current_depth + 1 if is_loop else current_depth
                if new_depth > nested_loop_depth:
                    nested_loop_depth = new_depth
                for child in ast.iter_child_nodes(node):
                    check_loop_depth(child, new_depth)

            check_loop_depth(parsed, 0)

            if nested_loop_depth >= 2:
                issues.append({
                    "line": 1,
                    "severity": "Warning",
                    "message": f"Nested loop depth of {nested_loop_depth} detected. High potential for quadratic or cubic time complexity.",
                    "suggestedFix": "Consider using hash maps, two-pointer techniques, or sorting to optimize."
                })

        except SyntaxError as se:
            issues.append({
                "line": se.lineno,
                "severity": "Critical",
                "message": f"Python SyntaxError: {se.msg}",
                "suggestedFix": "Fix syntax error at the indicated line before execution."
            })
        except Exception:
            pass

        return {
            "cyclomatic_complexity": cyclomatic_complexity,
            "nested_loop_depth": nested_loop_depth,
            "has_eval_or_exec": has_eval_or_exec,
            "heuristic_issues": issues
        }

    def analyze(self, code: str, language: str) -> Dict[str, Any]:
        lang = (language or "python").lower()
        if lang in ("python", "py"):
            return self.analyze_python_code(code)
        
        # General heuristic for JS / C / C++ / Java
        issues = []
        nested_for_count = code.count("for (") + code.count("for(") + code.count("while(") + code.count("while (")
        if nested_for_count >= 2:
            issues.append({
                "line": 1,
                "severity": "Warning",
                "message": f"Multiple iteration loops detected ({nested_for_count}). Ensure bounds prevent Time Limit Exceeded.",
                "suggestedFix": "Look for sub-quadratic O(N log N) or O(N) alternatives."
            })
            
        return {
            "cyclomatic_complexity": min(nested_for_count + 1, 10),
            "nested_loop_depth": min(nested_for_count, 3),
            "has_eval_or_exec": "eval(" in code,
            "heuristic_issues": issues
        }

static_analyzer = StaticAnalyzer()
