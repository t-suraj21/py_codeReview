from beanie import Document
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import Field
from app.schemas.review import ComplexityComparison, DetectedIssue, TestCaseResult

class ReviewDocument(Document):
    user_id: Optional[str] = None
    language: str = "python"
    code: str
    problem_title: Optional[str] = None
    rating: int = 0
    verdict: str = "Pending"
    algorithmic_approach: str = "Unknown"
    complexity: ComplexityComparison
    issues: List[DetectedIssue] = []
    test_case_results: List[TestCaseResult] = []
    ast_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reviews"
        indexes = [
            "created_at",
            "language",
            "verdict"
        ]

# In-memory store fallback if MongoDB is offline
IN_MEMORY_REVIEWS: List[Dict[str, Any]] = []
