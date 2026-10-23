import pytest
from app.core.test_runner import test_runner

@pytest.mark.asyncio
async def test_python_execution_success():
    code = "import sys\nname = sys.stdin.read().strip()\nprint(f'Hello, {name}!')"
    result = await test_runner.execute_single(code, "python", "World")
    assert result["status"] == "COMPLETED"
    assert result["stdout"] == "Hello, World!"
    assert result["exit_code"] == 0

@pytest.mark.asyncio
async def test_python_execution_tle():
    # Infinite loop should hit execution timeout
    code = "while True: pass"
    result = await test_runner.execute_single(code, "python", "")
    assert result["status"] == "TIME_LIMIT_EXCEEDED"
    assert result["exit_code"] == -1

@pytest.mark.asyncio
async def test_run_test_cases():
    code = """
import sys, json
line = sys.stdin.read().strip()
nums = json.loads(line)
print(sum(nums))
"""
    test_cases = [
        {"input": "[1, 2, 3]", "expected_output": "6"},
        {"input": "[10, -5, 5]", "expected_output": "10"}
    ]
    results = await test_runner.run_test_cases(code, "python", test_cases)
    assert len(results) == 2
    assert results[0].passed is True
    assert results[1].passed is True
