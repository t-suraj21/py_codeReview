import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from app.schemas.review import CodeReviewRequest, CodeReviewResponse
from app.core.ast_parser import ast_preprocessor
from app.core.static_analyzer import static_analyzer
from app.core.test_runner import test_runner
from app.core.gemini import review_code_with_gemini
from app.models.review import ReviewDocument, IN_MEMORY_REVIEWS

reviews_router = APIRouter()

@reviews_router.post("", response_model=CodeReviewResponse)
async def create_code_review(payload: CodeReviewRequest):
    """Executes full multi-stage code review pipeline: AST -> Static -> Sandbox Tests -> Gemini 2.5 Flash."""
    # Step 1: Multi-language AST Preprocessing
    ast_summary = ast_preprocessor.analyze_code(payload.code, payload.language)

    # Step 2: Static Complexity & Security Linting
    static_summary = static_analyzer.analyze(payload.code, payload.language)

    # Step 3: Run Sandboxed Test Cases (if any provided)
    test_results = []
    if payload.test_cases:
        test_results = await test_runner.run_test_cases(
            code=payload.code,
            language=payload.language,
            test_cases=payload.test_cases
        )

    # Step 4: AI Algorithm Synthesis (Gemini 2.5 Flash with fallback)
    review_response = await review_code_with_gemini(
        code=payload.code,
        language=payload.language,
        problem_title=payload.problem_title,
        problem_description=payload.problem_description,
        ast_summary=ast_summary,
        static_summary=static_summary,
        test_results=test_results
    )

    # Step 5: Asynchronous Persistence (MongoDB / Beanie or In-Memory fallback)
    review_record = {
        "id": str(uuid.uuid4()),
        "language": payload.language,
        "problem_title": payload.problem_title,
        "rating": review_response.rating,
        "verdict": review_response.verdict,
        "algorithmic_approach": review_response.algorithmic_approach,
        "summary": review_response.summary,
        "complexity": review_response.complexity_comparison.model_dump(by_alias=True),
        "issues_count": len(review_response.issues),
        "tests_passed": sum(1 for t in review_response.test_case_results if t.passed)
    }

    try:
        doc = ReviewDocument(
            language=payload.language,
            code=payload.code,
            problem_title=payload.problem_title,
            rating=review_response.rating,
            verdict=review_response.verdict,
            algorithmic_approach=review_response.algorithmic_approach,
            complexity=review_response.complexity_comparison,
            issues=review_response.issues,
            test_case_results=review_response.test_case_results,
            ast_metrics=ast_summary
        )
        await doc.insert()
        review_record["id"] = str(doc.id)
    except Exception:
        # If MongoDB is not connected, store in memory
        IN_MEMORY_REVIEWS.append(review_record)

    return review_response

@reviews_router.get("", response_model=List[dict])
async def list_recent_reviews():
    """Returns recent code reviews history."""
    try:
        docs = await ReviewDocument.find_all().sort("-created_at").limit(20).to_list()
        if docs:
            return [
                {
                    "id": str(d.id),
                    "language": d.language,
                    "problem_title": d.problem_title,
                    "rating": d.rating,
                    "verdict": d.verdict,
                    "algorithmic_approach": d.algorithmic_approach,
                    "created_at": d.created_at.isoformat()
                }
                for d in docs
            ]
    except Exception:
        pass
    
    return IN_MEMORY_REVIEWS[-20:]
