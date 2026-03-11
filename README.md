# ishkarim-sim

> **Symulacje agentowe (ABM) + differentiable physics — lokalne środowiska AI bez GPU**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![CPU-only](https://img.shields.io/badge/CPU-only-orange)]()

## Problem, który rozwiązujemy

- Mesa/Sugarscape jako deterministyczne środowisko testowe dla agentów AI
- Differentiable physics — gradienty przez symulator (RL, optymalizacja)
- LLM-sterowane symulacje społeczne (agenci z pamięcią i celami)

Pełna lista → [docs/PROBLEMS.md](docs/PROBLEMS.md)

## Szybki start

```bash
# Instalacja
pip install -e projects/ishkarim-sim

# Demo (10 sekund)
python projects/ishkarim-sim/demo.py
```

## Użycie w kodzie

```python
import ishkarim_sim as m

# Wszystkie 23 katalogi wiedzy obszaru 'sim'
docs = m.load_knowledge_index()
print(f"{len(docs)} katalogów | obszar: {m.__area__}")

# Narzędzia pomocnicze
from ishkarim_sim.utils import read_work_md, extract_tags, extract_python_blocks
```

## Dla kogo

- Prototypowanie strategii NPC przed implementacją w silniku gry
- Modelowanie ekonomiczne (rynek, zasoby) dla AI decision-making
- Testowanie hipotez badawczych o zachowaniach zbiorowych bez GPU

## Dokumentacja

| Plik | Zawartość |
|------|-----------|
| [docs/PROBLEMS.md](docs/PROBLEMS.md) | Co rozwiązuje / czego nie / znane problemy |
| [docs/api.md](docs/api.md) | Dokumentacja API |
| [docs/overview.md](docs/overview.md) | Przegląd obszaru |
| [docs/sources.md](docs/sources.md) | Źródłowe katalogi wiedzy |
| [MODULES.md](MODULES.md) | Pełny indeks 23 katalogów |

## Testy i benchmarki

```bash
# Testy jednostkowe
pytest tests/test_sim.py -v

# Testy domenowe (z prawdziwymi danymi)
pytest tests/test_sim_domain.py -v

# Benchmarki wydajnościowe
python benchmarks/bench_sim.py --quick
```

## Struktura projektu

```
ishkarim-sim/
├── demo.py                    ← uruchom mnie
├── pyproject.toml
├── README.md
├── MODULES.md                 ← 23 katalogów-źródeł
├── docs/
│   ├── PROBLEMS.md            ← co rozwiązuje / czego nie
│   ├── api.md                 ← dokumentacja API
│   ├── overview.md
│   └── sources.md
├── src/ishkarim_sim/
│   ├── __init__.py            ← MODULES list + load_knowledge_index()
│   ├── utils.py               ← read_work_md, extract_tags, extract_python_blocks
│   └── snippets/              ← kod z WORK.md (referencyjny)
├── tests/
│   ├── test_sim.py         ← testy jednostkowe
│   └── test_sim_domain.py  ← testy domenowe
└── benchmarks/
    └── bench_sim.py        ← benchmarki wydajnościowe
```

## Ograniczenia

> ⚠️ To projekt **referencyjny** — wzorce i wiedza, nie gotowa biblioteka produkcyjna.
> Przed wdrożeniem produkcyjnym przeczytaj [docs/PROBLEMS.md](docs/PROBLEMS.md).

---

*Część ekosystemu [Ishkarim](../../README.md) — 23 katalogów wiedzy obszaru `sim`*
*Wygenerowano: 2026-03-11 | `scripts/build_projects.py` + `scripts/enrich_projects.py`*
