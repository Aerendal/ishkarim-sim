"""
utils.py — wspólne narzędzia dla ishkarim_sim.
"""
from __future__ import annotations
import re
from pathlib import Path


def read_work_md(dir_path: str | Path) -> str:
    """Wczytuje WORK.md z podanego katalogu."""
    p = Path(dir_path) / "WORK.md"
    if p.exists():
        return p.read_text(errors="replace")
    return ""


def extract_tags(dir_path: str | Path) -> dict:
    """Parsuje TAGS.md i zwraca słownik metadanych."""
    p = Path(dir_path) / "TAGS.md"
    if not p.exists():
        return {}
    content = p.read_text(errors="replace")
    result = {}
    for key in ("doc_id", "title", "maturity", "topic_area", "tags"):
        m = re.search(rf"^{key}:\s*(.+)", content, re.M)
        if m:
            result[key] = m.group(1).strip()
    return result


def extract_python_blocks(work_md: str) -> list[str]:
    """Wyodrębnia bloki ```python z tekstu Markdown."""
    pattern = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)
    return [m.group(1).strip() for m in pattern.finditer(work_md) if len(m.group(1).strip()) > 10]
