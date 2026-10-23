import asyncio
import os
import shutil
import tempfile
import time
from typing import Dict, Any, List
from app.config import settings
from app.utils.normalizer import are_outputs_equal, normalize_output
from app.schemas.review import TestCaseResult

class CodeExecutionRunner:
    def __init__(self):
        self.timeout = settings.EXECUTION_TIMEOUT

    async def execute_single(self, code: str, language: str, test_input: str) -> Dict[str, Any]:
        """Executes a snippet with standard input and returns stdout, stderr, execution time."""
        lang = (language or "python").lower().strip()
        start_time = time.perf_counter()

        # Temporary sandbox directory
        temp_dir = tempfile.mkdtemp(prefix="pycode_runner_")

        try:
            if lang in ("python", "py"):
                file_path = os.path.join(temp_dir, "solution.py")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                cmd = ["python3", file_path]
                return await self._run_command(cmd, test_input, start_time)

            elif lang in ("javascript", "js", "node"):
                file_path = os.path.join(temp_dir, "solution.js")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                cmd = ["node", file_path]
                return await self._run_command(cmd, test_input, start_time)

            elif lang in ("c",):
                file_path = os.path.join(temp_dir, "solution.c")
                out_binary = os.path.join(temp_dir, "solution.out")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                # Compile step
                compiler = shutil.which("clang") or shutil.which("gcc")
                if not compiler:
                    return {"stdout": "", "stderr": "No C compiler (clang/gcc) found on server.", "exit_code": 1, "status": "COMPILATION_ERROR", "execution_time_ms": 0}
                
                comp_proc = await asyncio.create_subprocess_exec(
                    compiler, file_path, "-O2", "-o", out_binary,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, comp_err = await comp_proc.communicate()
                if comp_proc.returncode != 0:
                    return {
                        "stdout": "",
                        "stderr": comp_err.decode(errors="replace"),
                        "exit_code": comp_proc.returncode,
                        "status": "COMPILATION_ERROR",
                        "execution_time_ms": (time.perf_counter() - start_time) * 1000
                    }
                return await self._run_command([out_binary], test_input, start_time)

            elif lang in ("cpp", "c++"):
                file_path = os.path.join(temp_dir, "solution.cpp")
                out_binary = os.path.join(temp_dir, "solution.out")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                compiler = shutil.which("clang++") or shutil.which("g++")
                if not compiler:
                    return {"stdout": "", "stderr": "No C++ compiler (clang++/g++) found on server.", "exit_code": 1, "status": "COMPILATION_ERROR", "execution_time_ms": 0}

                comp_proc = await asyncio.create_subprocess_exec(
                    compiler, "-std=c++17", file_path, "-O2", "-o", out_binary,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                _, comp_err = await comp_proc.communicate()
                if comp_proc.returncode != 0:
                    return {
                        "stdout": "",
                        "stderr": comp_err.decode(errors="replace"),
                        "exit_code": comp_proc.returncode,
                        "status": "COMPILATION_ERROR",
                        "execution_time_ms": (time.perf_counter() - start_time) * 1000
                    }
                return await self._run_command([out_binary], test_input, start_time)

            else:
                return {
                    "stdout": "",
                    "stderr": f"Execution for language '{language}' is not supported yet.",
                    "exit_code": 1,
                    "status": "UNSUPPORTED_LANGUAGE",
                    "execution_time_ms": 0
                }

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def _run_command(self, cmd: List[str], test_input: str, start_time: float) -> Dict[str, Any]:
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(input=(test_input or "").encode("utf-8")),
                timeout=self.timeout
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            stdout_str = stdout_bytes.decode(errors="replace").strip()
            stderr_str = stderr_bytes.decode(errors="replace").strip()

            return {
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": process.returncode,
                "status": "COMPLETED" if process.returncode == 0 else "RUNTIME_ERROR",
                "execution_time_ms": round(elapsed_ms, 2)
            }
        except asyncio.TimeoutError:
            try:
                process.kill()
            except Exception:
                pass
            return {
                "stdout": "",
                "stderr": f"Time Limit Exceeded: Execution took longer than {self.timeout}s",
                "exit_code": -1,
                "status": "TIME_LIMIT_EXCEEDED",
                "execution_time_ms": round(self.timeout * 1000, 2)
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": 1,
                "status": "ERROR",
                "execution_time_ms": round((time.perf_counter() - start_time) * 1000, 2)
            }

    async def run_test_cases(self, code: str, language: str, test_cases: List[Any]) -> List[TestCaseResult]:
        """Runs code against multiple test cases and formats TestCaseResult objects."""
        results: List[TestCaseResult] = []

        for tc in test_cases:
            tc_input = tc.get("input", "") if isinstance(tc, dict) else getattr(tc, "input", "")
            tc_expected = tc.get("expected_output") or tc.get("expectedOutput") if isinstance(tc, dict) else getattr(tc, "expected_output", "")

            exec_res = await self.execute_single(code, language, tc_input)
            actual = exec_res["stdout"]
            passed = are_outputs_equal(actual, tc_expected)

            explanation = ""
            if exec_res["status"] == "TIME_LIMIT_EXCEEDED":
                explanation = "Process exceeded time limit (TLE)."
            elif exec_res["status"] == "COMPILATION_ERROR":
                explanation = f"Compilation Error: {exec_res['stderr'][:100]}"
            elif exec_res["status"] == "RUNTIME_ERROR":
                explanation = f"Runtime Error: {exec_res['stderr'][:100]}"
            elif passed:
                explanation = "Output matches expected result."
            else:
                explanation = f"Mismatch: expected '{tc_expected}', got '{actual}'"

            results.append(TestCaseResult(
                input=str(tc_input),
                expected_output=str(tc_expected),
                actual_output=actual if not exec_res["stderr"] else f"{actual}\n[Error: {exec_res['stderr']}]".strip(),
                passed=passed,
                execution_time_ms=exec_res["execution_time_ms"],
                explanation=explanation
            ))

        return results

test_runner = CodeExecutionRunner()
