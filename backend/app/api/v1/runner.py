from fastapi import APIRouter, HTTPException
from app.schemas.test_case import (
    SingleRunRequest,
    SingleRunResponse,
    BatchTestRunRequest,
    BatchTestRunResponse
)
from app.core.test_runner import test_runner

runner_router = APIRouter()

@runner_router.post("/run-single", response_model=SingleRunResponse)
async def run_single_code(payload: SingleRunRequest):
    """Executes single code snippet against custom input."""
    result = await test_runner.execute_single(
        code=payload.code,
        language=payload.language,
        test_input=payload.input
    )
    return SingleRunResponse(
        stdout=result.get("stdout", ""),
        stderr=result.get("stderr", ""),
        exitCode=result.get("exit_code", 0),
        status=result.get("status", "UNKNOWN"),
        executionTimeMs=result.get("execution_time_ms", 0.0)
    )

@runner_router.post("/run-tests", response_model=BatchTestRunResponse)
async def run_test_cases(payload: BatchTestRunRequest):
    """Executes code against a collection of test cases."""
    results = await test_runner.run_test_cases(
        code=payload.code,
        language=payload.language,
        test_cases=payload.test_cases
    )
    passed_count = sum(1 for r in results if r.passed)
    return BatchTestRunResponse(
        results=[r.model_dump(by_alias=True) for r in results],
        totalPassed=passed_count,
        totalCases=len(results)
    )
