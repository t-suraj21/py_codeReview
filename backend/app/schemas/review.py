from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict

class TestCaseInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    input: str = ""
    expected_output: str = Field("", alias="expectedOutput")

class TestCaseResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    input: str = ""
    expected_output: str = Field("", alias="expectedOutput")
    actual_output: str = Field("", alias="actualOutput")
    passed: bool = False
    execution_time_ms: Optional[float] = Field(None, alias="executionTimeMs")
    explanation: Optional[str] = ""

class ComplexityComparison(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    user_time: str = Field("O(N)", alias="userTime", description="e.g. O(N^2)")
    optimal_time: str = Field("O(N)", alias="optimalTime", description="e.g. O(N)")
    user_space: str = Field("O(1)", alias="userSpace", description="e.g. O(1)")
    optimal_space: str = Field("O(1)", alias="optimalSpace", description="e.g. O(N)")

class DetectedIssue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    line: Optional[int] = None
    severity: str = Field("Info", description="Critical | Warning | Info")
    message: str
    suggested_fix: Optional[str] = Field(None, alias="suggestedFix")

class CodeReviewRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    language: str = "python"
    problem_title: Optional[str] = Field(None, alias="problemTitle")
    problem_description: Optional[str] = Field(None, alias="problemDescription")
    test_cases: List[TestCaseInput] = Field(default=[], alias="testCases")

class CodeReviewResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    summary: str
    rating: int = Field(ge=0, le=100, description="Overall code rating from 0 to 100")
    verdict: str = Field(description="Accepted | Wrong Answer | Needs Improvement | Time Limit Exceeded | Syntax Error")
    algorithmic_approach: str = Field(alias="algorithmicApproach", description="e.g. Two Pointers, Dynamic Programming")
    correct_code: str = Field(alias="correctCode", description="Optimal canonical reference implementation")
    optimal_explanation: str = Field(alias="optimalExplanation")
    complexity_comparison: ComplexityComparison = Field(alias="complexityComparison")
    test_case_results: List[TestCaseResult] = Field(default=[], alias="testCaseResults")
    issues: List[DetectedIssue] = Field(default=[])
    ast_metrics: Optional[Dict[str, Any]] = Field(default=None, alias="astMetrics")
