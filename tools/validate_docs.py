#!/usr/bin/env python3
"""
validate_docs.py — Documentation accuracy validation pipeline.

Usage:
    python tools/validate_docs.py [--src docs_src] [--out docs] [--fail-on-errors]

Exit codes:
    0 — all checks passed (or only warnings)
    1 — one or more errors found (only when --fail-on-errors is set)
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports work from the repo root
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from tools.doc_verification.doc_parser import DocParser
from tools.doc_verification.source_inspector import SourceInspector
from tools.doc_verification.example_checker import ExampleChecker
from tools.doc_verification.reporter import Validator, write_json_report, write_markdown_report


def main():
    parser = argparse.ArgumentParser(description="Validate Vibrante-Node documentation against source code.")
    parser.add_argument("--src",  default="docs_src",  help="Path to docs_src/ markdown directory")
    parser.add_argument("--out",  default="docs",      help="Output directory (for validation.json)")
    parser.add_argument("--fail-on-errors", action="store_true",
                        help="Exit with code 1 if any errors are found")
    args = parser.parse_args()

    docs_src = Path(args.src)
    if not docs_src.is_absolute():
        docs_src = _ROOT / docs_src

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = _ROOT / out_dir

    if not docs_src.exists():
        print(f"ERROR: docs_src not found: {docs_src}", file=sys.stderr)
        sys.exit(1)

    print(f"[validate_docs] Source: {docs_src}")
    print(f"[validate_docs] Output: {out_dir}")
    print()

    # 1. Parse docs
    print("Parsing documentation...")
    doc_parser = DocParser(docs_src)
    doc_parser.parse_all()
    print(f"  {len(doc_parser.code_examples)} code examples, "
          f"{len(doc_parser.api_claims)} API claims, "
          f"{len(doc_parser.node_claims)} node claims")

    # 2. Inspect source
    print("Inspecting source code...")
    inspector = SourceInspector(_ROOT)
    inspector.inspect_all()
    print(f"  {len(inspector.nodes)} nodes, "
          f"{len(inspector.classes)} classes inspected")
    if inspector.json_nodes_with_errors:
        print(f"  WARNING: {len(inspector.json_nodes_with_errors)} JSON node files failed to parse:")
        for p in inspector.json_nodes_with_errors:
            print(f"    - {p}")

    # 3. Check examples
    print("Checking code examples...")
    checker = ExampleChecker()
    checker.check_all(doc_parser.code_examples)
    cs = checker.summary()
    print(f"  ok={cs.get('ok',0)}  integration={cs.get('integration',0)}  "
          f"syntax_error={cs.get('syntax_error',0)}  json_error={cs.get('json_error',0)}  "
          f"skip={cs.get('skip',0)}")

    # 4. Cross-validate
    print("Cross-validating docs against source...")
    validator = Validator(inspector, doc_parser, checker)
    validator.run()
    errors = validator.errors()
    warnings = validator.warnings()
    print(f"  {len(errors)} errors, {len(warnings)} warnings")

    # 5. Write reports
    json_out = out_dir / "validation.json"
    md_out = _ROOT / "VALIDATION_REPORT.md"
    write_json_report(validator, json_out)
    write_markdown_report(validator, md_out)
    print(f"\nReports written:")
    print(f"  {json_out}")
    print(f"  {md_out}")

    # 6. Print errors
    if errors:
        print(f"\n{'='*60}")
        print(f"ERRORS ({len(errors)}):")
        print('='*60)
        for f in errors:
            print(f"  [{f.file}:{f.line}] {f.category}: {f.message}")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for f in warnings:
            print(f"  [{f.file}:{f.line}] {f.category}: {f.message}")

    print()
    if errors:
        print(f"Validation complete: {len(errors)} error(s), {len(warnings)} warning(s)")
        if args.fail_on_errors:
            sys.exit(1)
    else:
        print(f"Validation complete: all checks passed ({len(warnings)} warning(s))")


if __name__ == "__main__":
    main()
