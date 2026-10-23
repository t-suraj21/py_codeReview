import pytest
from app.core.ast_parser import ast_preprocessor

def test_ast_python_valid():
    code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
    result = ast_preprocessor.analyze_code(code, "python")
    assert result["supported"] is True
    assert result["has_syntax_error"] is False
    assert result["function_count"] == 1
    assert result["loop_count"] == 1
    assert "two_sum" in result["function_names"]

def test_ast_python_syntax_error():
    code = "def broken_code(a, b:\n    return a + b"
    result = ast_preprocessor.analyze_code(code, "python")
    assert result["supported"] is True
    assert result["has_syntax_error"] is True
    assert result["error_count"] > 0

def test_ast_javascript_valid():
    code = """
function findMax(arr) {
    let max = -Infinity;
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] > max) max = arr[i];
    }
    return max;
}
"""
    result = ast_preprocessor.analyze_code(code, "javascript")
    assert result["supported"] is True
    assert result["has_syntax_error"] is False
    assert result["function_count"] == 1
    assert result["loop_count"] == 1
