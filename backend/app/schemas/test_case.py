from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

class SingleRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: str
    language: str = "python"
    input: str = ""

class SingleRunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    stdout: str
    stderr: str
    exit_code: int = Field(alias="exitCode")
    status: str
    execution_time_ms: float = Field(alias="executionTimeMs")

class BatchTestRunRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    code: str
    language: str = "python"
    test_cases: List[dict] = Field(default=[], alias="testCases")

class BatchTestRunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    results: List[dict]
    total_passed: int = Field(alias="totalPassed")
    total_cases: int = Field(alias="totalCases")
