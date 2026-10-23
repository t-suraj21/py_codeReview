import json
import logging
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types
from app.config import settings
from app.schemas.review import (
    CodeReviewResponse,
    ComplexityComparison,
    DetectedIssue,
    TestCaseResult
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a Principal Software Engineer, Algorithm Architect, and Code Review Specialist.
Analyze the user's code submission with precision:
1. Evaluate algorithmic correctness, efficiency, and edge case coverage.
2. Formulate a canonical, optimal reference solution in the target programming language.
3. Contrast user vs optimal Time & Space complexity in standard Big-O notation.
4. Pinpoint exact line numbers, severity, and actionable remediation for defects.
5. Provide an overall score (0 to 100) and authoritative verdict:
   - "Accepted": Optimal or near-optimal and passes all cases.
   - "Needs Improvement": Correct output but suboptimal complexity or major code smells.
   - "Wrong Answer": Fails edge cases or core problem requirements.
   - "Time Limit Exceeded": Algorithm complexity causes unacceptable runtime.
   - "Syntax Error": Code contains compiler or interpreter syntax failures.
Strictly adhere to the provided JSON response schema.
"""

def generate_local_fallback_review(
    code: str,
    language: str,
    problem_title: Optional[str] = None,
    ast_summary: Optional[Dict[str, Any]] = None,
    static_summary: Optional[Dict[str, Any]] = None,
    test_results: Optional[List[TestCaseResult]] = None
) -> CodeReviewResponse:
    """Intelligent offline fallback using AST & static analysis if Gemini API key is missing."""
    issues: List[DetectedIssue] = []
    
    # Check syntax issues from AST
    has_syntax_err = False
    if ast_summary and ast_summary.get("has_syntax_error"):
        has_syntax_err = True
        for err in ast_summary.get("syntax_errors", []):
            issues.append(DetectedIssue(
                line=err.get("line", 1),
                severity="Critical",
                message="Syntax error detected during AST preprocessing.",
                suggestedFix="Review syntax according to language specifications."
            ))

    # Check static analysis issues
    nested_depth = 0
    if static_summary:
        nested_depth = static_summary.get("nested_loop_depth", 0)
        for h_issue in static_summary.get("heuristic_issues", []):
            issues.append(DetectedIssue(
                line=h_issue.get("line"),
                severity=h_issue.get("severity", "Warning"),
                message=h_issue.get("message", "Potential inefficiency detected."),
                suggestedFix=h_issue.get("suggestedFix")
            ))

    # Calculate test pass rate
    passed_cases = sum(1 for tc in (test_results or []) if tc.passed)
    total_cases = len(test_results or [])
    all_passed = total_cases > 0 and passed_cases == total_cases

    # Verdict & Score determination
    if has_syntax_err:
        verdict = "Syntax Error"
        rating = 25
        summary = "Code contains syntax errors detected by Tree-Sitter AST preprocessing."
    elif total_cases > 0 and not all_passed:
        verdict = "Wrong Answer"
        rating = max(30, int((passed_cases / total_cases) * 70))
        summary = f"Code failed {total_cases - passed_cases} out of {total_cases} test cases."
    elif nested_depth >= 2:
        verdict = "Needs Improvement"
        rating = 72
        summary = f"Solution passes tests but contains nested loops (depth {nested_depth}), which may hit TLE on large scale data."
    else:
        verdict = "Accepted"
        rating = 92
        summary = "Clean implementation passing static AST checks and provided test cases."

    user_time = f"O(N^{nested_depth})" if nested_depth >= 2 else "O(N)"
    optimal_time = "O(N)" if nested_depth >= 2 else "O(1)" if "return" in code and nested_depth == 0 else "O(N)"

    return CodeReviewResponse(
        summary=summary,
        rating=rating,
        verdict=verdict,
        algorithmic_approach="Standard Iterative / Heuristic" if nested_depth > 0 else "Direct Computation",
        correct_code=code,
        optimal_explanation="Review generated via offline AST and Static Analyzer engine. For deep LLM algorithm synthesis, configure a valid GEMINI_API_KEY in .env.",
        complexity_comparison=ComplexityComparison(
            user_time=user_time,
            optimal_time=optimal_time,
            user_space="O(1)",
            optimal_space="O(1)"
        ),
        test_case_results=test_results or [],
        issues=issues,
        ast_metrics=ast_summary
    )

async def review_code_with_gemini(
    code: str,
    language: str,
    problem_title: Optional[str] = None,
    problem_description: Optional[str] = None,
    ast_summary: Optional[Dict[str, Any]] = None,
    static_summary: Optional[Dict[str, Any]] = None,
    test_results: Optional[List[TestCaseResult]] = None
) -> CodeReviewResponse:
    """Reviews code with Gemini 2.5 Flash, falling back to AST/Static engine if key is absent."""
    api_key = settings.GEMINI_API_KEY.strip()
    
    if not api_key or api_key == "your_actual_gemini_api_key":
        logger.info("Using AST/Static fallback review engine (No GEMINI_API_KEY set).")
        return generate_local_fallback_review(
            code=code,
            language=language,
            problem_title=problem_title,
            ast_summary=ast_summary,
            static_summary=static_summary,
            test_results=test_results
        )

    try:
        client = genai.Client(api_key=api_key)
        
        prompt_parts = [
            f"### Target Language: {language}",
            f"### User Code Submission:\n```{language}\n{code}\n```"
        ]

        if problem_title:
            prompt_parts.append(f"### Problem: {problem_title}\n{problem_description or ''}")

        if ast_summary:
            prompt_parts.append(f"### Tree-Sitter AST Preprocessor Metrics:\n{json.dumps(ast_summary, indent=2)}")

        if static_summary:
            prompt_parts.append(f"### Static Lint & Complexity Metrics:\n{json.dumps(static_summary, indent=2)}")

        if test_results:
            tc_data = [tc.model_dump() for tc in test_results]
            prompt_parts.append(f"### Sandbox Execution Results:\n{json.dumps(tc_data, indent=2)}")

        full_prompt = "\n\n".join(prompt_parts)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=CodeReviewResponse,
                temperature=0.2,
            )
        )

        review = CodeReviewResponse.model_validate_json(response.text)
        if test_results and not review.test_case_results:
            review.test_case_results = test_results
        if ast_summary:
            review.ast_metrics = ast_summary

        return review

    except Exception as e:
        logger.error(f"Gemini API invocation failed: {e}. Falling back to AST engine.")
        fallback = generate_local_fallback_review(
            code=code,
            language=language,
            problem_title=problem_title,
            ast_summary=ast_summary,
            static_summary=static_summary,
            test_results=test_results
        )
        fallback.summary += f" (Note: Gemini API fallback triggered: {str(e)[:60]})"
        return fallback
