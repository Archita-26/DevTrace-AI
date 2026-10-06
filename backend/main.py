"""
FastAPI REST API Backend for DevTrace AI.
Exposes endpoints for repository scanning, benchmark discovery,
and automated closed-loop code repair.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ast_parser import ASTParser
from core.orchestrator import DevTraceOrchestrator

app = FastAPI(
    title="DevTrace AI Backend API",
    description="Autonomous Code Understanding, Bug Localization & Verification Engine",
    version="1.0.0",
)

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request & Response Schemas
class ScanRequest(BaseModel):
    file_path: str = Field(..., example="benchmarks/calculator/calculator.py")


class RepairRequest(BaseModel):
    target_dir: str = Field(default="benchmarks/calculator", example="benchmarks/calculator")
    max_retries: int = Field(default=2, ge=1, le=5)


@app.get("/api/health")
def health_check() -> Dict[str, str]:
    """Returns the operational status of the DevTrace AI backend."""
    return {
        "status": "healthy",
        "service": "DevTrace AI Backend",
        "version": "1.0.0",
    }


@app.get("/api/benchmarks")
def list_benchmarks() -> Dict[str, List[Dict[str, Any]]]:
    """Lists available test benchmark suites for demonstration."""
    benchmarks_dir = PROJECT_ROOT / "benchmarks"
    suites = []

    if benchmarks_dir.exists():
        for item in benchmarks_dir.iterdir():
            if item.is_dir() and not item.name.startswith("__"):
                py_files = [f.name for f in item.glob("*.py")]
                suites.append({
                    "name": item.name,
                    "path": f"benchmarks/{item.name}",
                    "files": py_files,
                })

    return {"benchmarks": suites}


@app.post("/api/scan")
def scan_code(request: ScanRequest) -> Dict[str, Any]:
    """Extracts structural AST symbols (functions, classes, imports) from a file."""
    target = PROJECT_ROOT / request.file_path
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Target file not found: {request.file_path}")

    parser = ASTParser(str(target))
    return parser.parse()


@app.post("/api/repair")
def run_repair(request: RepairRequest) -> Dict[str, Any]:
    """Triggers the autonomous closed feedback repair pipeline."""
    target_dir = PROJECT_ROOT / request.target_dir
    if not target_dir.exists():
        raise HTTPException(status_code=404, detail=f"Target directory not found: {request.target_dir}")

    orchestrator = DevTraceOrchestrator(str(target_dir))
    result = orchestrator.run_repair_loop(max_retries=request.max_retries)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
