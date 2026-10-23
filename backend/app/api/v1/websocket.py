import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.ast_parser import ast_preprocessor
from app.core.static_analyzer import static_analyzer

logger = logging.getLogger(__name__)
ws_router = APIRouter()

@ws_router.websocket("/ws/realtime-analysis")
async def realtime_analysis_websocket(websocket: WebSocket):
    """Provides ultra-fast (<10ms) live AST diagnostics and lint markers directly to Monaco."""
    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                payload = json.loads(raw_data)
            except Exception:
                continue

            code = payload.get("code", "")
            language = payload.get("language", "python")

            # Fast AST parsing
            ast_metrics = ast_preprocessor.analyze_code(code, language)
            
            # Fast static check
            static_metrics = static_analyzer.analyze(code, language)

            # Combine markers for Monaco Editor
            markers = []
            for err in ast_metrics.get("syntax_errors", []):
                markers.append({
                    "startLineNumber": err.get("line", 1),
                    "startColumn": err.get("column", 1),
                    "endLineNumber": err.get("line", 1),
                    "endColumn": err.get("column", 1) + 5,
                    "message": err.get("message", "Syntax error"),
                    "severity": 8  # Monaco MarkerSeverity.Error
                })

            for issue in static_metrics.get("heuristic_issues", []):
                if issue.get("line"):
                    markers.append({
                        "startLineNumber": issue["line"],
                        "startColumn": 1,
                        "endLineNumber": issue["line"],
                        "endColumn": 50,
                        "message": issue["message"],
                        "severity": 4 if issue.get("severity") == "Warning" else 8
                    })

            await websocket.send_json({
                "type": "AST_DIAGNOSTICS",
                "hasError": ast_metrics.get("has_syntax_error", False),
                "errorCount": ast_metrics.get("error_count", 0),
                "functionCount": ast_metrics.get("function_count", 0),
                "loopCount": ast_metrics.get("loop_count", 0),
                "complexity": static_metrics.get("cyclomatic_complexity", 1),
                "markers": markers
            })

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
