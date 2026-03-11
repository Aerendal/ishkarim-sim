"""
ishkarim_sim — moduł z obszaru sim.

Symulacje ABM i fizyczne: Mesa, differentiable physics, LLM w symulacjach społecznych.

Źródła: 23 katalogów z repozytorium Ishkarim.
"""
from __future__ import annotations

__version__ = "0.1.0"
__area__ = "sim"



MODULES: list[str] = [
    'AMBER  - CPU-only scaffold dla ABM',
    'AMBER: kolumnowa architektura dla szybszych symulacji',
    'Ceny dualne jako kompas w symulacjach',
    'Differentiable simulators & hybrids',
    'Hybrid physics-ML notable papers & code',
    'Mikrojądra dyfuzyjne w silnikach symulacyjnych',
    'Mini‑grid i TextWorld: małe, deterministyczne harnessy',
    'New agent‑based simulation updates_04',
    'New economic  and social simulation tools',
    'New hybrid physics–ML papers',
    'New hybrid physics–ML research',
    'New papers SRE Simulation Formal Methods_04',
    'New practical hybrid‑physics research_04',
    'New simulation research & tools',
    'Nowe duże symulacje społeczne z LLM',
    'Nowe przełomy w symulacjach AI_05',
    'Nowe przełomy w symulacjach AI_06',
    'Nowe: MP‑ALOE i narzędzia symulacyjne',
    'Nowości: hybrydowe modele fizyko‑obliczeniowe',
    'Nowości: symulacje 3D i GIS',
    'Symulacje gier jako laboratoria AI',
    'Symulacyjne gospodarki sterowane przez AI',
    'Typy algorytmów biologicznych',
]


_REPO_ROOT: str | None = None


def _find_repo_root() -> str:
    """Auto-discover the Ishkarim repo root by walking up from __file__."""
    from pathlib import Path
    p = Path(__file__).resolve().parent
    for _ in range(10):
        if (p / "CATALOG.md").exists() or (p / "CHANGELOG.md").exists():
            return str(p)
        p = p.parent
    return str(Path(__file__).resolve().parents[5])  # fallback


def load_knowledge_index(root: str | None = None) -> list[dict]:
    """
    Zwraca listę rekordów ze wszystkich katalogów-źródeł obszaru.

    Args:
        root: ścieżka do katalogu głównego repozytorium (opcjonalne)

    Returns:
        Lista słowników z kluczami: name, doc_id, maturity, area
    """
    import re
    from pathlib import Path

    if root is None:
        root = _find_repo_root()

    results = []
    for name in MODULES:
        tags_path = Path(root) / name / "TAGS.md"
        if not tags_path.exists():
            continue
        tags = tags_path.read_text(errors="replace")
        doc_id = ""
        maturity = "draft"
        m = re.search(r"^doc_id:\s*(\S+)", tags, re.M)
        if m:
            doc_id = m.group(1)
        m2 = re.search(r"^maturity:\s*(\S+)", tags, re.M)
        if m2:
            maturity = m2.group(1)
        results.append({"name": name, "doc_id": doc_id, "maturity": maturity, "area": "sim"})
    return results


__all__ = ["MODULES", "load_knowledge_index", "__version__", "__area__"]
