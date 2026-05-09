"""
example_checker.py — Validate code examples extracted by DocParser.

For each CodeExample:
  - Python  → compile() for syntax check (no execution)
  - JSON    → json.loads() for parse check
  - Other   → skipped (no check possible without a runtime)
  - Integration examples → flagged but not failed

Results are tagged with one of:
  "ok"                  — syntax / parse valid, non-integration
  "integration"         — valid syntax but requires DCC / external service
  "syntax_error"        — compile() raised SyntaxError
  "json_error"          — json.loads() raised JSONDecodeError
  "skip"                — language not checkable (bash, text, etc.)
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional

from .doc_parser import CodeExample


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class ExampleResult:
    example: CodeExample
    status: str             # "ok" | "integration" | "syntax_error" | "json_error" | "skip"
    error_message: Optional[str] = None
    error_line: Optional[int] = None  # relative to the code block

    @property
    def is_ok(self) -> bool:
        return self.status in ("ok", "integration", "skip")

    @property
    def failed(self) -> bool:
        return self.status in ("syntax_error", "json_error")


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------

class ExampleChecker:
    def __init__(self):
        self.results: List[ExampleResult] = []

    def check_all(self, examples: List[CodeExample]):
        for ex in examples:
            self.results.append(self._check(ex))

    def _check(self, ex: CodeExample) -> ExampleResult:
        if ex.language == "python":
            return self._check_python(ex)
        elif ex.language == "json":
            return self._check_json(ex)
        else:
            return ExampleResult(example=ex, status="skip")

    def _check_python(self, ex: CodeExample) -> ExampleResult:
        if ex.is_integration:
            # Still syntax-check it, but tag as integration regardless
            err, err_line = _try_compile(ex.source, ex.file)
            if err:
                return ExampleResult(
                    example=ex,
                    status="syntax_error",
                    error_message=err,
                    error_line=err_line,
                )
            return ExampleResult(example=ex, status="integration")

        err, err_line = _try_compile(ex.source, ex.file)
        if err:
            return ExampleResult(
                example=ex,
                status="syntax_error",
                error_message=err,
                error_line=err_line,
            )
        return ExampleResult(example=ex, status="ok")

    def _check_json(self, ex: CodeExample) -> ExampleResult:
        try:
            json.loads(ex.source)
        except json.JSONDecodeError as e:
            return ExampleResult(
                example=ex,
                status="json_error",
                error_message=str(e),
                error_line=e.lineno,
            )
        status = "integration" if ex.is_integration else "ok"
        return ExampleResult(example=ex, status=status)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def failed_results(self) -> List[ExampleResult]:
        return [r for r in self.results if r.failed]

    def integration_results(self) -> List[ExampleResult]:
        return [r for r in self.results if r.status == "integration"]

    def summary(self) -> dict:
        counts: dict = {"ok": 0, "integration": 0, "syntax_error": 0, "json_error": 0, "skip": 0}
        for r in self.results:
            counts[r.status] = counts.get(r.status, 0) + 1
        return counts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _try_compile(source: str, filename: str):
    """
    Returns (error_message, error_line) or (None, None) if valid.

    Handles common doc-snippet patterns that are not executable modules:
    - bare `await` / `return` / `yield` → wrap in async def
    - signature-only `def f(args)` without body → append `pass`
    - type-annotation-only lines → wrap in a class
    """
    source = source.rstrip()
    if not source.strip():
        return None, None

    # 1. Try as-is
    err, lineno = _compile_once(source, filename)
    if err is None:
        return None, None

    # 2. Wrap in async function if bare await/return/yield present at module level
    wrapped = _wrap_in_async_def(source)
    if wrapped != source:
        err2, lineno2 = _compile_once(wrapped, filename)
        if err2 is None:
            return None, None

    # 3. Try appending `pass` to incomplete defs/classes/ifs (signature-only snippets)
    patched = _patch_incomplete_blocks(source)
    if patched != source:
        err3, lineno3 = _compile_once(patched, filename)
        if err3 is None:
            return None, None

    # 4. Try wrapping the whole thing in an async def (catches mixed snippets)
    all_lines = source.split("\n")
    indented = "\n".join("    " + l for l in all_lines)
    full_wrap = f"async def _doc_snippet():\n{indented}"
    err4, lineno4 = _compile_once(full_wrap, filename)
    if err4 is None:
        return None, None

    # Return the original error
    return err, lineno


def _compile_once(source: str, filename: str):
    try:
        compile(source, filename, "exec")
        return None, None
    except SyntaxError as e:
        return str(e), e.lineno


def _wrap_in_async_def(source: str) -> str:
    """If any top-level line is a bare await/return/yield, wrap entire source in async def."""
    lines = source.split("\n")
    bare_keywords = ("await ", "return ", "return\n", "yield ", "raise ", "raise\n")
    needs_wrap = False
    for line in lines:
        stripped = line.lstrip()
        if any(stripped.startswith(kw) for kw in bare_keywords):
            # Only if NOT already inside a def (rough check: not indented)
            if not line.startswith(" ") and not line.startswith("\t"):
                needs_wrap = True
                break
    if not needs_wrap:
        return source
    indented = "\n".join("    " + l for l in lines)
    return f"async def _doc_snippet():\n{indented}"


_BLOCK_STARTERS = ("def ", "async def ", "class ", "if ", "elif ", "else:",
                   "else", "for ", "while ", "with ", "try:", "except", "finally")


def _patch_incomplete_blocks(source: str) -> str:
    """
    Append `pass` after definitions without bodies.

    Handles:
    - `def method(self)` — missing colon
    - `def method(self) -> ReturnType` — return annotation, missing colon
    - `def method(self):` — colon present but no body
    - Multi-line signatures where `)` is on its own line
    """
    non_empty = [l for l in source.rstrip().split("\n") if l.strip()]
    if not non_empty:
        return source

    last = non_empty[-1].rstrip()
    stripped = last.lstrip()
    indent = len(last) - len(last.lstrip())
    body_indent = " " * (indent + 4)

    # Case 1: starts with a block keyword and does NOT end with ':'
    if any(stripped.startswith(kw) for kw in _BLOCK_STARTERS) and not stripped.endswith(":"):
        return source.rstrip() + ":\n" + body_indent + "pass"

    # Case 2: ends with ':' but has no following non-empty line in the source
    if stripped.endswith(":"):
        lines = source.rstrip().split("\n")
        # Check if there's any non-empty line after the last ':'
        last_colon_idx = max(
            i for i, l in enumerate(lines) if l.rstrip().endswith(":")
        )
        has_body = any(l.strip() for l in lines[last_colon_idx + 1:])
        if not has_body:
            return source.rstrip() + "\n" + body_indent + "pass"

    # Case 3: multiline signature — last line ends with ')', ']', or a type annotation `-> Type`
    # and an earlier line has a `def`/`class`/`async def`
    _ends_signature = (
        last.rstrip().endswith(")")
        or last.rstrip().endswith("]")
        or bool(__import__("re").search(r"->\s*\w[\w\[\], ]*$", last.rstrip()))
    )
    if _ends_signature:
        src_lines = source.rstrip().split("\n")
        for line in src_lines:
            s = line.lstrip()
            if any(s.startswith(kw) for kw in ("def ", "async def ", "class ")):
                return source.rstrip() + ":\n    pass"

    # Case 4: an INTERIOR def/class line has no body (not the last line).
    # Walk lines and find a def/class that has no following indented code.
    import re as _re
    src_lines = source.split("\n")
    patched_lines = list(src_lines)
    changed = False
    for i, line in enumerate(src_lines):
        stripped = line.rstrip()
        s = stripped.lstrip()
        if not any(s.startswith(kw) for kw in ("def ", "async def ", "class ")):
            continue
        if stripped.endswith(":"):
            # Has colon — check if next non-empty line is indented enough to be a body
            indent = len(stripped) - len(stripped.lstrip())
            next_body = False
            for j in range(i + 1, len(src_lines)):
                if not src_lines[j].strip():
                    continue
                next_indent = len(src_lines[j]) - len(src_lines[j].lstrip())
                next_body = next_indent > indent
                break
            if not next_body:
                # Insert `pass` as body
                body_indent = " " * (indent + 4)
                patched_lines.insert(i + 1, body_indent + "pass")
                changed = True
        # else: no colon — handled by earlier cases
    if changed:
        return "\n".join(patched_lines)

    return source
