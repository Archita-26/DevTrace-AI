"""
Core Test Runner Module for DevTrace AI.
Executes pytest test suites programmatically, capturing structured pass/fail results,
counts, and detailed error tracebacks for autonomous AI self-healing.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List


class TestRunner:
    """Executes pytest suites and parses the execution feedback."""

    def __init__(self, target_path: str = "benchmarks/calculator"):
        self.target_path = Path(target_path)

    def run(self, timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Executes pytest on the target directory/file and parses output.
        Returns a structured dictionary with success status, counts, and error tracebacks.
        """
        if not self.target_path.exists():
            return {
                "success": False,
                "error": f"Target path does not exist: {self.target_path}",
                "passed": 0,
                "failed": 0,
                "failures": [],
                "raw_output": "",
            }

        # Run pytest using current python executable
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(self.target_path),
            "-v",
            "--tb=short",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            raw_output = result.stdout + "\n" + result.stderr
            return self._parse_pytest_output(result.returncode, raw_output)

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Test execution timed out after {timeout_seconds} seconds.",
                "passed": 0,
                "failed": 1,
                "failures": [{"name": "Timeout", "traceback": "Execution exceeded timeout limit."}],
                "raw_output": "Execution timed out.",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "passed": 0,
                "failed": 1,
                "failures": [{"name": "ExecutionError", "traceback": str(e)}],
                "raw_output": "",
            }

    def _parse_pytest_output(self, returncode: int, output: str) -> Dict[str, Any]:
        """Extracts passed/failed counts and error traces from pytest terminal output."""
        all_passed = returncode == 0

        # Regex for summary counts e.g. "1 failed, 3 passed in 0.05s"
        passed_match = re.search(r"(\d+)\s+passed", output)
        failed_match = re.search(r"(\d+)\s+failed", output)

        passed_count = int(passed_match.group(1)) if passed_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0

        # Extract failed test details
        failures: List[Dict[str, str]] = []
        failure_blocks = re.findall(
            r"_{3,}\s*(test_\w+)\s*_{3,}([\s\S]*?)(?=(?:_{3,}\s*test_\w+|\={3,}|$))",
            output,
        )

        for test_name, trace in failure_blocks:
            failures.append({
                "test_name": test_name.strip(),
                "traceback": trace.strip(),
            })

        return {
            "success": all_passed,
            "exit_code": returncode,
            "passed": passed_count,
            "failed": failed_count,
            "failures": failures,
            "raw_output": output,
        }


# Quick test runner for this module
if __name__ == "__main__":
    target = "benchmarks/calculator"
    print(f"\nRunning tests on: {target}...\n")
    runner = TestRunner(target)
    result = runner.run()

    print(f"Overall Success : {result['success']}")
    print(f"Passed Tests    : {result['passed']}")
    print(f"Failed Tests    : {result['failed']}")

    if result["failures"]:
        print("\nCaptured Failure Details:")
        for f in result["failures"]:
            print(f"  ❌ Failing Test: {f['test_name']}")
            print(f"     Traceback Snippet:\n     {f['traceback'][:200]}...")
    print("\nSuccess! Test Runner captures structured test telemetry.")
