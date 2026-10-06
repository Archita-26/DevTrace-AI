"""
Core Orchestrator Module for DevTrace AI.
Connects AST Parsing, Automated Pytest Execution, and Gemini AI Fix Generation
into an autonomous closed-loop repair and verification pipeline.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ast_parser import ASTParser
from core.test_runner import TestRunner
from core.fix_engine import AIFixEngine


class DevTraceOrchestrator:
    """Master controller that executes the closed-loop auto-repair workflow."""

    def __init__(self, target_dir: str = "benchmarks/calculator"):
        self.target_dir = Path(target_dir)
        self.test_runner = TestRunner(str(self.target_dir))
        self.fix_engine = AIFixEngine()

    def run_repair_loop(self, max_retries: int = 2) -> Dict[str, Any]:
        """
        Executes the full closed feedback loop:
        1. Run Tests -> Detect Failure & Traceback
        2. Localize Faulty Function via AST
        3. Prompt Gemini AI for patch
        4. Apply patch to file
        5. Re-run tests to autonomously verify fix
        """
        print(f"\n{'='*55}")
        print(f"🚀 DevTrace AI: Starting Autonomous Repair Pipeline")
        print(f"📁 Target Repository: {self.target_dir}")
        print(f"{'='*55}\n")

        # Step 1: Run Initial Tests
        print("▶ [Step 1/5] Running initial test suite...")
        initial_test = self.test_runner.run()

        if initial_test["success"]:
            print("✅ All tests already pass! No bug found.")
            return {"status": "SUCCESS", "message": "All tests already pass.", "retries": 0}

        print(f"❌ Tests Failed: {initial_test['failed']} failed, {initial_test['passed']} passed.")
        failure = initial_test["failures"][0]
        failing_test_name = failure["test_name"]
        traceback_text = failure["traceback"]
        print(f"   Target Error: {failing_test_name}")

        # Step 2: Localize the culprit file and function
        print("\n▶ [Step 2/5] Localizing bug using AST and Traceback...")
        culprit = self._localize_bug(traceback_text, failing_test_name)
        if not culprit:
            return {"status": "FAILED", "message": "Could not localize faulty function."}

        target_file = culprit["file_path"]
        target_fn = culprit["function_name"]
        print(f"🎯 Culprit Localized: Function '{target_fn}' in [{target_file}]")

        # Keep a backup of the original file content for safety
        original_file_content = Path(target_file).read_text(encoding="utf-8")

        for attempt in range(1, max_retries + 1):
            print(f"\n▶ [Step 3/5] Requesting AI fix from Google Gemini (Attempt {attempt}/{max_retries})...")
            ai_result = self.fix_engine.generate_fix(
                file_path=target_file,
                function_name=target_fn,
                error_traceback=traceback_text,
            )

            if not ai_result["success"]:
                print(f"❌ AI Fix Generation Error: {ai_result['error']}")
                continue

            print("✅ Gemini generated patch successfully.")

            # Step 4: Apply Patch
            print("\n▶ [Step 4/5] Applying patch to target file...")
            patch_applied = self.fix_engine.apply_patch_to_file(
                file_path=target_file,
                original_snippet=ai_result["original_code"],
                fixed_snippet=ai_result["fixed_code"],
            )

            if not patch_applied:
                print("❌ Failed to apply patch snippet to source file.")
                continue

            print("✅ Patch applied successfully to source code.")

            # Step 5: Verification Run
            print("\n▶ [Step 5/5] Re-running tests to verify fix in real-time...")
            verification = self.test_runner.run()

            if verification["success"]:
                print(f"\n{'='*55}")
                print(f"🎉 SUCCESS: Autonomous Fix Verified!")
                print(f"📊 Results: {verification['passed']} passed, {verification['failed']} failed")
                print(f"🔧 Repaired Function: {target_fn}")
                print(f"{'='*55}\n")
                return {
                    "status": "VERIFIED_SUCCESS",
                    "file_path": target_file,
                    "function_name": target_fn,
                    "original_code": ai_result["original_code"],
                    "fixed_code": ai_result["fixed_code"],
                    "passed_tests": verification["passed"],
                    "attempts": attempt,
                }
            else:
                print(f"⚠️ Attempt {attempt} failed verification. Tests still failing.")
                traceback_text = verification["failures"][0]["traceback"]

        # If all retries failed, rollback file to prevent corruption
        print("\n❌ Max retries reached without passing tests. Rolling back file...")
        Path(target_file).write_text(original_file_content, encoding="utf-8")
        return {"status": "FAILED", "message": "Failed to verify fix after retries."}

    def _localize_bug(self, traceback_text: str, test_name: str) -> Optional[Dict[str, str]]:
        """Finds non-test python file and function matching the failure."""
        py_files = [f for f in self.target_dir.glob("*.py") if not f.name.startswith("test_")]
        
        for file_path in py_files:
            parser = ASTParser(str(file_path))
            parsed = parser.parse()
            for fn in parsed["functions"]:
                # Check if function name appears in test name or traceback
                if fn["name"] in test_name or fn["name"] in traceback_text:
                    return {
                        "file_path": str(file_path),
                        "function_name": fn["name"],
                    }

        # Fallback to first non-test file and function
        if py_files:
            parser = ASTParser(str(py_files[0]))
            parsed = parser.parse()
            if parsed["functions"]:
                return {
                    "file_path": str(py_files[0]),
                    "function_name": parsed["functions"][-1]["name"],
                }

        return None


if __name__ == "__main__":
    orchestrator = DevTraceOrchestrator("benchmarks/calculator")
    orchestrator.run_repair_loop()
