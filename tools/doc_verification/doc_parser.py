"""
doc_parser.py — Extract claims made by the documentation from docs_src/ markdown files.

Extracts:
  - Every code block (language, source text, file origin, line number)
  - Every node name / node_id referenced (backtick identifiers, table cells, bold text)
  - Every class.method() reference documented as an API
  - Every signal name documented
  - Headings (for structural checks)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CodeExample:
    language: str          # "python", "json", "bash", "", …
    source: str            # raw code text
    file: str              # docs_src filename
    line: int              # approximate line number in source file
    is_integration: bool = False   # requires DCC / external service


@dataclass
class ApiClaim:
    """A method or attribute mentioned in the docs."""
    class_name: str        # e.g. "NetworkExecutor"
    member_name: str       # e.g. "run" or "node_started"
    is_signal: bool = False
    file: str = ""
    line: int = 0


@dataclass
class NodeClaim:
    """A node_id or display name mentioned in the docs."""
    raw_text: str          # exactly as written
    file: str = ""
    line: int = 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

# Patterns that indicate a code example requires DCC / integration
_INTEGRATION_PATTERNS = re.compile(
    r'\b(hou\b|bridge\.|get_bridge|maya|blender|bpy\.|cmds\.|prism|PrismCore|deadline|mango)',
    re.IGNORECASE
)

# API patterns: ClassName.method_name or ClassName.signal_name
_API_REF_PATTERN = re.compile(
    r'\b([A-Z][A-Za-z]+)\.((?:[a-z_][a-z_0-9]*|[a-z_][a-z_0-9]*\(\)))',
)

# Backtick identifiers that look like node_ids (snake_case or slugs)
_NODE_ID_PATTERN = re.compile(r'`([a-z][a-z0-9_]{2,})`')

# Known DCC / integration node prefixes
_DCC_PREFIXES = ("maya_", "houdini_", "blender_", "prism_", "deadline_", "hou_")


class DocParser:
    def __init__(self, docs_src: Path):
        self.docs_src = docs_src
        self.code_examples: List[CodeExample] = []
        self.api_claims: List[ApiClaim] = []
        self.node_claims: List[NodeClaim] = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def parse_all(self):
        for md_file in sorted(self.docs_src.glob("*.md")):
            self._parse_file(md_file)

    # ------------------------------------------------------------------
    # File-level parsing
    # ------------------------------------------------------------------

    def _parse_file(self, path: Path):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return

        fname = path.name
        lines = text.splitlines()

        self._extract_code_blocks(text, fname)
        self._extract_api_claims(lines, fname)
        self._extract_node_claims(lines, fname)

    # ------------------------------------------------------------------
    # Code block extraction
    # ------------------------------------------------------------------

    def _extract_code_blocks(self, text: str, fname: str):
        """Extract all fenced code blocks (``` ... ```)."""
        pattern = re.compile(r'^```(\w*)\n(.*?)^```', re.MULTILINE | re.DOTALL)
        for m in pattern.finditer(text):
            lang = m.group(1).lower().strip()
            source = m.group(2)
            line = text[:m.start()].count('\n') + 1
            is_integration = bool(_INTEGRATION_PATTERNS.search(source))
            self.code_examples.append(CodeExample(
                language=lang,
                source=source,
                file=fname,
                line=line,
                is_integration=is_integration,
            ))

    # ------------------------------------------------------------------
    # API claim extraction
    # ------------------------------------------------------------------

    def _extract_api_claims(self, lines: List[str], fname: str):
        """Find ClassName.method_name patterns in text (outside code blocks)."""
        in_code_block = False
        for i, line in enumerate(lines, 1):
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for m in _API_REF_PATTERN.finditer(line):
                class_name = m.group(1)
                member_raw = m.group(2).rstrip("()")
                # Skip false positives (common words that happen to have capitals)
                if class_name in ("True", "False", "None", "Ok", "Error"):
                    continue
                is_signal = not m.group(2).endswith(")")
                self.api_claims.append(ApiClaim(
                    class_name=class_name,
                    member_name=member_raw,
                    is_signal=is_signal,
                    file=fname,
                    line=i,
                ))

    # ------------------------------------------------------------------
    # Node claim extraction
    # ------------------------------------------------------------------

    def _extract_node_claims(self, lines: List[str], fname: str):
        """
        Find backtick identifiers that look like node IDs (snake_case, 3+ chars,
        starting with a lowercase letter).  Also find explicit node_id mentions
        in table cells like | `my_node` |.
        """
        in_code_block = False
        for i, line in enumerate(lines, 1):
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            for m in _NODE_ID_PATTERN.finditer(line):
                candidate = m.group(1)
                # Filter: must contain at least one underscore or look like a node_id
                if "_" in candidate or any(candidate.startswith(p) for p in _DCC_PREFIXES):
                    self.node_claims.append(NodeClaim(
                        raw_text=candidate,
                        file=fname,
                        line=i,
                    ))

    # ------------------------------------------------------------------
    # Convenience queries
    # ------------------------------------------------------------------

    def get_python_examples(self) -> List[CodeExample]:
        return [e for e in self.code_examples if e.language == "python"]

    def get_json_examples(self) -> List[CodeExample]:
        return [e for e in self.code_examples if e.language == "json"]

    def get_claims_for_class(self, class_name: str) -> List[ApiClaim]:
        return [c for c in self.api_claims if c.class_name == class_name]

    def unique_node_claims(self) -> List[str]:
        return sorted(set(c.raw_text for c in self.node_claims))

    def unique_api_claims(self) -> List[Tuple[str, str]]:
        return sorted(set((c.class_name, c.member_name) for c in self.api_claims))
