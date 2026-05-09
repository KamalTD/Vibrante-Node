"""
reporter.py — Aggregate all validation findings and produce reports.

Outputs:
  1. validation.json   — machine-readable summary (for portal badge injection)
  2. VALIDATION_REPORT.md — human-readable Markdown report
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .doc_parser import DocParser, ApiClaim, NodeClaim
from .source_inspector import SourceInspector
from .example_checker import ExampleChecker, ExampleResult


# ---------------------------------------------------------------------------
# Finding types
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    severity: str       # "error" | "warning" | "info"
    category: str       # "api", "node", "example", "signal"
    message: str
    file: str
    line: int = 0

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "file": self.file,
            "line": self.line,
        }


# ---------------------------------------------------------------------------
# Validator — ties everything together
# ---------------------------------------------------------------------------

class Validator:
    def __init__(self, inspector: SourceInspector, parser: DocParser, checker: ExampleChecker):
        self.inspector = inspector
        self.parser = parser
        self.checker = checker
        self.findings: List[Finding] = []

    def run(self):
        self._check_api_claims()
        self._check_node_claims()
        self._check_examples()

    # ------------------------------------------------------------------
    # API / signal claim checks
    # ------------------------------------------------------------------

    # Pydantic BaseModel methods inherited by all model classes (not in class body).
    _PYDANTIC_INHERITED = frozenset({
        "model_dump", "model_validate", "model_fields", "model_config",
        "model_json_schema", "model_copy", "model_rebuild", "model_post_init",
        "parse_obj", "from_orm", "schema", "dict", "json",
    })

    def _check_api_claims(self):
        for claim in self.parser.api_claims:
            cls = self.inspector.classes.get(claim.class_name)
            if cls is None:
                # Unknown class — not one we inspect (could be third-party or untouched internal)
                continue

            known_methods = {m.name for m in cls.methods}
            known_signals = set(cls.signals)
            known_attrs = set(cls.class_attrs) | set(cls.instance_attrs)
            all_known = known_methods | known_signals | known_attrs

            if claim.is_signal:
                # "Without parens" in prose could mean: signal, attribute, or method reference.
                # Only flag if the name is completely absent from the class.
                # Exception: leading-underscore privates are intentionally not inspected.
                if claim.member_name.startswith("_"):
                    continue
                # Skip Pydantic-inherited methods that aren't in the class body
                if claim.member_name in self._PYDANTIC_INHERITED:
                    continue
                if claim.member_name not in all_known:
                    self.findings.append(Finding(
                        severity="error",
                        category="signal",
                        message=(
                            f"`{claim.class_name}.{claim.member_name}` documented but not found "
                            f"in source (checked methods, signals, attributes). "
                            f"Known signals: {sorted(known_signals) or ['(none)']}"
                        ),
                        file=claim.file,
                        line=claim.line,
                    ))
            else:
                if claim.member_name.startswith("_"):
                    continue
                if claim.member_name not in all_known:
                    self.findings.append(Finding(
                        severity="error",
                        category="api",
                        message=(
                            f"`{claim.class_name}.{claim.member_name}()` documented "
                            f"but not found in source."
                        ),
                        file=claim.file,
                        line=claim.line,
                    ))

    # ------------------------------------------------------------------
    # Node claim checks
    # ------------------------------------------------------------------

    # Terms that look like node IDs (snake_case) but are actually port names,
    # signal names, environment variables, or other well-known identifiers.
    _NODE_CLAIM_SKIP = frozenset({
        "exec_in", "exec_out", "exec_fail",
        "node_started", "node_finished", "node_error", "node_output", "node_log",
        "execution_finished",
        "node_id", "node_type", "node_results", "node_info", "node_exists",
        "actions_in", "actions_out",
        "data_type", "widget_type", "use_exec",
        "add_input", "add_output", "add_exec_input", "add_exec_output",
        "log_error", "log_info", "log_warn",
        "get_bridge", "run_code",
        "resolve_prism_core",
        "register_node",
        "async_def", "for_each", "while_loop",
    })

    def _check_node_claims(self):
        for claim in self.parser.node_claims:
            raw = claim.raw_text
            # Skip DCC prefixes that are in plugins/ (we can't inspect those easily)
            if any(raw.startswith(p) for p in ("maya_", "houdini_", "blender_", "prism_", "deadline_", "hou_")):
                continue
            # Skip well-known non-node identifiers
            if raw in self._NODE_CLAIM_SKIP:
                continue
            if not self.inspector.node_exists(raw):
                # Check if it's a display name match
                display_names_lower = {n.lower().replace(" ", "_"): nid
                                       for nid, n in
                                       [(nid, f.display_name) for nid, f in self.inspector.nodes.items()]}
                if raw.lower() not in display_names_lower:
                    self.findings.append(Finding(
                        severity="warning",
                        category="node",
                        message=f"Node `{raw}` mentioned in docs but not found in nodes/ or builtins.",
                        file=claim.file,
                        line=claim.line,
                    ))

    # ------------------------------------------------------------------
    # Code example checks
    # ------------------------------------------------------------------

    def _check_examples(self):
        for result in self.checker.results:
            if result.status == "syntax_error":
                self.findings.append(Finding(
                    severity="error",
                    category="example",
                    message=(
                        f"Python syntax error in code block: {result.error_message}"
                        + (f" (block-relative line {result.error_line})" if result.error_line else "")
                    ),
                    file=result.example.file,
                    line=result.example.line,
                ))
            elif result.status == "json_error":
                self.findings.append(Finding(
                    severity="error",
                    category="example",
                    message=f"JSON parse error in code block: {result.error_message}",
                    file=result.example.file,
                    line=result.example.line,
                ))

    # ------------------------------------------------------------------
    # Summaries and queries
    # ------------------------------------------------------------------

    def errors(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    def warnings(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    def findings_by_file(self) -> dict:
        result: dict = {}
        for f in self.findings:
            result.setdefault(f.file, []).append(f)
        return result

    def per_page_status(self) -> dict:
        """
        Returns {filename: {"ok": bool, "errors": int, "warnings": int}}
        Used by portal badge injection.
        """
        by_file = self.findings_by_file()
        pages = {}
        all_files = set(e.file for e in self.parser.code_examples)
        all_files |= set(c.file for c in self.parser.api_claims)
        all_files |= set(c.file for c in self.parser.node_claims)

        for fname in all_files:
            findings = by_file.get(fname, [])
            errs = sum(1 for f in findings if f.severity == "error")
            warns = sum(1 for f in findings if f.severity == "warning")
            pages[fname] = {"ok": errs == 0, "errors": errs, "warnings": warns}
        return pages


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def write_json_report(validator: Validator, out_path: Path):
    checker_summary = validator.checker.summary()
    data = {
        "total_findings": len(validator.findings),
        "errors": len(validator.errors()),
        "warnings": len(validator.warnings()),
        "example_summary": checker_summary,
        "per_page": validator.per_page_status(),
        "findings": [f.as_dict() for f in validator.findings],
        "known_node_ids": validator.inspector.get_all_node_ids(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_markdown_report(validator: Validator, out_path: Path):
    lines = [
        "# Documentation Validation Report",
        "",
        f"**Errors:** {len(validator.errors())}  ",
        f"**Warnings:** {len(validator.warnings())}  ",
        f"**Total findings:** {len(validator.findings)}",
        "",
    ]

    # Example summary
    cs = validator.checker.summary()
    lines += [
        "## Code Example Summary",
        "",
        f"| Status | Count |",
        f"|--------|-------|",
        f"| OK (non-integration) | {cs.get('ok', 0)} |",
        f"| Integration (DCC/Prism) | {cs.get('integration', 0)} |",
        f"| Python syntax errors | {cs.get('syntax_error', 0)} |",
        f"| JSON parse errors | {cs.get('json_error', 0)} |",
        f"| Skipped (non-checkable) | {cs.get('skip', 0)} |",
        "",
    ]

    # Node coverage
    known = validator.inspector.get_all_node_ids()
    lines += [
        "## Known Nodes in Source",
        "",
        f"Total: **{len(known)}** node IDs",
        "",
        "```",
        "\n".join(known),
        "```",
        "",
    ]

    # Findings by file
    by_file = validator.findings_by_file()
    if by_file:
        lines += ["## Findings by File", ""]
        for fname in sorted(by_file):
            file_findings = by_file[fname]
            lines.append(f"### `{fname}`")
            lines.append("")
            for f in sorted(file_findings, key=lambda x: x.line):
                icon = "🔴" if f.severity == "error" else "🟡"
                lines.append(f"- {icon} **[{f.category}]** line {f.line}: {f.message}")
            lines.append("")
    else:
        lines += ["## Findings", "", "_No findings — all checks passed._", ""]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
