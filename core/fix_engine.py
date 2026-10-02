"""
Core AI Fix Engine for DevTrace AI.
Connects to Google Gemini API to analyze error tracebacks and faulty code snippets,
autonomously generating minimal and precise code patches.
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

from dotenv import load_dotenv
from google import genai
from core.ast_parser import ASTParser

# Load API key from local .env file
load_dotenv()


class AIFixEngine:
    """Uses Google Gemini LLM to generate targeted bug fixes."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.8-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or .env file.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def generate_fix(
        self,
        file_path: str,
        function_name: str,
        error_traceback: str,
    ) -> Dict[str, Any]:
        """
        Extracts faulty function via ASTParser, prompts Gemini for a targeted fix,
        and returns the corrected function code.
        """
        parser = ASTParser(file_path)
        parsed = parser.parse()

        # Find target function snippet
        target_fn = None
        for fn in parsed["functions"]:
            if fn["name"] == function_name:
                target_fn = fn
                break

        if not target_fn:
            return {
                "success": False,
                "error": f"Function '{function_name}' not found in {file_path}",
                "original_code": "",
                "fixed_code": "",
            }

        original_code = target_fn["code_snippet"]

        prompt = f"""You are an autonomous software repair agent for DevTrace AI.

A test case failed for the following Python function.
Target File: {file_path}

FAULTY FUNCTION CODE:
```python
{original_code}
```

ERROR TRACEBACK FROM PYTEST:
```text
{error_traceback}
```

TASK:
1. Identify the root cause of the failure based on the traceback.
2. Fix the bug in the function so that the test passes.
3. Return ONLY the complete corrected Python function. 
Do not include any explanation or extra text. Wrap the corrected code in a ```python block.
"""

        models_to_try = [self.model, "gemini-2.0-flash", "gemini-1.5-flash"]
        last_error = ""

        for current_model in models_to_try:
            try:
                # Generate fix using Google GenAI SDK
                response = self.client.models.generate_content(
                    model=current_model,
                    contents=prompt,
                )
                raw_text = response.text.strip()

                # Clean markdown code block if present
                code_match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", raw_text)
                fixed_code = code_match.group(1).strip() if code_match else raw_text

                return {
                    "success": True,
                    "model_used": current_model,
                    "function_name": function_name,
                    "file_path": file_path,
                    "original_code": original_code,
                    "fixed_code": fixed_code,
                }
            except Exception as e:
                last_error = str(e)
                continue

        return {
            "success": False,
            "error": f"AI Generation Error (All fallback models tried): {last_error}",
            "original_code": original_code,
            "fixed_code": "",
        }

    def apply_patch_to_file(self, file_path: str, original_snippet: str, fixed_snippet: str) -> bool:
        """Applies the generated code fix directly to the target file."""
        target = Path(file_path)
        if not target.exists():
            return False

        content = target.read_text(encoding="utf-8")
        if original_snippet not in content:
            return False

        updated_content = content.replace(original_snippet, fixed_snippet, 1)
        target.write_text(updated_content, encoding="utf-8")
        return True


# Quick test runner for this module
if __name__ == "__main__":
    sample_file = "benchmarks/calculator/calculator.py"
    target_function = "calculate_discount"
    sample_traceback = "assert 20.0 == 80.0\nE   AssertionError: calculate_discount returned 20.0 instead of 80.0"

    print(f"\nSending '{target_function}' to Gemini AI for repair...\n")
    engine = AIFixEngine()
    result = engine.generate_fix(sample_file, target_function, sample_traceback)

    if result["success"]:
        print("✅ Gemini AI Fix Generated Successfully!")
        print("\n--- ORIGINAL FAULTY CODE ---")
        print(result["original_code"])
        print("\n--- AI-GENERATED FIXED CODE ---")
        print(result["fixed_code"])
    else:
        print(f"❌ Failed: {result['error']}")
