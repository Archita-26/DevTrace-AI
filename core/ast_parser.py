"""
Core AST Parser Module for DevTrace AI.
Extracts functions, classes, imports, and line boundaries from Python files
deterministically using Python's built-in `ast` module.
"""

import ast
from pathlib import Path
from typing import Dict, List, Any, Optional


class ASTParser:
    """Parses Python source files and extracts structural metadata."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.source_code = ""
        self.tree: Optional[ast.AST] = None

    def read_file(self) -> str:
        """Reads source code from the target file."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.source_code = f.read()
        return self.source_code

    def parse(self) -> Dict[str, Any]:
        """
        Parses source code into an AST and extracts structure:
        - imports
        - functions (with start_line, end_line, args, docstring)
        - classes (with methods and line numbers)
        """
        if not self.source_code:
            self.read_file()

        try:
            self.tree = ast.parse(self.source_code, filename=str(self.file_path))
        except SyntaxError as e:
            return {
                "file": str(self.file_path),
                "error": f"SyntaxError on line {e.lineno}: {e.msg}",
                "functions": [],
                "classes": [],
                "imports": [],
            }

        lines = self.source_code.splitlines()

        functions = []
        classes = []
        imports = []

        for node in ast.iter_child_nodes(self.tree):
            # 1. Extract Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

            # 2. Extract Top-level Functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_info = self._extract_function_info(node, lines)
                functions.append(fn_info)

            # 3. Extract Classes and their Methods
            elif isinstance(node, ast.ClassDef):
                class_methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        class_methods.append(self._extract_function_info(item, lines))

                classes.append({
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "docstring": ast.get_docstring(node) or "",
                    "methods": class_methods,
                })

        return {
            "file": str(self.file_path),
            "total_lines": len(lines),
            "imports": imports,
            "classes": classes,
            "functions": functions,
        }

    def _extract_function_info(self, node: ast.FunctionDef, lines: List[str]) -> Dict[str, Any]:
        """Extracts metadata and snippet for a specific function node."""
        start_line = node.lineno
        end_line = getattr(node, "end_lineno", start_line)

        # Slice exact source code lines of this function
        func_lines = lines[start_line - 1 : end_line]
        code_snippet = "\n".join(func_lines)

        args = [arg.arg for arg in node.args.args]

        return {
            "name": node.name,
            "start_line": start_line,
            "end_line": end_line,
            "arguments": args,
            "docstring": ast.get_docstring(node) or "",
            "code_snippet": code_snippet,
        }


# Quick test runner for this module
if __name__ == "__main__":
    sample_file = "benchmarks/calculator/calculator.py"
    print(f"\nScanning file: {sample_file}...\n")
    parser = ASTParser(sample_file)
    result = parser.parse()

    print(f"Total Lines: {result['total_lines']}")
    print(f"Functions Found ({len(result['functions'])}):")
    for fn in result["functions"]:
        print(f"  - def {fn['name']}({', '.join(fn['arguments'])}) [Lines {fn['start_line']}-{fn['end_line']}]")
    print("\nSuccess! AST Parser is working deterministically.")
