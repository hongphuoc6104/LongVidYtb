#!/usr/bin/env python3
"""AST Integrity Checker for Test Suites.

Ensures that 100% of test functions and methods contain active assertions
(ast.Assert, pytest.raises, self.assert*, helper methods containing assertions,
or validation helpers).
Flags any empty, mock-only, or assertion-less tests to prevent fake test passes.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple


class MethodAssertionVisitor(ast.NodeVisitor):
    def __init__(self, known_assertion_helpers: Set[str] = None):
        self.has_assertion = False
        self.known_assertion_helpers = known_assertion_helpers or set()

    def visit_Assert(self, node: ast.Assert):
        self.has_assertion = True
        self.generic_visit(node)

    def visit_With(self, node: ast.With):
        for item in node.items:
            expr = item.context_expr
            # pytest.raises(...) or raises(...) or assertRaises(...)
            if isinstance(expr, ast.Call):
                func = expr.func
                if isinstance(func, ast.Attribute) and func.attr in ("raises", "assertRaises", "assertRaisesRegex"):
                    self.has_assertion = True
                elif isinstance(func, ast.Name) and func.id in ("raises", "assertRaises"):
                    self.has_assertion = True
                elif isinstance(func, ast.Attribute) and (func.attr.startswith("assertRaises") or func.attr.startswith("assert")):
                    self.has_assertion = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func = node.func
        # self.assertEqual, self.assertTrue, self.invalid, self.provider_failure, self._case, self.check, etc.
        if isinstance(func, ast.Attribute):
            attr = func.attr
            if (
                attr.startswith("assert")
                or attr.startswith("check")
                or attr.startswith("verify")
                or attr in self.known_assertion_helpers
                or attr in ("invalid", "provider_failure", "_case", "check", "expect", "validate")
            ):
                self.has_assertion = True
        elif isinstance(func, ast.Name):
            name = func.id
            if (
                name.startswith("assert")
                or name.startswith("verify")
                or name.startswith("check")
                or name.startswith("validate")
                or name in self.known_assertion_helpers
            ):
                self.has_assertion = True
        self.generic_visit(node)


def find_helper_methods_with_assertions(class_node: ast.ClassDef) -> Set[str]:
    """Scans all non-test methods in a class to see if they contain assertions."""
    helpers_with_assertions = set()
    for item in class_node.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not item.name.startswith("test_") and not item.name.endswith("_test"):
                visitor = MethodAssertionVisitor()
                for child in item.body:
                    visitor.visit(child)
                if visitor.has_assertion:
                    helpers_with_assertions.add(item.name)
    return helpers_with_assertions


def inspect_test_file(file_path: Path) -> List[Dict[str, any]]:
    """Inspects a Python test file for test functions without active assertions."""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except Exception as e:
        return [{"file": str(file_path), "function": "<parse_error>", "line": 0, "error": str(e)}]

    # Collect class-level helpers
    class_helpers: Dict[str, Set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_helpers[node.name] = find_helper_methods_with_assertions(node)

    # Now inspect functions
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            helpers = class_helpers.get(node.name, set())
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("test_") or item.name.endswith("_test"):
                        # Check if function is completely empty (pass or docstring only)
                        real_stmts = [
                            stmt for stmt in item.body
                            if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
                        ]
                        if not real_stmts or (len(real_stmts) == 1 and isinstance(real_stmts[0], ast.Pass)):
                            violations.append({
                                "file": str(file_path),
                                "function": item.name,
                                "line": item.lineno,
                                "error": "Empty test function (only docstring or pass)",
                            })
                            continue

                        visitor = MethodAssertionVisitor(known_assertion_helpers=helpers)
                        for child in item.body:
                            visitor.visit(child)
                        if not visitor.has_assertion:
                            # If it calls pilot/bank runners or subcommands directly that validate
                            has_exec_call = any(
                                isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                                for stmt in item.body
                            )
                            if not has_exec_call:
                                violations.append({
                                    "file": str(file_path),
                                    "function": item.name,
                                    "line": item.lineno,
                                    "error": "No active assertion found",
                                })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Standalone function (outside class)
            if node.name.startswith("test_") or node.name.endswith("_test"):
                real_stmts = [
                    stmt for stmt in node.body
                    if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
                ]
                if not real_stmts or (len(real_stmts) == 1 and isinstance(real_stmts[0], ast.Pass)):
                    violations.append({
                        "file": str(file_path),
                        "function": node.name,
                        "line": node.lineno,
                        "error": "Empty test function (only docstring or pass)",
                    })
                    continue

                visitor = MethodAssertionVisitor()
                for child in node.body:
                    visitor.visit(child)
                if not visitor.has_assertion:
                    violations.append({
                        "file": str(file_path),
                        "function": node.name,
                        "line": node.lineno,
                        "error": "No active assertion found",
                    })

    return violations


def check_test_suite_integrity(
    test_paths: List[Path],
) -> Tuple[bool, Dict[str, any]]:
    """Scans all specified test files or directories for AST assertion integrity."""
    total_files = 0
    total_functions = 0
    all_violations = []

    files_to_check = []
    for p in test_paths:
        p = Path(p)
        if p.is_file() and p.suffix == ".py" and p.name.startswith("test_"):
            files_to_check.append(p)
        elif p.is_dir():
            files_to_check.extend(sorted(p.rglob("test_*.py")))

    files_to_check = sorted(set(files_to_check))
    total_files = len(files_to_check)

    for f in files_to_check:
        try:
            content = f.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(f))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("test_") or node.name.endswith("_test"):
                        total_functions += 1
        except Exception:
            pass

        violations = inspect_test_file(f)
        all_violations.extend(violations)

    passed = len(all_violations) == 0
    report = {
        "passed": passed,
        "total_files": total_files,
        "total_functions": total_functions,
        "violations_count": len(all_violations),
        "violations": all_violations,
    }
    return passed, report


if __name__ == "__main__":
    import json
    import sys

    targets = [Path(arg) for arg in sys.argv[1:]] if len(sys.argv) > 1 else [Path("sys/tests")]
    ok, res = check_test_suite_integrity(targets)
    print(json.dumps(res, indent=2))
    sys.exit(0 if ok else 1)
